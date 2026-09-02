from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


BASE_FILE = Path(
    "main_option2_all_etfs_v5_16_rolling_asof_monthly_attribution_dynamic_enddate.py"
)

STALE_SOFT_REDUCTION_FRACTION = 0.50
CORR_THRESHOLD = 0.85
MAX_CORRELATED_PAIR_WEIGHT = 0.15

_context: dict[str, Any] = {
    "train_returns": None,
    "score_table": None,
    "eligible_assets": [],
    "date": None,
    "start_window": None,
}

_overlay_rows: list[dict[str, Any]] = []
_overlay_summary_rows: list[dict[str, Any]] = []


def _load_base_module():
    if not BASE_FILE.exists():
        raise FileNotFoundError(
            f"Missing {BASE_FILE}. Create it from the clean production baseline first."
        )

    spec = importlib.util.spec_from_file_location("v516_base_for_v3", BASE_FILE)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {BASE_FILE}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base = _load_base_module()

_original_select_eligible_assets = base.select_eligible_assets
_original_apply_turnover_cap = base.apply_turnover_cap
_original_run_backtest_for_start_window = base.run_backtest_for_start_window


def _normalize(weights: pd.Series) -> pd.Series:
    w = weights.copy().astype(float)
    w = w.replace([np.inf, -np.inf], np.nan).fillna(0.0).clip(lower=0.0)

    total = float(w.sum())

    if total > 0:
        w = w / total

    return w


def _score_value(ticker: str) -> float:
    score_table = _context.get("score_table")

    if (
        score_table is None
        or score_table.empty
        or ticker not in score_table.index
    ):
        return -np.inf

    value = score_table.loc[ticker].get("Score", np.nan)
    return float(value) if pd.notna(value) else -np.inf


def _signal_row(ticker: str) -> pd.Series:
    score_table = _context.get("score_table")

    if (
        score_table is None
        or score_table.empty
        or ticker not in score_table.index
    ):
        return pd.Series(dtype=object)

    return score_table.loc[ticker]


def _is_hard_exit(ticker: str) -> tuple[bool, str]:
    row = _signal_row(ticker)

    above_sma126 = row.get("AboveSMA126", np.nan)
    mom63 = row.get("Mom63", np.nan)
    mom126 = row.get("Mom126", np.nan)

    below_sma126 = (
        False
        if pd.isna(above_sma126)
        else not bool(above_sma126)
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


def _effective_positive_corr(
    train_returns: pd.DataFrame,
    assets: list[str],
) -> pd.DataFrame:
    assets = [ticker for ticker in assets if ticker in train_returns.columns]

    if len(assets) < 2:
        return pd.DataFrame(index=assets, columns=assets, dtype=float)

    fast = (
        train_returns[assets]
        .tail(min(base.FAST_CORR_LOOKBACK_DAYS, len(train_returns)))
        .corr()
    )

    slow = (
        train_returns[assets]
        .tail(min(base.SLOW_CORR_LOOKBACK_DAYS, len(train_returns)))
        .corr()
    )

    result = pd.DataFrame(index=assets, columns=assets, dtype=float)

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
            result.loc[ticker_a, ticker_b] = max(values) if values else np.nan

    return result


def _weaker_member(
    ticker_a: str,
    ticker_b: str,
    weights: pd.Series,
) -> tuple[str, str]:
    eligible = set(_context.get("eligible_assets", []))

    a_eligible = ticker_a in eligible
    b_eligible = ticker_b in eligible

    if a_eligible != b_eligible:
        return (
            (ticker_b, ticker_a)
            if a_eligible
            else (ticker_a, ticker_b)
        )

    score_a = _score_value(ticker_a)
    score_b = _score_value(ticker_b)

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
    candidates: list[str],
    reference_target: pd.Series,
) -> pd.Series:
    if not candidates:
        return pd.Series(dtype=float)

    ref = reference_target.reindex(candidates).fillna(0.0).clip(lower=0.0)

    if float(ref.sum()) > 1e-12:
        return ref / ref.sum()

    scores = pd.Series(
        {ticker: _score_value(ticker) for ticker in candidates},
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
    ticker: str,
    weights: pd.Series,
    corr: pd.DataFrame,
) -> float:
    current = float(weights.get(ticker, 0.0))
    capacity = max(0.0, base.MAX_RISK_ASSET_WEIGHT - current)

    if ticker not in corr.index:
        return capacity

    for peer, peer_weight_raw in weights.items():
        if peer in {ticker, base.CASH_TICKER}:
            continue

        peer_weight = float(peer_weight_raw)

        if (
            peer_weight <= 0
            or peer not in corr.columns
        ):
            continue

        value = corr.loc[ticker, peer]

        if (
            pd.notna(value)
            and float(value) >= CORR_THRESHOLD
        ):
            capacity = min(
                capacity,
                max(
                    0.0,
                    MAX_CORRELATED_PAIR_WEIGHT
                    - current
                    - peer_weight,
                ),
            )

    return max(0.0, capacity)


