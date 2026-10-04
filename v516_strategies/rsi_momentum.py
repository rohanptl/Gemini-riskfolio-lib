from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from v516_plugins.types import StrategyContext, StrategyResult


class RSIMomentumPlugin:
    """
    Research-only entry/accumulation timing overlay.

    It does not choose the ETF universe and does not force exits.
    V5.16 decides what to own; this plug-in only controls how quickly
    an increase is deployed.
    """

    name = "rsi_momentum"

    def __init__(
        self,
        rsi_period: int = 14,
        pullback_low: float = 40.0,
        pullback_high: float = 50.0,
        staged_entry_fraction: float = 0.50,
        ema_period: int = 20,
        breakout_lookback: int = 5,
    ) -> None:
        self.rsi_period = int(rsi_period)
        self.pullback_low = float(pullback_low)
        self.pullback_high = float(pullback_high)
        self.staged_entry_fraction = float(staged_entry_fraction)
        self.ema_period = int(ema_period)
        self.breakout_lookback = int(breakout_lookback)

    @staticmethod
    def _normalize(weights: pd.Series) -> pd.Series:
        w = weights.copy().astype(float)
        w = w.replace([np.inf, -np.inf], np.nan).fillna(0.0).clip(lower=0.0)
        total = float(w.sum())
        return w / total if total > 0 else w

    def _rsi(self, prices: pd.Series) -> pd.Series:
        delta = prices.diff()
        gain = delta.clip(lower=0.0)
        loss = -delta.clip(upper=0.0)

        avg_gain = gain.ewm(
            alpha=1.0 / self.rsi_period,
            adjust=False,
            min_periods=self.rsi_period,
        ).mean()
        avg_loss = loss.ewm(
            alpha=1.0 / self.rsi_period,
            adjust=False,
            min_periods=self.rsi_period,
        ).mean()

        rs = avg_gain / avg_loss.replace(0.0, np.nan)
        rsi = 100.0 - (100.0 / (1.0 + rs))

        # A run with no losses is conventionally RSI=100.
        rsi = rsi.where(avg_loss > 0, 100.0)
        return rsi

    def _confirmed_turn(
        self,
        context: StrategyContext,
        ticker: str,
    ) -> tuple[bool, dict[str, Any]]:
        train_returns = context.train_returns

        if (
            train_returns is None
            or train_returns.empty
            or ticker not in train_returns.columns
        ):
            return False, {"reason": "missing_returns"}

        r = train_returns[ticker].dropna()
        if len(r) < 160:
            return False, {"reason": "insufficient_history"}

        prices = (1.0 + r).cumprod()
        daily_rsi = self._rsi(prices)

        latest_rsi = float(daily_rsi.iloc[-1])
        previous_rsi = float(daily_rsi.iloc[-2])

        recent_rsi = daily_rsi.tail(max(5, self.rsi_period // 2))
        pullback_seen = bool(
            ((recent_rsi >= self.pullback_low) & (recent_rsi <= self.pullback_high)).any()
        )
        rsi_turning_up = latest_rsi > previous_rsi

        ema = prices.ewm(
            span=self.ema_period,
            adjust=False,
            min_periods=self.ema_period,
        ).mean()
        above_ema = bool(prices.iloc[-1] > ema.iloc[-1])

        prior_high = prices.shift(1).rolling(
            self.breakout_lookback,
            min_periods=self.breakout_lookback,
        ).max()
        price_breakout = bool(prices.iloc[-1] > prior_high.iloc[-1])

        weekly_prices = prices.resample("W-FRI").last().dropna()
        weekly_sma = weekly_prices.rolling(20, min_periods=20).mean()

        weekly_trend = False
        if len(weekly_prices) >= 21 and pd.notna(weekly_sma.iloc[-2]):
            weekly_trend = bool(
                weekly_prices.iloc[-1] > weekly_sma.iloc[-1]
                and weekly_sma.iloc[-1] > weekly_sma.iloc[-2]
            )

        price_confirmation = above_ema or price_breakout
        confirmed = (
            weekly_trend
            and pullback_seen
            and rsi_turning_up
            and price_confirmation
        )

        return confirmed, {
            "rsi14": latest_rsi,
            "previous_rsi14": previous_rsi,
            "pullback_seen_40_50": pullback_seen,
            "rsi_turning_up": rsi_turning_up,
            "weekly_trend": weekly_trend,
            "above_ema20": above_ema,
            "breakout_prior_5d_high": price_breakout,
            "confirmed": confirmed,
        }

    def apply_target(
        self,
        context: StrategyContext,
        previous_weights: pd.Series | None,
        weights: pd.Series,
        all_assets: list[str],
        reference_target: pd.Series,
    ) -> StrategyResult:
        if previous_weights is None:
            return StrategyResult(weights=weights)

        w = weights.reindex(all_assets).fillna(0.0).clip(lower=0.0)
        prev = previous_weights.reindex(all_assets).fillna(0.0).clip(lower=0.0)
        actions: list[dict[str, Any]] = []
        diagnostics: dict[str, Any] = {}
        delayed_to_cash = 0.0

        for ticker in context.eligible_assets:
            if ticker not in w.index or ticker == context.engine.CASH_TICKER:
                continue

            target_weight = float(w.get(ticker, 0.0))
            previous_weight = float(prev.get(ticker, 0.0))
            desired_increase = max(0.0, target_weight - previous_weight)

            if desired_increase <= 1e-12:
                continue

            confirmed, signal = self._confirmed_turn(context, ticker)
            diagnostics[ticker] = signal

            if confirmed:
                continue

            allowed_increase = desired_increase * self.staged_entry_fraction
            delayed = desired_increase - allowed_increase

            if delayed <= 1e-12:
                continue

            w.loc[ticker] = target_weight - delayed
            delayed_to_cash += delayed

            actions.append(
                {
                    "Ticker": ticker,
                    "Strategy": self.name,
                    "Overlay": "RSIMomentum",
                    "ActionType": "StageIncrease",
                    "WeightBefore": target_weight,
                    "WeightAfter": float(w.loc[ticker]),
                    "WeightReleased": delayed,
                    "WeightRedistributedToEligible": 0.0,
                    "WeightFreedToSGOV": delayed,
                    "Reason": (
                        "V5.16 wants an increase but RSI/price confirmation is "
                        f"not complete; deploy {self.staged_entry_fraction:.0%} "
                        "of the increase and hold the rest temporarily in SGOV"
                    ),
                    **signal,
                }
            )

        if (
            delayed_to_cash > 1e-12
            and context.engine.CASH_TICKER in w.index
        ):
            w.loc[context.engine.CASH_TICKER] = (
                float(w.get(context.engine.CASH_TICKER, 0.0))
                + delayed_to_cash
            )

        return StrategyResult(
            weights=self._normalize(w),
            actions=actions,
            diagnostics={
                "affected_assets": len(actions),
                "delayed_weight_to_sgov": delayed_to_cash,
                "signals": diagnostics,
            },
        )

    def apply_risk_override(
        self,
        context: StrategyContext,
        previous_weights: pd.Series | None,
        weights: pd.Series,
        all_assets: list[str],
    ) -> StrategyResult:
        # RSI never overrides the V5.16/V3 risk exits.
        return StrategyResult(weights=weights)
