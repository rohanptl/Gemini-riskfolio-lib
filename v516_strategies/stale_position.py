from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from v516_plugins.types import StrategyContext, StrategyResult


class StalePositionPlugin:
    name = "stale_position"

    def __init__(self, soft_reduction_fraction: float = 0.50) -> None:
        self.soft_reduction_fraction = float(soft_reduction_fraction)

    @staticmethod
    def _normalize(weights: pd.Series) -> pd.Series:
        w = weights.copy().astype(float)
        w = w.replace([np.inf, -np.inf], np.nan).fillna(0.0).clip(lower=0.0)
        total = float(w.sum())
        return w / total if total > 0 else w

    def _is_hard_exit(
        self,
        context: StrategyContext,
        ticker: str,
    ) -> tuple[bool, str]:
        row = context.signal_row(ticker)

        above_sma126 = row.get("AboveSMA126", np.nan)
        mom63 = row.get("Mom63", np.nan)
        mom126 = row.get("Mom126", np.nan)

        below_sma126 = (
            False if pd.isna(above_sma126) else not bool(above_sma126)
        )
        both_negative = (
            pd.notna(mom63)
            and pd.notna(mom126)
            and float(mom63) < 0
            and float(mom126) < 0
        )

        if below_sma126:
            return True, "Ineligible and below SMA126"

        if both_negative:
            return True, "Ineligible and Mom63/Mom126 both negative"

        return False, ""

    @staticmethod
    def _preference_weights(
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

    def apply_target(
        self,
        context: StrategyContext,
        previous_weights: pd.Series | None,
        weights: pd.Series,
        all_assets: list[str],
        reference_target: pd.Series,
    ) -> StrategyResult:
        """Exact V3 soft-stale behavior, before turnover control."""
        target = (
            weights.reindex(all_assets)
            .fillna(0.0)
            .clip(lower=0.0)
        )
        target = self._normalize(target)

        if previous_weights is None:
            return StrategyResult(weights=target)

        prev = (
            previous_weights.reindex(all_assets)
            .fillna(0.0)
            .clip(lower=0.0)
        )
        eligible = set(context.eligible_assets)
        soft_targets: dict[str, float] = {}
        actions: list[dict[str, Any]] = []

        for ticker, previous_weight_raw in prev.items():
            if ticker == context.engine.CASH_TICKER or ticker in eligible:
                continue

            previous_weight = float(previous_weight_raw)
            if previous_weight <= 1e-12:
                continue

            hard_exit, _ = self._is_hard_exit(context, ticker)
            if hard_exit:
                continue

            stale_target = previous_weight * (
                1.0 - self.soft_reduction_fraction
            )
            if stale_target <= 1e-12:
                continue

            soft_targets[ticker] = stale_target

            actions.append(
                {
                    "Ticker": ticker,
                    "Strategy": self.name,
                    "Overlay": "StalePosition",
                    "ActionType": "SoftTargetTrim",
                    "WeightBefore": previous_weight,
                    "WeightAfter": stale_target,
                    "WeightReleased": previous_weight - stale_target,
                    "WeightRedistributedToEligible": previous_weight - stale_target,
                    "WeightFreedToSGOV": 0.0,
                    "Reason": (
                        "Ineligible but long-term trend not hard-broken: "
                        f"target a {self.soft_reduction_fraction:.0%} reduction "
                        "before turnover control"
                    ),
                }
            )

        if not soft_targets:
            return StrategyResult(
                weights=target,
                actions=actions,
                diagnostics={"soft_actions": len(actions)},
            )

        cash_target = float(target.get(context.engine.CASH_TICKER, 0.0))
        stale_total = float(sum(soft_targets.values()))
        max_stale_total = max(0.0, 1.0 - cash_target)

        if stale_total > max_stale_total and stale_total > 0:
            scale = max_stale_total / stale_total
            soft_targets = {
                ticker: weight * scale
                for ticker, weight in soft_targets.items()
            }
            stale_total = float(sum(soft_targets.values()))

        adjusted = pd.Series(0.0, index=all_assets, dtype=float)

        if context.engine.CASH_TICKER in adjusted.index:
            adjusted.loc[context.engine.CASH_TICKER] = cash_target

        for ticker, weight in soft_targets.items():
            adjusted.loc[ticker] = weight

        eligible_assets = [
            ticker
            for ticker in context.eligible_assets
            if ticker in adjusted.index
        ]

        available_for_eligible = max(
            0.0,
            1.0 - cash_target - stale_total,
        )

        base_eligible = (
            target.reindex(eligible_assets)
            .fillna(0.0)
            .clip(lower=0.0)
        )

        if eligible_assets:
            if float(base_eligible.sum()) > 1e-12:
                base_eligible = base_eligible / base_eligible.sum()
            else:
                base_eligible = self._preference_weights(
                    context,
                    eligible_assets,
                    target,
                )

            adjusted.loc[eligible_assets] = (
                base_eligible * available_for_eligible
            )

        return StrategyResult(
            weights=self._normalize(adjusted),
            actions=actions,
            diagnostics={
                "soft_actions": len(actions),
                "soft_target_weight_released": sum(
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
        """Exact V3 hard exits, after the normal turnover cap."""
        w = (
            weights.reindex(all_assets)
            .fillna(0.0)
            .clip(lower=0.0)
        )
        eligible = set(context.eligible_assets)

        actions: list[dict[str, Any]] = []
        released_to_cash = 0.0

        for ticker in list(w.index):
            if ticker == context.engine.CASH_TICKER or ticker in eligible:
                continue

            current_weight = float(w.get(ticker, 0.0))
            if current_weight <= 1e-12:
                continue

            hard_exit, reason = self._is_hard_exit(context, ticker)
            if not hard_exit:
                continue

            w.loc[ticker] = 0.0
            released_to_cash += current_weight
            row = context.signal_row(ticker)

            actions.append(
                {
                    "Ticker": ticker,
                    "Strategy": self.name,
                    "Overlay": "StalePosition",
                    "ActionType": "HardExit",
                    "WeightBefore": current_weight,
                    "WeightAfter": 0.0,
                    "WeightReleased": current_weight,
                    "WeightRedistributedToEligible": 0.0,
                    "WeightFreedToSGOV": current_weight,
                    "Reason": reason + " -> hard exit after turnover cap",
                    "AboveSMA126": row.get("AboveSMA126", np.nan),
                    "Mom63": row.get("Mom63", np.nan),
                    "Mom126": row.get("Mom126", np.nan),
                }
            )

        if (
            released_to_cash > 1e-12
            and context.engine.CASH_TICKER in w.index
        ):
            w.loc[context.engine.CASH_TICKER] = (
                float(w.get(context.engine.CASH_TICKER, 0.0))
                + released_to_cash
            )

        return StrategyResult(
            weights=self._normalize(w),
            actions=actions,
            diagnostics={
                "hard_exit_actions": len(actions),
                "hard_exit_weight_to_sgov": released_to_cash,
            },
        )
