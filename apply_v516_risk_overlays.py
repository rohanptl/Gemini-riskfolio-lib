from __future__ import annotations

from pathlib import Path

PRODUCTION_FILE = Path("main_option2_all_etfs_v5_16_rolling_asof_monthly_attribution_dynamic_enddate.py")
WORKFLOW_FILE = Path(".github/workflows/v516_rolling_asof_allocation_workflow.yml")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"Patch anchor not found: {label}")
    return text.replace(old, new, 1)


def patch_strategy(text: str) -> str:
    if "USE_STALE_POSITION_EXIT_OVERLAY = True" in text:
        print("Strategy already patched; skipping strategy changes.")
        return text

    text = replace_once(
        text,
        'USE_TURNOVER_CAP = True\nMAX_TURNOVER_PER_REBALANCE = 0.20\n\n# V5.6: keep turnover control, but do not let tiny residual positions linger forever.',
        '''USE_TURNOVER_CAP = True
MAX_TURNOVER_PER_REBALANCE = 0.20

# V5.16 production risk overlays.
# Stale-position exit rules override the turnover cap so broken carryovers cannot linger.
USE_STALE_POSITION_EXIT_OVERLAY = True
STALE_INELIGIBLE_REDUCTION_FRACTION = 0.50

# Correlation deconcentration is weight-aware: high correlation alone does not force a cut.
# Only positive-correlation clusters >= 0.80 with combined weight > 20% are reduced.
USE_CORRELATION_DECONCENTRATION_OVERLAY = True
CORR_DECONCENTRATION_THRESHOLD = 0.80
MAX_CORRELATED_CLUSTER_WEIGHT = 0.20

# V5.6: keep turnover control, but do not let tiny residual positions linger forever.''',
        "risk-overlay config",
    )

    helper_block = r'''

def _move_freed_weight_to_cash(weights: pd.Series, freed_weight: float) -> pd.Series:
    """Move de-risked weight into SGOV while preserving a 100% portfolio."""
    w = weights.copy().astype(float).fillna(0.0).clip(lower=0.0)
    if freed_weight > 0 and CASH_TICKER in w.index:
        w.loc[CASH_TICKER] = float(w.get(CASH_TICKER, 0.0)) + float(freed_weight)
    if w.sum() > 0:
        w = w / w.sum()
    return w


def apply_stale_position_exit_overlay(
    weights: pd.Series,
    score_table: pd.DataFrame,
    eligible_assets: list[str],
) -> tuple[pd.Series, list[dict]]:
    """
    Rules:
    - no longer eligible -> reduce by 50%
    - no longer eligible AND below SMA126 -> exit fully
    - no longer eligible AND Mom63 < 0 AND Mom126 < 0 -> exit fully
    Freed weight goes to SGOV.
    """
    if not USE_STALE_POSITION_EXIT_OVERLAY:
        return weights, []

    w = weights.copy().astype(float).fillna(0.0).clip(lower=0.0)
    eligible_set = set(eligible_assets)
    actions: list[dict] = []
    total_freed = 0.0

    for ticker in w.index:
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

        if below_sma126:
            new_weight = 0.0
            reason = "No longer eligible and below SMA126 -> full exit"
        elif both_momentum_negative:
            new_weight = 0.0
            reason = "No longer eligible and Mom63/Mom126 both negative -> full exit"
        else:
            new_weight = current_weight * (1.0 - STALE_INELIGIBLE_REDUCTION_FRACTION)
            reason = f"No longer eligible -> reduce by {STALE_INELIGIBLE_REDUCTION_FRACTION:.0%}"

        freed = max(0.0, current_weight - new_weight)
        if freed <= 1e-12:
            continue
        w.loc[ticker] = new_weight
        total_freed += freed
        actions.append({
            "Ticker": ticker,
            "Overlay": "StalePositionExit",
            "WeightBefore": current_weight,
            "WeightAfter": new_weight,
            "WeightFreedToSGOV": freed,
            "Reason": reason,
            "AboveSMA126": above_sma126_raw,
            "Mom63": mom63,
            "Mom126": mom126,
        })

    return _move_freed_weight_to_cash(w, total_freed), actions


def _effective_positive_correlation(
    train_returns: pd.DataFrame,
    assets: list[str],
) -> pd.DataFrame:
    """Use max positive 63d/126d correlation; negative correlation is diversifying."""
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


def _correlation_components(corr: pd.DataFrame, threshold: float) -> list[list[str]]:
    assets = corr.index.tolist()
    adjacency = {a: set() for a in assets}
    for i, a in enumerate(assets):
        for b in assets[i + 1:]:
            value = corr.loc[a, b]
            if pd.notna(value) and float(value) >= threshold:
                adjacency[a].add(b)
                adjacency[b].add(a)

    visited: set[str] = set()
    components: list[list[str]] = []
    for asset in assets:
        if asset in visited:
            continue
        stack = [asset]
        component: list[str] = []
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            component.append(node)
            stack.extend(adjacency[node] - visited)
        if len(component) > 1:
            components.append(component)
    return components


def apply_correlation_deconcentration_overlay(
    weights: pd.Series,
    train_returns: pd.DataFrame,
    score_table: pd.DataFrame,
    eligible_assets: list[str],
) -> tuple[pd.Series, list[dict]]:
    """
    Reduce only overweight correlated clusters. Excess is removed from the weakest
    member(s) first (non-eligible first, then lower score) and moved to SGOV.
    """
    if not USE_CORRELATION_DECONCENTRATION_OVERLAY:
        return weights, []

    w = weights.copy().astype(float).fillna(0.0).clip(lower=0.0)
    holdings = [t for t, x in w.items() if t != CASH_TICKER and float(x) > 0]
    if len(holdings) < 2:
        return w, []

    corr = _effective_positive_correlation(train_returns, holdings)
    components = _correlation_components(corr, CORR_DECONCENTRATION_THRESHOLD)
    eligible_set = set(eligible_assets)
    actions: list[dict] = []
    total_freed = 0.0

    for component in components:
        cluster_weight = float(w.reindex(component).fillna(0.0).sum())
        if cluster_weight <= MAX_CORRELATED_CLUSTER_WEIGHT + 1e-12:
            continue
        excess = cluster_weight - MAX_CORRELATED_CLUSTER_WEIGHT

        def weakness_key(ticker: str) -> tuple:
            score = np.nan
            if score_table is not None and not score_table.empty and ticker in score_table.index:
                score = score_table.loc[ticker].get("Score", np.nan)
            score_value = float(score) if pd.notna(score) else -np.inf
            return (0 if ticker not in eligible_set else 1, score_value, float(w.get(ticker, 0.0)))

        for ticker in sorted(component, key=weakness_key):
            if excess <= 1e-12:
                break
            current_weight = float(w.get(ticker, 0.0))
            if current_weight <= 0:
                continue
            reduction = min(current_weight, excess)
            new_weight = current_weight - reduction
            w.loc[ticker] = new_weight
            excess -= reduction
            total_freed += reduction

            peer_corr = [
                float(corr.loc[ticker, peer])
                for peer in component
                if peer != ticker and pd.notna(corr.loc[ticker, peer])
            ]
            actions.append({
                "Ticker": ticker,
                "Overlay": "CorrelationDeconcentration",
                "WeightBefore": current_weight,
                "WeightAfter": new_weight,
                "WeightFreedToSGOV": reduction,
                "Reason": (
                    f"Correlation cluster >= {CORR_DECONCENTRATION_THRESHOLD:.2f} "
                    f"exceeded {MAX_CORRELATED_CLUSTER_WEIGHT:.0%} combined weight"
                ),
                "CorrelationCluster": ",".join(sorted(component)),
                "MaxCorrelationToClusterPeer": max(peer_corr) if peer_corr else np.nan,
                "ClusterWeightBefore": cluster_weight,
                "ClusterWeightCap": MAX_CORRELATED_CLUSTER_WEIGHT,
            })

    return _move_freed_weight_to_cash(w, total_freed), actions
'''

    marker = "\n\n# ============================================================\n# RISKFOLIO OPTIMIZER\n# ============================================================"
    if marker not in text:
        raise RuntimeError("Patch anchor not found: optimizer section")
    text = text.replace(marker, helper_block + marker, 1)

    replacements = [
        (
            '    post_turnover_weights: pd.Series,\n    final_weights: pd.Series,',
            '    post_turnover_weights: pd.Series,\n    post_stale_exit_weights: pd.Series,\n    post_correlation_weights: pd.Series,\n    final_weights: pd.Series,',
            "attribution signature",
        ),
        (
            '            + [str(t) for t in post_turnover_weights.index.tolist()]\n            + [str(t) for t in final_weights.index.tolist()]',
            '            + [str(t) for t in post_turnover_weights.index.tolist()]\n            + [str(t) for t in post_stale_exit_weights.index.tolist()]\n            + [str(t) for t in post_correlation_weights.index.tolist()]\n            + [str(t) for t in final_weights.index.tolist()]',
            "attribution ticker union",
        ),
        (
            '    post_turnover = post_turnover_weights.reindex(all_tickers).fillna(0.0)\n    final = final_weights.reindex(all_tickers).fillna(0.0)',
            '    post_turnover = post_turnover_weights.reindex(all_tickers).fillna(0.0)\n    post_stale_exit = post_stale_exit_weights.reindex(all_tickers).fillna(0.0)\n    post_correlation = post_correlation_weights.reindex(all_tickers).fillna(0.0)\n    final = final_weights.reindex(all_tickers).fillna(0.0)',
            "attribution series",
        ),
        (
            '        post_turnover_weight = float(post_turnover.get(ticker, 0.0))',
            '        post_turnover_weight = float(post_turnover.get(ticker, 0.0))\n        post_stale_exit_weight = float(post_stale_exit.get(ticker, 0.0))\n        post_correlation_weight = float(post_correlation.get(ticker, 0.0))',
            "attribution row values",
        ),
        (
            '                "WeightAfterTurnoverCapBeforePrune": post_turnover_weight,\n                "WeightAfterPruningFinal": final_weight,',
            '                "WeightAfterTurnoverCapBeforePrune": post_turnover_weight,\n                "WeightAfterStaleExitOverlay": post_stale_exit_weight,\n                "WeightAfterCorrelationDeconcentration": post_correlation_weight,\n                "StaleExitOverlayReduction": max(0.0, post_turnover_weight - post_stale_exit_weight),\n                "CorrelationOverlayReduction": max(0.0, post_stale_exit_weight - post_correlation_weight),\n                "WeightAfterPruningFinal": final_weight,',
            "attribution columns",
        ),
        (
            '                "PrunedOrReducedByCleanup": (\n                    post_turnover_weight > 0 and final_weight < post_turnover_weight - 1e-12\n                ),',
            '                "PrunedOrReducedByCleanup": (\n                    post_correlation_weight > 0\n                    and final_weight < post_correlation_weight - 1e-12\n                ),',
            "prune flag",
        ),
        (
            '    allocation_attribution_rows = []\n    daily_portfolio_returns = []',
            '    allocation_attribution_rows = []\n    risk_overlay_rows = []\n    daily_portfolio_returns = []',
            "audit row list",
        ),
    ]
    for old, new, label in replacements:
        text = replace_once(text, old, new, label)

    old_flow = '''        turnover_before_prune = calculate_turnover(
            previous_weights=previous_weights,
            current_weights=weights_after_turnover_cap,
            all_assets=final_assets,
        )

        final_weights = prune_tiny_positions_after_turnover(weights_after_turnover_cap)

        turnover = calculate_turnover(
            previous_weights=previous_weights,
            current_weights=final_weights,
            all_assets=final_assets,
        )'''
    new_flow = '''        turnover_after_turnover_cap = calculate_turnover(
            previous_weights=previous_weights,
            current_weights=weights_after_turnover_cap,
            all_assets=final_assets,
        )

        weights_after_stale_exit, stale_exit_actions = apply_stale_position_exit_overlay(
            weights=weights_after_turnover_cap,
            score_table=score_table,
            eligible_assets=eligible_assets,
        )

        turnover_after_stale_exit = calculate_turnover(
            previous_weights=previous_weights,
            current_weights=weights_after_stale_exit,
            all_assets=final_assets,
        )

        weights_after_correlation_overlay, correlation_actions = apply_correlation_deconcentration_overlay(
            weights=weights_after_stale_exit,
            train_returns=train_returns,
            score_table=score_table,
            eligible_assets=eligible_assets,
        )

        turnover_before_prune = calculate_turnover(
            previous_weights=previous_weights,
            current_weights=weights_after_correlation_overlay,
            all_assets=final_assets,
        )

        for action in [*stale_exit_actions, *correlation_actions]:
            action["Date"] = date
            action["StartWindow"] = start_date
            risk_overlay_rows.append(action)

        final_weights = prune_tiny_positions_after_turnover(weights_after_correlation_overlay)

        turnover = calculate_turnover(
            previous_weights=previous_weights,
            current_weights=final_weights,
            all_assets=final_assets,
        )'''
    text = replace_once(text, old_flow, new_flow, "rebalance overlay flow")

    text = replace_once(
        text,
        '            post_turnover_weights=weights_after_turnover_cap,\n            final_weights=final_weights,',
        '            post_turnover_weights=weights_after_turnover_cap,\n            post_stale_exit_weights=weights_after_stale_exit,\n            post_correlation_weights=weights_after_correlation_overlay,\n            final_weights=final_weights,',
        "attribution call",
    )

    text = replace_once(
        text,
        '                "Turnover": turnover,\n                "TurnoverBeforePrune": turnover_before_prune,\n                "ExtraTurnoverFromPrune": max(0.0, turnover - turnover_before_prune),',
        '                "Turnover": turnover,\n                "TurnoverAfterTurnoverCap": turnover_after_turnover_cap,\n                "TurnoverAfterStaleExitOverlay": turnover_after_stale_exit,\n                "TurnoverBeforePrune": turnover_before_prune,\n                "ExtraTurnoverFromRiskOverlays": max(0.0, turnover_before_prune - (0.0 if np.isnan(turnover_after_turnover_cap) else turnover_after_turnover_cap)),\n                "ExtraTurnoverFromPrune": max(0.0, turnover - turnover_before_prune),',
        "turnover audit columns",
    )

    text = replace_once(
        text,
        '    turnover_df = pd.DataFrame(turnover_rows)\n    turnover_df.to_csv(output_dir / "turnover_by_rebalance.csv", index=False)\n\n    eligibility_df = pd.concat(eligibility_rows, ignore_index=True)',
        '    turnover_df = pd.DataFrame(turnover_rows)\n    turnover_df.to_csv(output_dir / "turnover_by_rebalance.csv", index=False)\n\n    risk_overlay_df = pd.DataFrame(risk_overlay_rows)\n    risk_overlay_df.to_csv(output_dir / "risk_overlay_adjustments.csv", index=False)\n\n    eligibility_df = pd.concat(eligibility_rows, ignore_index=True)',
        "overlay audit output",
    )

    diagnostic_old = '                f"eligible={len(eligible_assets)} | "\n                f"top={top_weights}"'
    diagnostic_new = '                f"eligible={len(eligible_assets)} | "\n                f"stale_actions={len(stale_exit_actions)} | "\n                f"corr_actions={len(correlation_actions)} | "\n                f"top={top_weights}"'
    text = replace_once(text, diagnostic_old, diagnostic_new, "console diagnostics")

    return text


