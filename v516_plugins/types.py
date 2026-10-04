from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

import pandas as pd


@dataclass
class StrategyContext:
    engine: Any
    train_returns: pd.DataFrame | None = None
    score_table: pd.DataFrame | None = None
    eligible_assets: list[str] = field(default_factory=list)
    date: pd.Timestamp | None = None
    start_window: str | None = None
    plugin_payoff_matrix: pd.DataFrame | None = None
    regime_probabilities: pd.Series | None = None
    strategy_targets: dict[str, pd.Series] | None = None

    def score_value(self, ticker: str) -> float:
        if (
            self.score_table is None
            or self.score_table.empty
            or ticker not in self.score_table.index
        ):
            return float("-inf")

        value = self.score_table.loc[ticker].get("Score", float("nan"))
        return float(value) if pd.notna(value) else float("-inf")

    def signal_row(self, ticker: str) -> pd.Series:
        if (
            self.score_table is None
            or self.score_table.empty
            or ticker not in self.score_table.index
        ):
            return pd.Series(dtype=object)
        return self.score_table.loc[ticker]


@dataclass
class StrategyResult:
    weights: pd.Series
    actions: list[dict[str, Any]] = field(default_factory=list)
    diagnostics: dict[str, Any] = field(default_factory=dict)


class StrategyPlugin(Protocol):
    name: str

    def apply_target(
        self,
        context: StrategyContext,
        previous_weights: pd.Series | None,
        weights: pd.Series,
        all_assets: list[str],
        reference_target: pd.Series,
    ) -> StrategyResult:
        ...

    def apply_risk_override(
        self,
        context: StrategyContext,
        previous_weights: pd.Series | None,
        weights: pd.Series,
        all_assets: list[str],
    ) -> StrategyResult:
        ...
