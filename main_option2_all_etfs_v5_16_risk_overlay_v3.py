from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd

from strategy_config import (
    PLUGIN_CONFIG,
    RISK_OVERRIDE_PLUGIN_ORDER,
    TARGET_PLUGIN_ORDER,
)
from v516_plugins.pipeline import StrategyPipeline
from v516_plugins.registry import build_plugins
from v516_plugins.types import StrategyContext


BASE_FILE = Path(
    "main_option2_all_etfs_v5_16_rolling_asof_monthly_attribution_dynamic_enddate.py"
)


def _load_base_module():
    if not BASE_FILE.exists():
        raise FileNotFoundError(
            f"Missing clean V5.16 production engine: {BASE_FILE}"
        )

    spec = importlib.util.spec_from_file_location(
        "v516_production_engine",
        BASE_FILE,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {BASE_FILE}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = _load_base_module()

_original_select_eligible_assets = base.select_eligible_assets
_original_apply_turnover_cap = base.apply_turnover_cap
_original_run_backtest_for_start_window = base.run_backtest_for_start_window

_context = StrategyContext(engine=base)
_pipeline = StrategyPipeline(
    target_plugins=build_plugins(
        config=PLUGIN_CONFIG,
        order=TARGET_PLUGIN_ORDER,
    ),
    risk_override_plugins=build_plugins(
        config=PLUGIN_CONFIG,
        order=RISK_OVERRIDE_PLUGIN_ORDER,
    ),
)

_overlay_rows: list[dict] = []
_overlay_summary_rows: list[dict] = []


def _sum_released(actions: list[dict], action_type: str) -> float:
    return sum(
        float(row.get("WeightReleased", 0.0))
        for row in actions
        if row.get("ActionType") == action_type
    )


def _count(actions: list[dict], action_type: str) -> int:
    return sum(
        1 for row in actions if row.get("ActionType") == action_type
    )


def wrapped_select_eligible_assets(
    train_returns: pd.DataFrame,
    risk_assets: list[str],
):
    eligible, score_table = _original_select_eligible_assets(
        train_returns=train_returns,
        risk_assets=risk_assets,
    )

    _context.train_returns = train_returns
    _context.score_table = score_table
    _context.eligible_assets = eligible
    _context.date = (
        pd.Timestamp(train_returns.index[-1])
        if len(train_returns.index)
        else None
    )

    return eligible, score_table


def wrapped_apply_turnover_cap(
    previous_weights: pd.Series | None,
    target_weights: pd.Series,
    all_assets: list[str],
    max_turnover: float,
) -> pd.Series:
    base_target = (
        target_weights
        .reindex(all_assets)
        .fillna(0.0)
        .clip(lower=0.0)
    )

    target_result = _pipeline.apply_target_overlays(
        context=_context,
        previous_weights=previous_weights,
        target_weights=base_target,
        all_assets=all_assets,
    )

    capped = _original_apply_turnover_cap(
        previous_weights=previous_weights,
        target_weights=target_result.weights,
        all_assets=all_assets,
        max_turnover=max_turnover,
    )

    turnover_after_normal_cap = base.calculate_turnover(
        previous_weights=previous_weights,
        current_weights=capped,
        all_assets=all_assets,
    )

    risk_result = _pipeline.apply_risk_overrides(
        context=_context,
        previous_weights=previous_weights,
        weights=capped,
        all_assets=all_assets,
    )

    final_after_risk_overrides = risk_result.weights

    turnover_after_hard_exit = base.calculate_turnover(
        previous_weights=previous_weights,
        current_weights=final_after_risk_overrides,
        all_assets=all_assets,
    )

    actions = [
        *target_result.actions,
        *risk_result.actions,
    ]

    for action in actions:
        action["Date"] = _context.date
        action["StartWindow"] = _context.start_window
        _overlay_rows.append(action)

    soft_released = _sum_released(actions, "SoftTargetTrim")
    corr_released = _sum_released(actions, "PairTargetTrim")
    hard_released = _sum_released(actions, "HardExit")

    _overlay_summary_rows.append(
        {
            "Date": _context.date,
            "StartWindow": _context.start_window,
            "SoftStaleActions": _count(actions, "SoftTargetTrim"),
            "CorrelationActions": _count(actions, "PairTargetTrim"),
            "HardExitActions": _count(actions, "HardExit"),
            "SoftStaleTargetWeightReleased": soft_released,
            "CorrelationTargetWeightReleased": corr_released,
            "HardExitWeightToSGOV": hard_released,
            "TurnoverAfterNormalCap": turnover_after_normal_cap,
            "TurnoverAfterHardExit": turnover_after_hard_exit,
            "ExtraTurnoverFromHardExit": (
                np.nan
                if pd.isna(turnover_after_normal_cap)
                or pd.isna(turnover_after_hard_exit)
                else max(
                    0.0,
                    float(turnover_after_hard_exit)
                    - float(turnover_after_normal_cap),
                )
            ),
            "EnabledTargetPlugins": ",".join(
                plugin.name for plugin in _pipeline.target_plugins
            ),
            "EnabledRiskOverridePlugins": ",".join(
                plugin.name for plugin in _pipeline.risk_override_plugins
            ),
        }
    )

    return final_after_risk_overrides


def wrapped_run_backtest_for_start_window(
    base_returns: pd.DataFrame,
    risk_tickers: list[str],
    start_date: str,
    output_dir: Path,
):
    _context.start_window = start_date

    row_start = len(_overlay_rows)
    summary_start = len(_overlay_summary_rows)

    result = _original_run_backtest_for_start_window(
        base_returns=base_returns,
        risk_tickers=risk_tickers,
        start_date=start_date,
        output_dir=output_dir,
    )

    output_dir = Path(output_dir)

    overlay_df = pd.DataFrame(_overlay_rows[row_start:])
    overlay_df.to_csv(
        output_dir / "risk_overlay_adjustments.csv",
        index=False,
    )
    overlay_df.to_csv(
        output_dir / "strategy_plugin_adjustments.csv",
        index=False,
    )

    summary_df = pd.DataFrame(
        _overlay_summary_rows[summary_start:]
    )
    summary_df.to_csv(
        output_dir / "risk_overlay_summary_by_rebalance.csv",
        index=False,
    )
    summary_df.to_csv(
        output_dir / "strategy_plugin_summary_by_rebalance.csv",
        index=False,
    )

    return result


# Install the plug-in pipeline into the clean V5.16 production engine.
base.select_eligible_assets = wrapped_select_eligible_assets
base.apply_turnover_cap = wrapped_apply_turnover_cap
base.run_backtest_for_start_window = wrapped_run_backtest_for_start_window


def main() -> None:
    print("V5.16 modular strategy pipeline")
    print(
        "Target plug-ins: "
        + (
            ", ".join(plugin.name for plugin in _pipeline.target_plugins)
            or "none"
        )
    )
    print(
        "Risk-override plug-ins: "
        + (
            ", ".join(
                plugin.name for plugin in _pipeline.risk_override_plugins
            )
            or "none"
        )
    )

    args = base.parse_runtime_args()
    base.apply_runtime_overrides(args)
    base.main()


if __name__ == "__main__":
    main()