def patch_workflow(text: str) -> str:
    if "risk_overlay_adjustments.csv" in text:
        return text
    anchor = "            outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023/turnover_by_rebalance.csv"
    if anchor not in text:
        raise RuntimeError("Workflow artifact anchor not found")
    return text.replace(
        anchor,
        anchor + "\n            outputs_option2_v5_16_score_tilted_cvar/walk_forward_windows/2023/risk_overlay_adjustments.csv",
        1,
    )


def main() -> None:
    if not PRODUCTION_FILE.exists():
        raise FileNotFoundError(f"Run from repo root; missing {PRODUCTION_FILE}")

    original = PRODUCTION_FILE.read_text(encoding="utf-8")
    patched = patch_strategy(original)
    compile(patched, str(PRODUCTION_FILE), "exec")
    if patched != original:
        PRODUCTION_FILE.write_text(patched, encoding="utf-8")
        print(f"Updated: {PRODUCTION_FILE}")

    if WORKFLOW_FILE.exists():
        wf_original = WORKFLOW_FILE.read_text(encoding="utf-8")
        wf_patched = patch_workflow(wf_original)
        if wf_patched != wf_original:
            WORKFLOW_FILE.write_text(wf_patched, encoding="utf-8")
            print(f"Updated: {WORKFLOW_FILE}")
    else:
        print(f"Warning: workflow not found: {WORKFLOW_FILE}")

    print("Patch complete and Python syntax validated.")
    print("New audit output: risk_overlay_adjustments.csv")


if __name__ == "__main__":
    main()
