from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from v516_plugins.types import StrategyContext, StrategyResult


class CorrelationControlPlugin:
    name = "correlation_control"

    def __init__(
        self,
        corr_threshold: float = 0.85,
        max_pair_weight: float = 0.15,
    ) -> None:
        self.corr_threshold = float(corr_threshold)
        self.max_pair_weight = float(max_pair_weight)

    @staticmethod
    def _normalize(weights: pd.Series) -> pd.Series:
        w = weights.copy().astype(float)
        w = w.replace([np.inf, -np.inf], np.nan).fillna(0.0).clip(lower=0.0)
        total = float(w.sum())
        return w / total if total > 0 else w

    def _effective_positive_corr(
        self,
        context: StrategyContext,
        assets: list[str],
    ) -> pd.DataFrame:
        train_returns = context.train_returns
        if train_returns is None or train_returns.empty:
            return pd.DataFrame(index=assets, columns=assets, dtype=float)

        assets = [
            ticker for ticker in assets if ticker in train_returns.columns
        ]

        if len(assets) < 2:
            return pd.DataFrame(index=assets, columns=assets, dtype=float)

        fast = (
            train_returns[assets]
            .tail(
                min(
                    context.engine.FAST_CORR_LOOKBACK_DAYS,
                    len(train_returns),
                )
            )
            .corr()
        )
        slow = (
            train_returns[assets]
            .tail(
                min(
                    context.engine.SLOW_CORR_LOOKBACK_DAYS,
                    len(train_returns),
                )
            )
            .corr()
        )

        result = pd.DataFrame(
            index=assets,
            columns=assets,
            dtype=float,
        )

        for ticker_a in assets:
            for ticker_b in assets:
                values = [
                    value
                    for value in (
                        fast.loc[ticker_a, ticker_b],
                        slow.loc[ticker_a, ticker_b],
                    )
                    if pd.notna(value)
                ]
                result.loc[ticker_a, ticker_b] = (
                    max(values) if values else np.nan
                )

        return result

    def _weaker_member(
        self,
        context: StrategyContext,
        ticker_a: str,
        ticker_b: str,
        weights: pd.Series,
    ) -> tuple[str, str]:
        eligible = set(context.eligible_assets)
        a_eligible = ticker_a in eligible
        b_eligible = ticker_b in eligible

        if a_eligible != b_eligible:
            return (
                (ticker_b, ticker_a)
                if a_eligible
                else (ticker_a, ticker_b)
            )

        score_a = context.score_value(ticker_a)
        score_b = context.score_value(ticker_b)

        if score_a != score_b:
            return (
                (ticker_a, ticker_b)
                if score_a < score_b
                else (ticker_b, ticker_a)
            )

        weight_a = float(weights.get(ticker_a, 0.0))
        weight_b = float(weights.get(ticker_b, 0.0))

        return (
            (ticker_a, ticker_b)
            if weight_a <= weight_b
            else (ticker_b, ticker_a)
        )

    def _preference_weights(
        self,
        context: StrategyContext,
        candidates: list[str],
        reference_target: pd.Series,
    ) -> pd.Series:
        if not candidates:
            return pd.Series(dtype=float)

        ref = (
            reference_target.reindex(candidates)
            .fillna(0.0)
            .clip(lower=0.0)
        )

        if float(ref.sum()) > 1e-12:
            return ref / ref.sum()

        scores = pd.Series(
            {ticker: context.score_value(ticker) for ticker in candidates},
            dtype=float,
        ).replace([np.inf, -np.inf], np.nan)

        if scores.notna().any():
            finite = scores.dropna()
            shifted = scores - finite.min() + 1e-6
            shifted = shifted.fillna(0.0).clip(lower=0.0)
            if float(shifted.sum()) > 1e-12:
                return shifted / shifted.sum()

        return pd.Series(
            1.0 / len(candidates),
            index=candidates,
            dtype=float,
        )

    def _pair_add_capacity(
        self,
        context: StrategyContext,
        ticker: str,
        weights: pd.Series,
        corr: pd.DataFrame,
    ) -> float:
        current = float(weights.get(ticker, 0.0))
        capacity = max(
            0.0,
            context.engine.MAX_RISK_ASSET_WEIGHT - current,
        )

        if ticker not in corr.index:
            return capacity

        for peer, peer_weight_raw in weights.items():
            if peer in {ticker, context.engine.CASH_TICKER}:
                continue

            peer_weight = float(peer_weight_raw)
            if peer_weight <= 0 or peer not in corr.columns:
                continue

            value = corr.loc[ticker, peer]

            if (
                pd.notna(value)
                and float(value) >= self.corr_threshold
            ):
                capacity = min(
                    capacity,
                    max(
                        0.0,
                        self.max_pair_weight
                        - current
                        - peer_weight,
                    ),
                )

        return max(0.0, capacity)

    def _redistribute_amount(
        self,
        context: StrategyContext,
        weights: pd.Series,
        amount: float,
        reference_target: pd.Series,
        corr: pd.DataFrame,
        exclude: set[str],
    ) -> tuple[pd.Series, dict[str, float], float]:
        w = weights.copy().astype(float).fillna(0.0).clip(lower=0.0)
        remaining = max(0.0, float(amount))
        allocations: dict[str, float] = {}

        eligible = [
            ticker
            for ticker in context.eligible_assets
            if (
                ticker in w.index
                and ticker != context.engine.CASH_TICKER
                and ticker not in exclude
            )
        ]

        for _ in range(100):
            if remaining <= 1e-12:
                break

            capacities: dict[str, float] = {}

            for ticker in eligible:
                capacity = self._pair_add_capacity(
                    context=context,
                    ticker=ticker,
                    weights=w,
                    corr=corr,
                )
                if capacity > 1e-12:
                    capacities[ticker] = capacity

            if not capacities:
                break

            active = list(capacities)
            preferences = self._preference_weights(
                context=context,
                candidates=active,
                reference_target=reference_target,
            )
            starting_remaining = remaining

            for ticker in active:
                preferred = float(preferences.get(ticker, 0.0))
                requested = starting_remaining * preferred
                allocation = min(capacities[ticker], requested)

                if allocation <= 1e-12:
                    continue

                w.loc[ticker] = float(w.get(ticker, 0.0)) + allocation
                allocations[ticker] = allocations.get(ticker, 0.0) + allocation
                remaining -= allocation

            if starting_remaining - remaining <= 1e-12:
                break

        return w, allocations, remaining

    @staticmethod
    def _recipient_text(allocations: dict[str, float]) -> str:
        if not allocations:
            return ""

        return ",".join(
            f"{ticker}:{weight:.6f}"
            for ticker, weight in sorted(
                allocations.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        )

    def apply_target(
        self,
        context: StrategyContext,
        previous_weights: pd.Series | None,
        weights: pd.Series,
        all_assets: list[str],
        reference_target: pd.Series,
    ) -> StrategyResult:
        """Exact V3 pairwise correlation guard, before turnover control."""
        train_returns = context.train_returns

        if train_returns is None or train_returns.empty:
            return StrategyResult(weights=weights)

        w = weights.copy().astype(float).fillna(0.0).clip(lower=0.0)
        corr_assets = [
            ticker
            for ticker, weight in w.items()
            if (
                ticker != context.engine.CASH_TICKER
                and float(weight) > 1e-12
                and ticker in train_returns.columns
            )
        ]

        if len(corr_assets) < 2:
            return StrategyResult(weights=self._normalize(w))

        corr = self._effective_positive_corr(
            context=context,
            assets=corr_assets,
        )
        actions: list[dict[str, Any]] = []

        for _ in range(100):
            holdings = [
                ticker
                for ticker, weight in w.items()
                if (
                    ticker != context.engine.CASH_TICKER
                    and float(weight) > 1e-12
                    and ticker in corr.index
                )
            ]
            violations: list[tuple[float, float, str, str]] = []

            for i, ticker_a in enumerate(holdings):
                for ticker_b in holdings[i + 1:]:
                    value = corr.loc[ticker_a, ticker_b]

                    if pd.isna(value):
                        continue

                    correlation = float(value)
                    if correlation < self.corr_threshold:
                        continue

                    combined = (
                        float(w.get(ticker_a, 0.0))
                        + float(w.get(ticker_b, 0.0))
                    )

                    if combined <= self.max_pair_weight + 1e-12:
                        continue

                    violations.append(
                        (
                            combined - self.max_pair_weight,
                            correlation,
                            ticker_a,
                            ticker_b,
                        )
                    )

            if not violations:
                break

            violations.sort(reverse=True)
            excess, correlation, ticker_a, ticker_b = violations[0]

            weaker, stronger = self._weaker_member(
                context=context,
                ticker_a=ticker_a,
                ticker_b=ticker_b,
                weights=w,
            )
            weaker_before = float(w.get(weaker, 0.0))

            if weaker_before <= 1e-12:
                break

            reduction = min(weaker_before, excess)
            w.loc[weaker] = weaker_before - reduction

            w, recipients, unallocated = self._redistribute_amount(
                context=context,
                weights=w,
                amount=reduction,
                reference_target=reference_target,
                corr=corr,
                exclude={ticker_a, ticker_b},
            )

            to_cash = 0.0
            if (
                unallocated > 1e-12
                and context.engine.CASH_TICKER in w.index
            ):
                w.loc[context.engine.CASH_TICKER] = (
                    float(w.get(context.engine.CASH_TICKER, 0.0))
                    + unallocated
                )
                to_cash = unallocated

            actions.append(
                {
                    "Ticker": weaker,
                    "Strategy": self.name,
                    "Overlay": "Correlation",
                    "ActionType": "PairTargetTrim",
                    "WeightBefore": weaker_before,
                    "WeightAfter": float(w.get(weaker, 0.0)),
                    "WeightReleased": reduction,
                    "WeightRedistributedToEligible": reduction - to_cash,
                    "WeightFreedToSGOV": to_cash,
                    "RecipientAllocations": self._recipient_text(recipients),
                    "Reason": (
                        "Pre-turnover target pair correlation "
                        f"{correlation:.3f} >= {self.corr_threshold:.2f} "
                        f"and pair weight > {self.max_pair_weight:.0%}"
                    ),
                    "CorrelationPair": ",".join(
                        sorted([ticker_a, ticker_b])
                    ),
                    "PairCorrelation": correlation,
                    "PairWeightCap": self.max_pair_weight,
                    "StrongerPairMember": stronger,
                }
            )

        return StrategyResult(
            weights=self._normalize(w),
            actions=actions,
            diagnostics={
                "correlation_actions": len(actions),
                "correlation_target_weight_released": sum(
                    float(row.get("WeightReleased", 0.0))
                    for row in actions
                ),
            },
        )

    def apply_risk_override(
        self,
        context: StrategyContext,
        previous_weights: pd.Series | None,
        weights: pd.Series,
        all_assets: list[str],
    ) -> StrategyResult:
        return StrategyResult(weights=weights)