def _redistribute_amount(
    weights: pd.Series,
    amount: float,
    reference_target: pd.Series,
    corr: pd.DataFrame | None = None,
    exclude: set[str] | None = None,
    enforce_pair_caps: bool = False,
) -> tuple[pd.Series, dict[str, float], float]:
    w = weights.copy().astype(float).fillna(0.0).clip(lower=0.0)
    remaining = max(0.0, float(amount))
    allocations: dict[str, float] = {}
    excluded = set(exclude or set())

    eligible = [
        ticker
        for ticker in _context.get("eligible_assets", [])
        if (
            ticker in w.index
            and ticker != base.CASH_TICKER
            and ticker not in excluded
        )
    ]

    for _ in range(100):
        if remaining <= 1e-12:
            break

        capacities: dict[str, float] = {}

        for ticker in eligible:
            if enforce_pair_caps and corr is not None:
                capacity = _pair_add_capacity(
                    ticker=ticker,
                    weights=w,
                    corr=corr,
                )
            else:
                capacity = max(
                    0.0,
                    base.MAX_RISK_ASSET_WEIGHT
                    - float(w.get(ticker, 0.0)),
                )

            if capacity > 1e-12:
                capacities[ticker] = capacity

        if not capacities:
            break

        active = list(capacities)
        preferences = _preference_weights(
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


def _build_soft_stale_target(
    previous_weights: pd.Series | None,
    base_target: pd.Series,
    all_assets: list[str],
) -> tuple[pd.Series, list[dict[str, Any]]]:
    """
    Build a PRE-turnover target.

    Soft stale rule:
    - Ineligible but not hard-broken => target 50% of previous weight.
    - Hard-broken => target remains zero; actual hard exit is enforced after
      the normal turnover cap.
    - Current eligible target weights are scaled proportionally to make room.
    """
    target = base_target.reindex(all_assets).fillna(0.0).clip(lower=0.0)
    target = _normalize(target)

    if previous_weights is None:
        return target, []

    prev = previous_weights.reindex(all_assets).fillna(0.0).clip(lower=0.0)
    eligible = set(_context.get("eligible_assets", []))
    soft_targets: dict[str, float] = {}
    actions: list[dict[str, Any]] = []

    for ticker, previous_weight_raw in prev.items():
        if ticker == base.CASH_TICKER or ticker in eligible:
            continue

        previous_weight = float(previous_weight_raw)

        if previous_weight <= 1e-12:
            continue

        hard_exit, _ = _is_hard_exit(ticker)

        if hard_exit:
            continue

        stale_target = previous_weight * (
            1.0 - STALE_SOFT_REDUCTION_FRACTION
        )

        if stale_target <= 1e-12:
            continue

        soft_targets[ticker] = stale_target

        actions.append(
            {
                "Ticker": ticker,
                "Overlay": "StalePosition",
                "ActionType": "SoftTargetTrim",
                "WeightBefore": previous_weight,
                "WeightAfter": stale_target,
                "WeightReleased": previous_weight - stale_target,
                "WeightRedistributedToEligible": previous_weight - stale_target,
                "WeightFreedToSGOV": 0.0,
                "Reason": (
                    "Ineligible but long-term trend not hard-broken: "
                    "target a 50% reduction before turnover control"
                ),
            }
        )

    if not soft_targets:
        return target, actions

    cash_target = float(target.get(base.CASH_TICKER, 0.0))
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

    if base.CASH_TICKER in adjusted.index:
        adjusted.loc[base.CASH_TICKER] = cash_target

    for ticker, weight in soft_targets.items():
        adjusted.loc[ticker] = weight

    eligible_assets = [
        ticker
        for ticker in _context.get("eligible_assets", [])
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
            base_eligible = _preference_weights(
                eligible_assets,
                target,
            )

        adjusted.loc[eligible_assets] = (
            base_eligible * available_for_eligible
        )

    return _normalize(adjusted), actions


def _apply_pairwise_corr_to_target(
    target: pd.Series,
    reference_target: pd.Series,
) -> tuple[pd.Series, list[dict[str, Any]]]:
    train_returns = _context.get("train_returns")

    if train_returns is None or train_returns.empty:
        return target, []

    w = target.copy().astype(float).fillna(0.0).clip(lower=0.0)

    corr_assets = [
        ticker
        for ticker, weight in w.items()
        if (
            ticker != base.CASH_TICKER
            and float(weight) > 1e-12
            and ticker in train_returns.columns
        )
    ]

    if len(corr_assets) < 2:
        return _normalize(w), []

    corr = _effective_positive_corr(
        train_returns=train_returns,
        assets=corr_assets,
    )

    actions: list[dict[str, Any]] = []

    for _ in range(100):
        holdings = [
            ticker
            for ticker, weight in w.items()
            if (
                ticker != base.CASH_TICKER
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

                if correlation < CORR_THRESHOLD:
                    continue

                combined = (
                    float(w.get(ticker_a, 0.0))
                    + float(w.get(ticker_b, 0.0))
                )

                if combined <= MAX_CORRELATED_PAIR_WEIGHT + 1e-12:
                    continue

                violations.append(
                    (
                        combined - MAX_CORRELATED_PAIR_WEIGHT,
                        correlation,
                        ticker_a,
                        ticker_b,
                    )
                )

        if not violations:
            break

        violations.sort(reverse=True)
        excess, correlation, ticker_a, ticker_b = violations[0]

        weaker, stronger = _weaker_member(
            ticker_a=ticker_a,
            ticker_b=ticker_b,
            weights=w,
        )

        weaker_before = float(w.get(weaker, 0.0))

        if weaker_before <= 1e-12:
            break

        reduction = min(weaker_before, excess)
        w.loc[weaker] = weaker_before - reduction

        w, recipients, unallocated = _redistribute_amount(
            weights=w,
            amount=reduction,
            reference_target=reference_target,
            corr=corr,
            exclude={ticker_a, ticker_b},
            enforce_pair_caps=True,
        )

        to_cash = 0.0

        if unallocated > 1e-12:
            if base.CASH_TICKER in w.index:
                w.loc[base.CASH_TICKER] = (
                    float(w.get(base.CASH_TICKER, 0.0))
                    + unallocated
                )
                to_cash = unallocated
                unallocated = 0.0

        actions.append(
            {
                "Ticker": weaker,
                "Overlay": "Correlation",
                "ActionType": "PairTargetTrim",
                "WeightBefore": weaker_before,
                "WeightAfter": float(w.get(weaker, 0.0)),
                "WeightReleased": reduction,
                "WeightRedistributedToEligible": (
                    reduction - to_cash
                ),
                "WeightFreedToSGOV": to_cash,
                "RecipientAllocations": _recipient_text(recipients),
                "Reason": (
                    f"Pre-turnover target pair correlation "
                    f"{correlation:.3f} >= {CORR_THRESHOLD:.2f} "
                    f"and pair weight > {MAX_CORRELATED_PAIR_WEIGHT:.0%}"
                ),
                "CorrelationPair": ",".join(
                    sorted([ticker_a, ticker_b])
                ),
                "PairCorrelation": correlation,
                "PairWeightCap": MAX_CORRELATED_PAIR_WEIGHT,
                "StrongerPairMember": stronger,
            }
        )

    return _normalize(w), actions


def _apply_hard_exits_after_turnover(
    previous_weights: pd.Series | None,
    capped_weights: pd.Series,
    all_assets: list[str],
) -> tuple[pd.Series, list[dict[str, Any]], float, float]:
    """
    Only true risk-control exits are allowed to override the 20% turnover cap.
    """
    w = capped_weights.reindex(all_assets).fillna(0.0).clip(lower=0.0)
    eligible = set(_context.get("eligible_assets", []))

    turnover_after_normal_cap = base.calculate_turnover(
        previous_weights=previous_weights,
        current_weights=w,
        all_assets=all_assets,
    )

    actions: list[dict[str, Any]] = []
    released_to_cash = 0.0

    for ticker in list(w.index):
        if ticker == base.CASH_TICKER or ticker in eligible:
            continue

        current_weight = float(w.get(ticker, 0.0))

        if current_weight <= 1e-12:
            continue

        hard_exit, reason = _is_hard_exit(ticker)

        if not hard_exit:
            continue

        w.loc[ticker] = 0.0
        released_to_cash += current_weight

        row = _signal_row(ticker)

        actions.append(
            {
                "Ticker": ticker,
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

    if released_to_cash > 1e-12 and base.CASH_TICKER in w.index:
        w.loc[base.CASH_TICKER] = (
            float(w.get(base.CASH_TICKER, 0.0))
            + released_to_cash
        )

    w = _normalize(w)

    turnover_after_hard_exit = base.calculate_turnover(
        previous_weights=previous_weights,
        current_weights=w,
        all_assets=all_assets,
    )

    return (
        w,
        actions,
        turnover_after_normal_cap,
        turnover_after_hard_exit,
    )


def wrapped_select_eligible_assets(
    train_returns: pd.DataFrame,
    risk_assets: list[str],
):
    eligible, score_table = _original_select_eligible_assets(
        train_returns=train_returns,
        risk_assets=risk_assets,
    )

    _context["train_returns"] = train_returns
    _context["score_table"] = score_table
    _context["eligible_assets"] = eligible
    _context["date"] = (
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

    target_after_stale, stale_soft_actions = _build_soft_stale_target(
        previous_weights=previous_weights,
        base_target=base_target,
        all_assets=all_assets,
    )

    target_after_corr, corr_actions = _apply_pairwise_corr_to_target(
        target=target_after_stale,
        reference_target=base_target,
    )

    capped = _original_apply_turnover_cap(
        previous_weights=previous_weights,
        target_weights=target_after_corr,
        all_assets=all_assets,
        max_turnover=max_turnover,
    )

    (
        final_after_hard_exit,
        hard_exit_actions,
        turnover_after_normal_cap,
        turnover_after_hard_exit,
    ) = _apply_hard_exits_after_turnover(
        previous_weights=previous_weights,
        capped_weights=capped,
        all_assets=all_assets,
    )

    date = _context.get("date")
    start_window = _context.get("start_window")

    all_actions = [
        *stale_soft_actions,
        *corr_actions,
        *hard_exit_actions,
    ]

    for action in all_actions:
        action["Date"] = date
        action["StartWindow"] = start_window
        _overlay_rows.append(action)

    soft_released = sum(
        float(row.get("WeightReleased", 0.0))
        for row in stale_soft_actions
    )
    corr_released = sum(
        float(row.get("WeightReleased", 0.0))
        for row in corr_actions
    )
    hard_released = sum(
        float(row.get("WeightReleased", 0.0))
        for row in hard_exit_actions
    )

    _overlay_summary_rows.append(
        {
            "Date": date,
            "StartWindow": start_window,
            "SoftStaleActions": len(stale_soft_actions),
            "CorrelationActions": len(corr_actions),
            "HardExitActions": len(hard_exit_actions),
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
        }
    )

    return final_after_hard_exit


def wrapped_run_backtest_for_start_window(
    base_returns: pd.DataFrame,
    risk_tickers: list[str],
    start_date: str,
    output_dir: Path,
):
    _context["start_window"] = start_date

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

    summary_df = pd.DataFrame(
        _overlay_summary_rows[summary_start:]
    )
    summary_df.to_csv(
        output_dir / "risk_overlay_summary_by_rebalance.csv",
        index=False,
    )

    return result


# Install V3 hooks into the clean V5.16 baseline module.
base.select_eligible_assets = wrapped_select_eligible_assets
base.apply_turnover_cap = wrapped_apply_turnover_cap
base.run_backtest_for_start_window = wrapped_run_backtest_for_start_window


def main() -> None:
    print("V5.16 Risk Overlay V3")
    print(
        "Soft stale + correlation target changes occur BEFORE the 20% turnover cap."
    )
    print(
        "Only hard stale exits may override the turnover cap and move directly to SGOV."
    )
    print(
        f"Soft stale reduction={STALE_SOFT_REDUCTION_FRACTION:.0%}; "
        f"pair corr threshold={CORR_THRESHOLD:.2f}; "
        f"pair weight cap={MAX_CORRELATED_PAIR_WEIGHT:.0%}"
    )

    args = base.parse_runtime_args()
    base.apply_runtime_overrides(args)
    base.main()


if __name__ == "__main__":
    main()
