from __future__ import annotations

from pathlib import Path
import importlib.util
import shutil

PRODUCTION_FILE = Path(
    "main_option2_all_etfs_v5_16_rolling_asof_monthly_attribution_dynamic_enddate.py"
)
WORKFLOW_FILE = Path(".github/workflows/v516_rolling_asof_allocation_workflow.yml")
V1_PATCHER_FILE = Path("apply_v516_risk_overlays.py")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Patch anchor not found: {label}")
    return text.replace(old, new, 1)


def ensure_v1_overlay(text: str) -> str:
    if "USE_STALE_POSITION_EXIT_OVERLAY = True" in text:
        return text

    if not V1_PATCHER_FILE.exists():
        raise RuntimeError(
            "The current strategy does not contain the V1 overlay and "
            "apply_v516_risk_overlays.py is not present. "
            "Run the V1 patcher first, then rerun this V2 upgrade."
        )

    spec = importlib.util.spec_from_file_location("v1_overlay_patcher", V1_PATCHER_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load apply_v516_risk_overlays.py")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    patched = module.patch_strategy(text)
    if "USE_STALE_POSITION_EXIT_OVERLAY = True" not in patched:
        raise RuntimeError("V1 patcher did not add the expected overlay markers.")

    return patched


NEW_HELPER_BLOCK = r'''

def _normalize_overlay_weights(weights: pd.Series) -> pd.Series:
    w = weights.copy().astype(float)
    w = w.replace([np.inf, -np.inf], np.nan).fillna(0.0).clip(lower=0.0)
    total = float(w.sum())
    if total > 0:
        w = w / total
    return w


def _move_amount_to_cash(weights: pd.Series, amount: float) -> pd.Series:
    """Move only the specified amount into SGOV."""
    w = weights.copy().astype(float).fillna(0.0).clip(lower=0.0)
    if amount > 1e-12 and CASH_TICKER in w.index:
        w.loc[CASH_TICKER] = float(w.get(CASH_TICKER, 0.0)) + float(amount)
    return _normalize_overlay_weights(w)


def _score_value(score_table: pd.DataFrame, ticker: str) -> float:
    if score_table is None or score_table.empty or ticker not in score_table.index:
        return -np.inf
    value = score_table.loc[ticker].get("Score", np.nan)
    return float(value) if pd.notna(value) else -np.inf


def _eligible_preference_weights(
    candidates: list[str],
    target_weights: pd.Series,
    score_table: pd.DataFrame,
) -> pd.Series:
    """Prefer current model target weights; fall back to score, then equal weight."""
    if not candidates:
        return pd.Series(dtype=float)

    target = target_weights.reindex(candidates).fillna(0.0).clip(lower=0.0)
    if float(target.sum()) > 1e-12:
        return target / target.sum()

    scores = pd.Series(
        {ticker: _score_value(score_table, ticker) for ticker in candidates},
        dtype=float,
    ).replace([np.inf, -np.inf], np.nan)

    if scores.notna().any():
        finite = scores.dropna()
        shifted = (scores - finite.min() + 1e-6).fillna(0.0).clip(lower=0.0)
        if float(shifted.sum()) > 1e-12:
            return shifted / shifted.sum()

    return pd.Series(1.0 / len(candidates), index=candidates, dtype=float)


def _candidate_pair_capacity(
    ticker: str,
    weights: pd.Series,
    corr: pd.DataFrame | None,
) -> float:
    """Capacity while respecting individual and correlated-pair caps."""
    current = float(weights.get(ticker, 0.0))
    capacity = max(0.0, MAX_RISK_ASSET_WEIGHT - current)

    if corr is None or corr.empty or ticker not in corr.index:
        return capacity

    for peer, raw_weight in weights.items():
        if peer in {ticker, CASH_TICKER}:
            continue
        peer_weight = float(raw_weight)
        if peer_weight <= 0 or peer not in corr.columns:
            continue
        value = corr.loc[ticker, peer]
        if pd.notna(value) and float(value) >= CORR_DECONCENTRATION_THRESHOLD:
            pair_capacity = MAX_CORRELATED_PAIR_WEIGHT - current - peer_weight
            capacity = min(capacity, max(0.0, pair_capacity))

    return max(0.0, capacity)


def _redistribute_to_eligible(
    weights: pd.Series,
    amount: float,
    eligible_assets: list[str],
    target_weights: pd.Series,
    score_table: pd.DataFrame,
    exclude_assets: set[str] | None = None,
    corr: pd.DataFrame | None = None,
    enforce_pair_caps: bool = False,
) -> tuple[pd.Series, float, float, dict[str, float]]:
    """Redistribute released weight into current eligible ETFs."""
    w = weights.copy().astype(float).fillna(0.0).clip(lower=0.0)
    remaining = max(0.0, float(amount))
    recipients: dict[str, float] = {}
    excluded = set(exclude_assets or set())

    eligible = [
        ticker for ticker in eligible_assets
        if ticker in w.index and ticker != CASH_TICKER and ticker not in excluded
    ]

    for _ in range(100):
        if remaining <= 1e-12:
            break

        capacities: dict[str, float] = {}
        for ticker in eligible:
            if enforce_pair_caps:
                capacity = _candidate_pair_capacity(ticker, w, corr)
            else:
                capacity = max(
                    0.0,
                    MAX_RISK_ASSET_WEIGHT - float(w.get(ticker, 0.0)),
                )
            if capacity > 1e-12:
                capacities[ticker] = capacity

        if not capacities:
            break

        active = list(capacities)
        preferences = _eligible_preference_weights(active, target_weights, score_table)
        start_remaining = remaining

        for ticker in active:
            desired = start_remaining * float(preferences.get(ticker, 0.0))
            allocation = min(capacities[ticker], desired, remaining)
            if allocation <= 1e-12:
                continue
            w.loc[ticker] = float(w.get(ticker, 0.0)) + allocation
            recipients[ticker] = recipients.get(ticker, 0.0) + allocation
            remaining -= allocation

        if start_remaining - remaining <= 1e-12:
            break

    allocated = max(0.0, float(amount) - remaining)
    return w, allocated, remaining, recipients


def _format_recipient_allocations(recipients: dict[str, float]) -> str:
    if not recipients:
        return ""
    return ",".join(
        f"{ticker}:{weight:.6f}"
        for ticker, weight in sorted(recipients.items(), key=lambda item: item[1], reverse=True)
    )


def apply_stale_position_exit_overlay(
    weights: pd.Series,
    score_table: pd.DataFrame,
    eligible_assets: list[str],
    target_weights: pd.Series,
) -> tuple[pd.Series, list[dict]]:
    """
    Hard exits go to SGOV. Soft 50% stale trims rotate into current eligible ETFs.
    """
    if not USE_STALE_POSITION_EXIT_OVERLAY:
        return weights, []

    w = weights.copy().astype(float).fillna(0.0).clip(lower=0.0)
    eligible_set = set(eligible_assets)
    actions: list[dict] = []

    for ticker in list(w.index):
        if ticker == CASH_TICKER:
            continue

        current_weight = float(w.get(ticker, 0.0))
        if current_weight <= 0 or ticker in eligible_set:
            continue

        score_row = (
            score_table.loc[ticker]
            if score_table is not None and not score_table.empty and ticker in score_table.index
            else pd.Series(dtype=object)
        )

        above_sma126_raw = score_row.get("AboveSMA126", np.nan)
        mom63 = score_row.get("Mom63", np.nan)
        mom126 = score_row.get("Mom126", np.nan)
        below_sma126 = False if pd.isna(above_sma126_raw) else not bool(above_sma126_raw)
        both_momentum_negative = (
            pd.notna(mom63) and pd.notna(mom126)
            and float(mom63) < 0 and float(mom126) < 0
        )

        recipients: dict[str, float] = {}
        redistributed = 0.0
        moved_to_sgov = 0.0

        if below_sma126 or both_momentum_negative:
            released = current_weight
            w.loc[ticker] = 0.0
            w = _move_amount_to_cash(w, released)
            moved_to_sgov = released
            action_type = "HardExit"
            if below_sma126:
                reason = "No longer eligible and below SMA126 -> full exit to SGOV"
            else:
                reason = "No longer eligible and Mom63/Mom126 both negative -> full exit to SGOV"
        else:
            new_weight = current_weight * (1.0 - STALE_INELIGIBLE_REDUCTION_FRACTION)
            released = current_weight - new_weight
            w.loc[ticker] = new_weight
            w, redistributed, unallocated, recipients = _redistribute_to_eligible(
                weights=w,
                amount=released,
                eligible_assets=eligible_assets,
                target_weights=target_weights,
                score_table=score_table,
                exclude_assets={ticker},
            )
            if unallocated > 1e-12:
                w = _move_amount_to_cash(w, unallocated)
                moved_to_sgov = unallocated
            action_type = "SoftTrim"
            reason = (
                f"No longer eligible -> reduce by {STALE_INELIGIBLE_REDUCTION_FRACTION:.0%}; "
                "rotate released weight into current eligible basket"
            )

        actions.append({
            "Ticker": ticker,
            "Overlay": "StalePositionExit",
            "ActionType": action_type,
            "WeightBefore": current_weight,
            "WeightAfter": float(w.get(ticker, 0.0)),
            "WeightReleased": released,
            "WeightRedistributedToEligible": redistributed,
            "WeightFreedToSGOV": moved_to_sgov,
            "RecipientAllocations": _format_recipient_allocations(recipients),
            "Reason": reason,
            "AboveSMA126": above_sma126_raw,
            "Mom63": mom63,
            "Mom126": mom126,
        })

    return _normalize_overlay_weights(w), actions


def _effective_positive_correlation(
    train_returns: pd.DataFrame,
    assets: list[str],
) -> pd.DataFrame:
    """Effective positive correlation = max(raw 63d corr, raw 126d corr)."""
    available = [a for a in assets if a in train_returns.columns]
    if len(available) < 2:
        return pd.DataFrame(index=available, columns=available, dtype=float)

    fast = train_returns[available].tail(min(FAST_CORR_LOOKBACK_DAYS, len(train_returns))).corr()
    slow = train_returns[available].tail(min(SLOW_CORR_LOOKBACK_DAYS, len(train_returns))).corr()
    effective = pd.DataFrame(index=available, columns=available, dtype=float)

    for a in available:
        for b in available:
            values = [v for v in (fast.loc[a, b], slow.loc[a, b]) if pd.notna(v)]
            effective.loc[a, b] = max(values) if values else np.nan
    return effective


def _weaker_pair_member(
    ticker_a: str,
    ticker_b: str,
    weights: pd.Series,
    score_table: pd.DataFrame,
    eligible_assets: list[str],
) -> tuple[str, str]:
    eligible_set = set(eligible_assets)
    a_eligible = ticker_a in eligible_set
    b_eligible = ticker_b in eligible_set

    if a_eligible != b_eligible:
        return (ticker_b, ticker_a) if a_eligible else (ticker_a, ticker_b)

    score_a = _score_value(score_table, ticker_a)
    score_b = _score_value(score_table, ticker_b)
    if score_a != score_b:
        return (ticker_a, ticker_b) if score_a < score_b else (ticker_b, ticker_a)

    weight_a = float(weights.get(ticker_a, 0.0))
    weight_b = float(weights.get(ticker_b, 0.0))
    return (ticker_a, ticker_b) if weight_a <= weight_b else (ticker_b, ticker_a)


def apply_correlation_deconcentration_overlay(
    weights: pd.Series,
    train_returns: pd.DataFrame,
    score_table: pd.DataFrame,
    eligible_assets: list[str],
    target_weights: pd.Series,
) -> tuple[pd.Series, list[dict]]:
    """
    Trim only pairs with corr >= 0.85 AND combined weight > 15%.
    Rotate the released amount to less-correlated eligible ETFs; SGOV is fallback only.
    """
    if not USE_CORRELATION_DECONCENTRATION_OVERLAY:
        return weights, []

    w = weights.copy().astype(float).fillna(0.0).clip(lower=0.0)
    all_corr_assets = list(dict.fromkeys(
        [t for t, x in w.items() if t != CASH_TICKER and float(x) > 0]
        + [t for t in eligible_assets if t != CASH_TICKER]
    ))

    if len(all_corr_assets) < 2:
        return _normalize_overlay_weights(w), []

    corr = _effective_positive_correlation(train_returns, all_corr_assets)
    actions: list[dict] = []

    for _ in range(100):
        holdings = [
            t for t, x in w.items()
            if t != CASH_TICKER and float(x) > 1e-12 and t in corr.index
        ]
        violations: list[tuple[float, float, str, str]] = []

        for i, ticker_a in enumerate(holdings):
            for ticker_b in holdings[i + 1:]:
                value = corr.loc[ticker_a, ticker_b]
                if pd.isna(value):
                    continue
                correlation = float(value)
                if correlation < CORR_DECONCENTRATION_THRESHOLD:
                    continue
                pair_weight = float(w.get(ticker_a, 0.0)) + float(w.get(ticker_b, 0.0))
                if pair_weight > MAX_CORRELATED_PAIR_WEIGHT + 1e-12:
                    violations.append((pair_weight - MAX_CORRELATED_PAIR_WEIGHT, correlation, ticker_a, ticker_b))

        if not violations:
            break

        violations.sort(reverse=True)
        excess, correlation, ticker_a, ticker_b = violations[0]
        weaker, stronger = _weaker_pair_member(
            ticker_a, ticker_b, w, score_table, eligible_assets
        )

        weaker_before = float(w.get(weaker, 0.0))
        if weaker_before <= 1e-12:
            break

        reduction = min(weaker_before, excess)
        pair_weight_before = float(w.get(ticker_a, 0.0)) + float(w.get(ticker_b, 0.0))
        w.loc[weaker] = weaker_before - reduction

        w, redistributed, unallocated, recipients = _redistribute_to_eligible(
            weights=w,
            amount=reduction,
            eligible_assets=eligible_assets,
            target_weights=target_weights,
            score_table=score_table,
            exclude_assets={ticker_a, ticker_b},
            corr=corr,
            enforce_pair_caps=True,
        )

        moved_to_sgov = 0.0
        if unallocated > 1e-12:
            w = _move_amount_to_cash(w, unallocated)
            moved_to_sgov = unallocated

        actions.append({
            "Ticker": weaker,
            "Overlay": "CorrelationDeconcentration",
            "ActionType": "PairTrim",
            "WeightBefore": weaker_before,
            "WeightAfter": float(w.get(weaker, 0.0)),
            "WeightReleased": reduction,
            "WeightRedistributedToEligible": redistributed,
            "WeightFreedToSGOV": moved_to_sgov,
            "RecipientAllocations": _format_recipient_allocations(recipients),
            "Reason": (
                f"Pair correlation {correlation:.3f} >= {CORR_DECONCENTRATION_THRESHOLD:.2f} "
                f"and combined weight exceeded {MAX_CORRELATED_PAIR_WEIGHT:.0%}; "
                "trim weaker member and rotate to less-correlated eligible ETFs"
            ),
            "CorrelationPair": ",".join(sorted([ticker_a, ticker_b])),
            "PairCorrelation": correlation,
            "PairWeightBefore": pair_weight_before,
            "PairWeightCap": MAX_CORRELATED_PAIR_WEIGHT,
            "StrongerPairMember": stronger,
        })

    return _normalize_overlay_weights(w), actions
'''


def migrate_strategy_to_v2(text: str) -> str:
    text = ensure_v1_overlay(text)

    if "MAX_CORRELATED_PAIR_WEIGHT = 0.15" in text:
        print("Strategy already contains V2 pairwise correlation overlay.")
        return text

    old_config = '''# Correlation deconcentration is weight-aware: high correlation alone does not force a cut.
# Only positive-correlation clusters >= 0.80 with combined weight > 20% are reduced.
USE_CORRELATION_DECONCENTRATION_OVERLAY = True
CORR_DECONCENTRATION_THRESHOLD = 0.80
MAX_CORRELATED_CLUSTER_WEIGHT = 0.20'''

    new_config = '''# Correlation deconcentration is pairwise and weight-aware.
# High correlation alone does not force a cut:
# - effective positive correlation must be >= 0.85
# - the pair's combined portfolio weight must exceed 15%
# The weaker side is trimmed and rotated to less-correlated eligible ETFs.
USE_CORRELATION_DECONCENTRATION_OVERLAY = True
CORR_DECONCENTRATION_THRESHOLD = 0.85
MAX_CORRELATED_PAIR_WEIGHT = 0.15'''

    text = replace_once(text, old_config, new_config, "V1 correlation config")

    helper_start = "\ndef _move_freed_weight_to_cash("
    optimizer_marker = (
        "\n\n# ============================================================\n"
        "# RISKFOLIO OPTIMIZER\n"
        "# ============================================================"
    )
    start_idx = text.find(helper_start)
    end_idx = text.find(optimizer_marker, start_idx)
    if start_idx < 0 or end_idx < 0:
        raise RuntimeError("Could not locate V1 overlay helper block.")
    text = text[:start_idx] + NEW_HELPER_BLOCK + text[end_idx:]

    old_stale_call = '''        weights_after_stale_exit, stale_exit_actions = apply_stale_position_exit_overlay(
            weights=weights_after_turnover_cap,
            score_table=score_table,
            eligible_assets=eligible_assets,
        )'''
    new_stale_call = '''        weights_after_stale_exit, stale_exit_actions = apply_stale_position_exit_overlay(
            weights=weights_after_turnover_cap,
            score_table=score_table,
            eligible_assets=eligible_assets,
            target_weights=target_final_weights,
        )'''
    text = replace_once(text, old_stale_call, new_stale_call, "stale overlay call")

    old_corr_call = '''        weights_after_correlation_overlay, correlation_actions = apply_correlation_deconcentration_overlay(
            weights=weights_after_stale_exit,
            train_returns=train_returns,
            score_table=score_table,
            eligible_assets=eligible_assets,
        )'''
    new_corr_call = '''        weights_after_correlation_overlay, correlation_actions = apply_correlation_deconcentration_overlay(
            weights=weights_after_stale_exit,
            train_returns=train_returns,
            score_table=score_table,
            eligible_assets=eligible_assets,
            target_weights=target_final_weights,
        )'''
    text = replace_once(text, old_corr_call, new_corr_call, "correlation overlay call")

    return text


def patch_workflow(text: str) -> str:
    if "risk_overlay_adjustments.csv" in text:
        return text
    anchor = (
        "            outputs_option2_v5_16_score_tilted_cvar/"
        "walk_forward_windows/2023/turnover_by_rebalance.csv"
    )
    if anchor not in text:
        raise RuntimeError("Workflow artifact anchor not found: turnover_by_rebalance.csv")
    return text.replace(
        anchor,
        anchor + "\n            outputs_option2_v5_16_score_tilted_cvar/"
        "walk_forward_windows/2023/risk_overlay_adjustments.csv",
        1,
    )


def main() -> None:
    if not PRODUCTION_FILE.exists():
        raise FileNotFoundError(f"Run from repository root. Missing: {PRODUCTION_FILE}")

    original = PRODUCTION_FILE.read_text(encoding="utf-8")
    patched = migrate_strategy_to_v2(original)
    compile(patched, str(PRODUCTION_FILE), "exec")

    backup = PRODUCTION_FILE.with_suffix(PRODUCTION_FILE.suffix + ".v1-overlay-backup")
    if patched != original:
        if not backup.exists():
            shutil.copy2(PRODUCTION_FILE, backup)
            print(f"Backup created: {backup}")
        PRODUCTION_FILE.write_text(patched, encoding="utf-8")
        print(f"Updated strategy: {PRODUCTION_FILE}")
    else:
        print(f"No strategy update needed: {PRODUCTION_FILE}")

    if WORKFLOW_FILE.exists():
        wf_original = WORKFLOW_FILE.read_text(encoding="utf-8")
        wf_patched = patch_workflow(wf_original)
        if wf_patched != wf_original:
            WORKFLOW_FILE.write_text(wf_patched, encoding="utf-8")
            print(f"Updated workflow artifact list: {WORKFLOW_FILE}")

    print("V2 overlay upgrade complete and Python syntax validated.")
    print("Hard exits -> SGOV; soft stale trims -> eligible basket.")
    print("Correlation: >=0.85 and pair weight >15%; trim weaker side.")
    print("Correlation trim -> less-correlated eligible ETFs; SGOV fallback only.")


if __name__ == "__main__":
    main()
