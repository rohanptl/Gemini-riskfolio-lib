from __future__ import annotations

from typing import Iterable

import pandas as pd

from .types import StrategyContext, StrategyPlugin, StrategyResult


class StrategyPipeline:
    """Runs plug-ins in deterministic stage order."""

    def __init__(
        self,
        target_plugins: Iterable[StrategyPlugin] = (),
        risk_override_plugins: Iterable[StrategyPlugin] = (),
    ) -> None:
        self.target_plugins = list(target_plugins)
        self.risk_override_plugins = list(risk_override_plugins)

    def apply_target_overlays(
        self,
        context: StrategyContext,
        previous_weights: pd.Series | None,
        target_weights: pd.Series,
        all_assets: list[str],
    ) -> StrategyResult:
        reference_target = target_weights.copy()
        weights = target_weights.copy()
        actions: list[dict] = []
        diagnostics: dict[str, dict] = {}

        for plugin in self.target_plugins:
            result = plugin.apply_target(
                context=context,
                previous_weights=previous_weights,
                weights=weights,
                all_assets=all_assets,
                reference_target=reference_target,
            )
            weights = result.weights
            actions.extend(result.actions)
            diagnostics[plugin.name] = result.diagnostics

        return StrategyResult(
            weights=weights,
            actions=actions,
            diagnostics=diagnostics,
        )

    def apply_risk_overrides(
        self,
        context: StrategyContext,
        previous_weights: pd.Series | None,
        weights: pd.Series,
        all_assets: list[str],
    ) -> StrategyResult:
        current = weights.copy()
        actions: list[dict] = []
        diagnostics: dict[str, dict] = {}

        for plugin in self.risk_override_plugins:
            result = plugin.apply_risk_override(
                context=context,
                previous_weights=previous_weights,
                weights=current,
                all_assets=all_assets,
            )
            current = result.weights
            actions.extend(result.actions)
            diagnostics[plugin.name] = result.diagnostics

        return StrategyResult(
            weights=current,
            actions=actions,
            diagnostics=diagnostics,
        )
