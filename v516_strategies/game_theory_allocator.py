from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from v516_plugins.types import StrategyContext, StrategyResult


class GameTheoryAllocatorPlugin:
    """
    Research-only meta allocator.

    Treats plug-in strategies as the player's available actions and market
    regimes as uncertain states/opposing conditions. It solves for a mixed
    strategy that balances Bayesian expected payoff with maximin robustness.

    Production remains unchanged unless:
    1. this plug-in is enabled, and
    2. context.plugin_payoff_matrix and context.strategy_targets are supplied.
    """

    name = "game_theory_allocator"

    def __init__(
        self,
        robustness_weight: float = 0.35,
        minimum_strategy_weight: float = 0.0,
    ) -> None:
        self.robustness_weight = float(
            np.clip(robustness_weight, 0.0, 1.0)
        )
        self.minimum_strategy_weight = float(
            max(0.0, minimum_strategy_weight)
        )

    @staticmethod
    def _normalize(weights: pd.Series) -> pd.Series:
        w = weights.copy().astype(float)
        w = w.replace([np.inf, -np.inf], np.nan).fillna(0.0).clip(lower=0.0)
        total = float(w.sum())
        return w / total if total > 0 else w

    def solve_mixed_strategy(
        self,
        payoff_matrix: pd.DataFrame,
        regime_probabilities: pd.Series | None = None,
    ) -> pd.Series:
        """
        Solve:
            max_x (1-lambda) * E[payoff] + lambda * worst_regime_payoff

        subject to:
            sum(x) = 1
            x_i >= minimum_strategy_weight
            worst_regime_payoff <= payoff in every regime

        The result is a game-theoretic mixed strategy across strategy modules.
        """
        from scipy.optimize import linprog

        payoffs = (
            payoff_matrix.astype(float)
            .replace([np.inf, -np.inf], np.nan)
            .dropna(axis=0, how="any")
            .dropna(axis=1, how="any")
        )

        if payoffs.empty:
            raise ValueError("Payoff matrix has no complete strategy/regime data.")

        n_strategies, n_regimes = payoffs.shape

        min_weight = self.minimum_strategy_weight
        if min_weight * n_strategies > 1.0 + 1e-12:
            raise ValueError(
                "minimum_strategy_weight is infeasible for the number of strategies."
            )

        if regime_probabilities is None:
            probs = pd.Series(
                1.0 / n_regimes,
                index=payoffs.columns,
                dtype=float,
            )
        else:
            probs = (
                regime_probabilities.reindex(payoffs.columns)
                .fillna(0.0)
                .clip(lower=0.0)
                .astype(float)
            )
            if float(probs.sum()) <= 0:
                probs[:] = 1.0 / n_regimes
            else:
                probs = probs / probs.sum()

        expected_by_strategy = payoffs.dot(probs).to_numpy()

        # Variables are [x_1 ... x_n, v], where v is worst-regime payoff.
        c = np.zeros(n_strategies + 1, dtype=float)
        c[:n_strategies] = (
            -(1.0 - self.robustness_weight) * expected_by_strategy
        )
        c[-1] = -self.robustness_weight

        # For each regime: v <= sum_i x_i payoff(i, regime)
        # => -payoff[:, regime]' x + v <= 0
        a_ub = np.zeros((n_regimes, n_strategies + 1), dtype=float)
        b_ub = np.zeros(n_regimes, dtype=float)

        for j, regime in enumerate(payoffs.columns):
            a_ub[j, :n_strategies] = -payoffs[regime].to_numpy()
            a_ub[j, -1] = 1.0

        a_eq = np.zeros((1, n_strategies + 1), dtype=float)
        a_eq[0, :n_strategies] = 1.0
        b_eq = np.array([1.0])

        bounds = [
            (min_weight, 1.0)
            for _ in range(n_strategies)
        ] + [(None, None)]

        result = linprog(
            c=c,
            A_ub=a_ub,
            b_ub=b_ub,
            A_eq=a_eq,
            b_eq=b_eq,
            bounds=bounds,
            method="highs",
        )

        if not result.success:
            raise RuntimeError(
                f"Game-theory allocation failed: {result.message}"
            )

        mixture = pd.Series(
            result.x[:n_strategies],
            index=payoffs.index,
            dtype=float,
        )
        mixture = mixture.clip(lower=0.0)
        mixture = mixture / mixture.sum()

        return mixture

    def apply_target(
        self,
        context: StrategyContext,
        previous_weights: pd.Series | None,
        weights: pd.Series,
        all_assets: list[str],
        reference_target: pd.Series,
    ) -> StrategyResult:
        if (
            context.plugin_payoff_matrix is None
            or context.strategy_targets is None
            or not context.strategy_targets
        ):
            return StrategyResult(
                weights=weights,
                diagnostics={
                    "status": "inactive_no_payoff_matrix_or_strategy_targets"
                },
            )

        available = [
            strategy_name
            for strategy_name in context.plugin_payoff_matrix.index
            if strategy_name in context.strategy_targets
        ]

        if not available:
            return StrategyResult(
                weights=weights,
                diagnostics={"status": "inactive_no_matching_strategies"},
            )

        payoff_matrix = context.plugin_payoff_matrix.loc[available]
        mixture = self.solve_mixed_strategy(
            payoff_matrix=payoff_matrix,
            regime_probabilities=context.regime_probabilities,
        )

        blended = pd.Series(0.0, index=all_assets, dtype=float)

        for strategy_name, strategy_weight in mixture.items():
            target = (
                context.strategy_targets[strategy_name]
                .reindex(all_assets)
                .fillna(0.0)
            )
            blended += float(strategy_weight) * target

        blended = self._normalize(blended)

        action = {
            "Ticker": "__PORTFOLIO__",
            "Strategy": self.name,
            "Overlay": "GameTheory",
            "ActionType": "MixedStrategyBlend",
            "WeightBefore": np.nan,
            "WeightAfter": np.nan,
            "WeightReleased": 0.0,
            "WeightRedistributedToEligible": 0.0,
            "WeightFreedToSGOV": 0.0,
            "Reason": (
                "Blend strategy targets using Bayesian expected payoff plus "
                "maximin regime robustness"
            ),
            "StrategyMixture": ",".join(
                f"{name}:{weight:.6f}"
                for name, weight in mixture.items()
            ),
        }

        return StrategyResult(
            weights=blended,
            actions=[action],
            diagnostics={
                "status": "applied",
                "strategy_mixture": mixture.to_dict(),
                "robustness_weight": self.robustness_weight,
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
