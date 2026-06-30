#!/usr/bin/env python3
"""
explain_v516_allocation.py

Generate a plain-English allocation explanation report from V5.16 backtest outputs.

Run after:
    python main_option2_all_etfs_v5_16_score_tilted_cvar_production.py

Example:
    python explain_v516_allocation.py \
      --output-dir outputs_option2_v5_16_score_tilted_cvar \
      --window 2023 \
      --zip

Outputs are written to:
    <output-dir>/allocation_explanation_reports/

Generated files:
    allocation_explanation_<window>.md
    allocation_explanation_<window>.html
    final_allocation_explanation_<window>.csv
    allocation_explanation_snapshot_<window>.json
    allocation_explanation_pack_<window>.zip  # if --zip is passed

This script explains what is available in V5.16 outputs:
    - final weights
    - trend/momentum/volatility reasons
    - cash/SGOV logic
    - turnover impact
    - correlation/overlap context
    - benchmark context

V5.16 does not currently save exact internal attribution such as:
    - raw CVaR weights before score tilt
    - score tilt multipliers
    - pre-cash/post-cash weights by ticker
    - pre-turnover/post-turnover/pruned weights by ticker

So this script gives a strong shareable explanation from saved outputs, but it cannot fully reconstruct every optimizer internals step unless the main V5.16 script is later modified to save those fields.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_CASH_TICKER = "SGOV"
DEFAULT_BENCHMARKS = ["SPY", "QQQ", "VTI"]


def read_csv(path: Path, indexed: bool = False) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, index_col=0 if indexed else None)
    except Exception:
        return pd.DataFrame()


def pct(x: Any, digits: int = 2) -> str:
    try:
        if pd.isna(x):
            return "n/a"
        return f"{float(x) * 100:.{digits}f}%"
    except Exception:
        return "n/a"


def num(x: Any, digits: int = 3) -> str:
    try:
        if pd.isna(x):
            return "n/a"
        return f"{float(x):.{digits}f}"
    except Exception:
        return "n/a"


def boolish(x: Any) -> bool | None:
    if pd.isna(x):
        return None
    if isinstance(x, bool):
        return x
    s = str(x).strip().lower()
    if s in {"true", "1", "yes", "y"}:
        return True
    if s in {"false", "0", "no", "n"}:
        return False
    return None


def safe_value(row: pd.Series, col: str, default: Any = None) -> Any:
    return row[col] if isinstance(row, pd.Series) and col in row.index else default


def find_window_dir(output_dir: Path, window: str | None) -> tuple[str, Path]:
    wf = output_dir / "walk_forward_windows"
    if not wf.exists():
        return output_dir.name, output_dir

    dirs = sorted([p for p in wf.iterdir() if p.is_dir()], key=lambda p: p.name)
    if not dirs:
        raise FileNotFoundError(f"No walk-forward folders found under {wf}")

    if window:
        wanted = wf / str(window)
        if not wanted.exists():
            raise FileNotFoundError(f"Window folder not found: {wanted}")
        return str(window), wanted

    numeric = []
    for p in dirs:
        try:
            numeric.append((int(p.name), p))
        except ValueError:
            pass
    if numeric:
        _, latest = max(numeric, key=lambda x: x[0])
        return latest.name, latest
    return dirs[-1].name, dirs[-1]


def weight_series(path: Path) -> pd.Series:
    df = read_csv(path, indexed=True)
    if df.empty:
        return pd.Series(dtype=float)
    if "Weight" in df.columns:
        s = df["Weight"]
    else:
        s = df.iloc[:, 0]
    s = pd.to_numeric(s, errors="coerce").dropna()
    return s[s > 0].sort_values(ascending=False)


def normalize_ticker_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "Ticker" in out.columns:
        out["Ticker"] = out["Ticker"].astype(str)
        return out
    if "index" in out.columns:
        out = out.rename(columns={"index": "Ticker"})
    else:
        out = out.reset_index().rename(columns={"index": "Ticker"})
    out["Ticker"] = out["Ticker"].astype(str)
    return out


def markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    if df.empty:
        return "_No data available._"
    work = df.head(max_rows).copy() if max_rows else df.copy()
    work = work.fillna("")
    cols = list(work.columns)
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in work.iterrows():
        vals = [str(row[c]).replace("\n", " ").replace("|", "\\|") for c in cols]
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def markdown_to_simple_html(md: str, title: str) -> str:
    html_lines: list[str] = []
    table_lines: list[str] = []
    in_list = False
    in_code = False

    def flush_table() -> None:
        nonlocal table_lines
        if not table_lines:
            return
        rows = [[c.strip() for c in line.strip().strip("|").split("|")] for line in table_lines]
        table_lines = []
        if len(rows) < 2:
            return
        header = rows[0]
        body = rows[2:]
        html_lines.append("<table>")
        html_lines.append("<thead><tr>" + "".join(f"<th>{html.escape(c)}</th>" for c in header) + "</tr></thead>")
        html_lines.append("<tbody>")
        for row in body:
            html_lines.append("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in row) + "</tr>")
        html_lines.append("</tbody></table>")

    for line in md.splitlines():
        if line.startswith("| ") and line.endswith(" |"):
            table_lines.append(line)
            continue
        flush_table()

        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_code:
                html_lines.append("<pre><code>")
                in_code = True
            else:
                html_lines.append("</code></pre>")
                in_code = False
            continue
        if in_code:
            html_lines.append(html.escape(line))
            continue

        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue
        if stripped.startswith("- "):
            if not in_list:
                html_lines.append("<ul>")
                in_list = True
            html_lines.append(f"<li>{html.escape(stripped[2:])}</li>")
            continue
        if in_list:
            html_lines.append("</ul>")
            in_list = False

        if stripped.startswith("# "):
            html_lines.append(f"<h1>{html.escape(stripped[2:])}</h1>")
        elif stripped.startswith("## "):
            html_lines.append(f"<h2>{html.escape(stripped[3:])}</h2>")
        elif stripped.startswith("### "):
            html_lines.append(f"<h3>{html.escape(stripped[4:])}</h3>")
        else:
            escaped = html.escape(stripped)
            escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
            html_lines.append(f"<p>{escaped}</p>")
    flush_table()
    if in_list:
        html_lines.append("</ul>")

    css = """
    body { font-family: Arial, Helvetica, sans-serif; max-width: 1200px; margin: 32px; line-height: 1.45; color: #1f2937; }
    h1, h2, h3 { color: #111827; }
    table { border-collapse: collapse; width: 100%; margin: 16px 0 28px 0; font-size: 14px; }
    th, td { border: 1px solid #d1d5db; padding: 8px 10px; text-align: left; vertical-align: top; }
    th { background: #f3f4f6; font-weight: 700; }
    code { background: #f3f4f6; padding: 2px 4px; border-radius: 4px; }
    pre { background: #111827; color: #f9fafb; padding: 14px; border-radius: 6px; overflow-x: auto; }
    """
    return f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title><style>{css}</style></head><body>" + "\n".join(html_lines) + "</body></html>"


def load_data(window_dir: Path) -> dict[str, Any]:
    return {
        "final_weights": weight_series(window_dir / "final_target_weights.csv"),
        "tradeable_weights": weight_series(window_dir / "final_target_weights_tradeable.csv"),
        "reasons": normalize_ticker_df(read_csv(window_dir / "final_portfolio_selection_reasons.csv")),
        "signal_cash": read_csv(window_dir / "signal_cash_history.csv"),
        "turnover": read_csv(window_dir / "turnover_by_rebalance.csv"),
        "weights_hist": read_csv(window_dir / "weights_by_rebalance.csv", indexed=True),
        "eligibility": normalize_ticker_df(read_csv(window_dir / "eligibility_history.csv")),
        "high_corr": read_csv(window_dir / "final_portfolio_high_correlation_pairs.csv"),
        "final_attribution": normalize_ticker_df(read_csv(window_dir / "final_allocation_attribution.csv")),
        "benchmark": read_csv(window_dir / "benchmark_comparison.csv", indexed=True),
        "rolling_summary": read_csv(window_dir / "rolling_12m_summary.csv"),
        "worst_months": read_csv(window_dir / "worst_months.csv"),
    }


def latest_eligibility(eligibility: pd.DataFrame) -> pd.DataFrame:
    if eligibility.empty:
        return eligibility
    if "Date" in eligibility.columns and not eligibility["Date"].dropna().empty:
        latest_date = eligibility["Date"].dropna().iloc[-1]
        return eligibility[eligibility["Date"] == latest_date].copy()
    return eligibility.copy()


def build_explanation_table(data: dict[str, Any], cash_ticker: str) -> pd.DataFrame:
    final_weights: pd.Series = data["final_weights"]
    tradeable_weights: pd.Series = data["tradeable_weights"]
    reasons: pd.DataFrame = data["reasons"]
    eligibility: pd.DataFrame = latest_eligibility(data["eligibility"])
    weights_hist: pd.DataFrame = data["weights_hist"]

    if final_weights.empty and not tradeable_weights.empty:
        final_weights = tradeable_weights.copy()
    if final_weights.empty:
        raise ValueError("No final weights found. Expected final_target_weights.csv or final_target_weights_tradeable.csv")

    latest_date = None
    prev_date = None
    latest_weights = pd.Series(dtype=float)
    prev_weights = pd.Series(dtype=float)
    if not weights_hist.empty:
        latest_date = str(weights_hist.index[-1])
        latest_weights = pd.to_numeric(weights_hist.iloc[-1], errors="coerce").fillna(0.0)
        if len(weights_hist) >= 2:
            prev_date = str(weights_hist.index[-2])
            prev_weights = pd.to_numeric(weights_hist.iloc[-2], errors="coerce").fillna(0.0)

    rows: list[dict[str, Any]] = []

    for ticker, final_w in final_weights.items():
        reason_row = pd.Series(dtype=object)
        if not reasons.empty and "Ticker" in reasons.columns:
            m = reasons[reasons["Ticker"].astype(str) == str(ticker)]
            if not m.empty:
                reason_row = m.iloc[0]

        elig_row = pd.Series(dtype=object)
        if not eligibility.empty and "Ticker" in eligibility.columns:
            m = eligibility[eligibility["Ticker"].astype(str) == str(ticker)]
            if not m.empty:
                elig_row = m.iloc[0]

        tradeable_w = float(tradeable_weights.get(ticker, final_w)) if not tradeable_weights.empty else float(final_w)
        prev_w = float(prev_weights.get(ticker, 0.0)) if not prev_weights.empty else None
        latest_w = float(latest_weights.get(ticker, final_w)) if not latest_weights.empty else float(final_w)
        delta = latest_w - prev_w if prev_w is not None else None

        score = safe_value(reason_row, "Score", safe_value(elig_row, "Score", None))
        rank = safe_value(reason_row, "Rank", safe_value(elig_row, "Rank", None))
        in_basket = safe_value(reason_row, "InLatestEligibleBasket", safe_value(reason_row, "EligibleNow", None))
        in_basket_bool = boolish(in_basket)

        above50 = boolish(safe_value(reason_row, "AboveSMA50", safe_value(elig_row, "AboveSMA50", None)))
        above126 = boolish(safe_value(reason_row, "AboveSMA126", safe_value(elig_row, "AboveSMA126", None)))
        pos63 = boolish(safe_value(reason_row, "PositiveMom63", safe_value(elig_row, "PositiveMom63", None)))
        pos126 = boolish(safe_value(reason_row, "PositiveMom126", safe_value(elig_row, "PositiveMom126", None)))
        mom21 = safe_value(reason_row, "Mom21", safe_value(elig_row, "Mom21", None))
        mom63 = safe_value(reason_row, "Mom63", safe_value(elig_row, "Mom63", None))
        mom126 = safe_value(reason_row, "Mom126", safe_value(elig_row, "Mom126", None))
        vol63 = safe_value(reason_row, "Vol63Ann", safe_value(elig_row, "Vol63Ann", None))
        saved_reason = safe_value(reason_row, "Reason", "")

        if ticker == cash_ticker:
            bucket = "Cash / risk-control sleeve"
            plain = (
                f"{ticker} is the cash/T-bill sleeve. The model uses it when it does not want the full portfolio "
                "in risk ETFs, usually because market breadth is weaker or the selected ETF basket is too volatile."
            )
        else:
            positives = []
            if above50:
                positives.append("above medium-term trend")
            if above126:
                positives.append("above longer-term trend")
            if pos63:
                positives.append("positive 3-month momentum")
            if pos126:
                positives.append("positive 6-month momentum")

            if in_basket_bool is True:
                bucket = "Selected by latest signal basket"
                plain = (
                    f"{ticker} received an allocation because it passed the latest ETF selection process, "
                    "survived the diversification/correlation filter, and then received a weight from CVaR risk sizing plus the score tilt."
                )
            elif in_basket_bool is False:
                bucket = "Carryover / turnover-constrained holding"
                plain = (
                    f"{ticker} is likely a carryover holding. It may remain because V5.16 limits monthly turnover, "
                    "so the portfolio does not fully replace old positions in one rebalance."
                )
            else:
                bucket = "Allocated holding"
                plain = f"{ticker} received a final allocation in the V5.16 portfolio."

            if positives:
                plain += " Main positives: " + ", ".join(positives) + "."
            if saved_reason:
                plain += " Saved model note: " + str(saved_reason)

        rows.append({
            "Ticker": ticker,
            "FinalWeight": float(final_w),
            "FinalWeightPct": pct(final_w),
            "TradeableWeight": tradeable_w,
            "TradeableWeightPct": pct(tradeable_w),
            "PreviousWeight": prev_w,
            "PreviousWeightPct": pct(prev_w) if prev_w is not None else "n/a",
            "WeightChange": delta,
            "WeightChangePct": pct(delta) if delta is not None else "n/a",
            "SelectionBucket": bucket,
            "PlainEnglishExplanation": plain,
            "InLatestEligibleBasket": in_basket,
            "Score": score,
            "Rank": rank,
            "AboveSMA50": above50,
            "AboveSMA126": above126,
            "PositiveMom63": pos63,
            "PositiveMom126": pos126,
            "Mom21": mom21,
            "Mom21Pct": pct(mom21),
            "Mom63": mom63,
            "Mom63Pct": pct(mom63),
            "Mom126": mom126,
            "Mom126Pct": pct(mom126),
            "Vol63Ann": vol63,
            "Vol63AnnPct": pct(vol63),
            "SavedReason": saved_reason,
            "LatestRebalanceDate": latest_date,
            "PreviousRebalanceDate": prev_date,
        })

    out = pd.DataFrame(rows).sort_values("FinalWeight", ascending=False)

    # If the updated V5.16 strategy script generated deeper attribution,
    # merge the most useful attribution columns into the explanation CSV/report.
    final_attr = data.get("final_attribution", pd.DataFrame())
    if final_attr is not None and not final_attr.empty and "Ticker" in final_attr.columns:
        attr_cols = [
            "Ticker",
            "AllocationBucket",
            "OptimizerUsed",
            "OptimizerRawWeight",
            "OptimizerWeightAfterCap",
            "ScoreRankPct",
            "ScoreTiltMultiplier",
            "ScoreTiltPreCapWeight",
            "RiskWeightAfterScoreTilt",
            "CashScaledTargetWeight",
            "WeightBeforeTurnoverCap",
            "WeightAfterTurnoverCapBeforePrune",
            "WeightAfterPruningFinal",
            "TurnoverContributionOneWay",
        ]
        attr_cols = [c for c in attr_cols if c in final_attr.columns]
        if len(attr_cols) > 1:
            attr_small = final_attr[attr_cols].copy()
            out = out.merge(
                attr_small,
                on="Ticker",
                how="left",
                suffixes=("", "_Attribution"),
            )

    return out


def latest_row(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series(dtype=object)
    return df.iloc[-1]


def make_cash_summary(data: dict[str, Any], cash_ticker: str) -> pd.DataFrame:
    signal = latest_row(data["signal_cash"])
    final_cash = data["final_weights"].get(cash_ticker, 0.0) if not data["final_weights"].empty else 0.0
    rows = [
        ("Final cash / SGOV weight", pct(final_cash), "How much of the portfolio is parked in the cash/T-bill sleeve."),
        ("Signal breadth", pct(safe_value(signal, "SignalBreadth", None)), "How broad the market strength was across the ETF universe."),
        ("Breadth-driven cash", pct(safe_value(signal, "BreadthCashWeight", None)), "Cash suggested because not enough ETFs had strong signals."),
        ("Volatility-driven cash", pct(safe_value(signal, "VolCashWeight", None)), "Cash suggested because the selected risk sleeve was too volatile."),
        ("Active sleeve volatility", pct(safe_value(signal, "ActiveSleeveVol", None)), "Estimated annualized volatility of the selected ETF basket."),
        ("Eligible ETF count", str(safe_value(signal, "EligibleCount", "n/a")), "Number of ETFs that passed the latest selection process."),
    ]
    return pd.DataFrame(rows, columns=["Item", "Value", "Plain English"])


def make_turnover_summary(data: dict[str, Any]) -> pd.DataFrame:
    row = latest_row(data["turnover"])
    rows = [
        ("Latest turnover", pct(safe_value(row, "Turnover", None)), "One-way movement at the latest rebalance."),
        ("Turnover before pruning", pct(safe_value(row, "TurnoverBeforePrune", None)), "How much the model wanted to move before cleaning up tiny positions."),
        ("Extra turnover from pruning", pct(safe_value(row, "ExtraTurnoverFromPrune", None)), "Additional movement caused by removing very small positions."),
    ]
    return pd.DataFrame(rows, columns=["Item", "Value", "Plain English"])


def make_benchmark_summary(data: dict[str, Any], benchmarks: list[str]) -> pd.DataFrame:
    bench = data["benchmark"]
    if bench.empty:
        return pd.DataFrame()
    cols = [c for c in ["Total Return", "CAGR", "Annual Volatility", "Sharpe", "Max Drawdown"] if c in bench.columns]
    rows = []
    for name in ["Strategy"] + benchmarks:
        if name in bench.index:
            r = {"Name": name}
            for c in cols:
                r[c] = num(bench.loc[name, c]) if c == "Sharpe" else pct(bench.loc[name, c])
            rows.append(r)
    return pd.DataFrame(rows)


def make_corr_summary(data: dict[str, Any]) -> pd.DataFrame:
    """
    Robustly summarize final high-correlation pairs.

    Fixes pandas error:
        TypeError: arg must be a list, tuple, 1-d array, or Series

    Cause:
        Some CSVs can contain duplicate or unexpected correlation columns.
        After renaming, out["Correlation"] may become a DataFrame, not a Series.

    This version:
        - normalizes ticker-pair columns,
        - chooses one numeric correlation column,
        - safely handles duplicate column names,
        - returns a compact display table.
    """
    df = data.get("high_corr", pd.DataFrame())

    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()
    out.columns = [str(c).strip() for c in out.columns]

    # Identify likely ticker-pair columns.
    col_lowers = {c: c.lower().strip() for c in out.columns}

    asset1_candidates = [
        c for c, low in col_lowers.items()
        if low in {"asset1", "ticker1", "asset_1", "etf 1", "etf1", "asset_a", "ticker_a"}
    ]
    asset2_candidates = [
        c for c, low in col_lowers.items()
        if low in {"asset2", "ticker2", "asset_2", "etf 2", "etf2", "asset_b", "ticker_b"}
    ]

    # Identify likely correlation columns. Prefer explicit correlation names.
    corr_candidates = [
        c for c, low in col_lowers.items()
        if "corr" in low or low in {"rho", "correlation"}
    ]

    # If no explicit correlation column exists, look for the most numeric non-ticker column.
    if not corr_candidates:
        non_asset_cols = [
            c for c in out.columns
            if c not in asset1_candidates and c not in asset2_candidates
        ]
        numeric_scores = []
        for c in non_asset_cols:
            s = pd.to_numeric(out[c], errors="coerce")
            numeric_scores.append((s.notna().sum(), c))
        numeric_scores = sorted(numeric_scores, reverse=True)
        if numeric_scores and numeric_scores[0][0] > 0:
            corr_candidates = [numeric_scores[0][1]]

    if not corr_candidates:
        return out.head(20)

    corr_col = corr_candidates[0]

    display = pd.DataFrame(index=out.index)

    if asset1_candidates:
        display["ETF 1"] = out[asset1_candidates[0]].astype(str)
    elif out.shape[1] >= 1:
        display["ETF 1"] = out.iloc[:, 0].astype(str)
    else:
        display["ETF 1"] = ""

    if asset2_candidates:
        display["ETF 2"] = out[asset2_candidates[0]].astype(str)
    elif out.shape[1] >= 2:
        display["ETF 2"] = out.iloc[:, 1].astype(str)
    else:
        display["ETF 2"] = ""

    corr_obj = out[corr_col]

    # If duplicate columns cause DataFrame result, take the first column.
    if isinstance(corr_obj, pd.DataFrame):
        corr_series = corr_obj.iloc[:, 0]
    else:
        corr_series = corr_obj

    display["CorrelationRaw"] = pd.to_numeric(corr_series, errors="coerce")

    display = display.dropna(subset=["CorrelationRaw"])
    display = display.sort_values("CorrelationRaw", ascending=False)

    display["Correlation"] = display["CorrelationRaw"].map(lambda x: num(x))
    display = display.drop(columns=["CorrelationRaw"])

    return display[["ETF 1", "ETF 2", "Correlation"]].head(20)


def build_report(
    output_dir: Path,
    window_name: str,
    window_dir: Path,
    explanation: pd.DataFrame,
    cash_summary: pd.DataFrame,
    turnover_summary: pd.DataFrame,
    benchmark_summary: pd.DataFrame,
    corr_summary: pd.DataFrame,
    cash_ticker: str,
) -> str:
    latest_rebalance = "n/a"
    if not explanation.empty and "LatestRebalanceDate" in explanation.columns:
        s = explanation["LatestRebalanceDate"].dropna()
        if not s.empty:
            latest_rebalance = str(s.iloc[0])

    final_table = explanation[["Ticker", "FinalWeightPct", "WeightChangePct", "SelectionBucket", "PlainEnglishExplanation"]]
    base_signal_cols = ["Ticker", "FinalWeightPct", "Score", "AboveSMA50", "AboveSMA126", "PositiveMom63", "PositiveMom126", "Vol63AnnPct", "SelectionBucket"]
    extra_attr_cols = ["OptimizerRawWeight", "ScoreTiltMultiplier", "RiskWeightAfterScoreTilt", "CashScaledTargetWeight", "WeightAfterTurnoverCapBeforePrune", "WeightAfterPruningFinal"]
    signal_cols = [c for c in base_signal_cols + extra_attr_cols if c in explanation.columns]
    signal_table = explanation[signal_cols].copy()
    if "Score" in signal_table.columns:
        signal_table["Score"] = pd.to_numeric(signal_table["Score"], errors="coerce").round(3)

    return f"""# V5.16 Allocation Explanation Report

Generated at: `{datetime.now().isoformat(timespec='seconds')}`

Output folder: `{output_dir}`  
Window folder: `{window_dir}`  
Walk-forward window: `{window_name}`  
Latest rebalance date: `{latest_rebalance}`

## One-paragraph explanation

V5.16 is a monthly ETF allocation model. It starts with the Wealthfront ETF universe, downloads price data, ranks ETFs using trend, momentum, and volatility signals, removes weak or highly correlated choices, uses Riskfolio's CVaR optimizer to size the selected basket, modestly tilts weights toward higher-scoring ETFs, adds `{cash_ticker}` as a cash/T-bill sleeve when risk is elevated, applies a 20% monthly turnover cap, removes tiny positions, and then holds the final weights until the next monthly rebalance.

## Final allocation and plain-English reasons

{markdown_table(final_table)}

## Signal details behind each holding

{markdown_table(signal_table)}

## Cash / SGOV explanation

{markdown_table(cash_summary)}

## Turnover explanation

{markdown_table(turnover_summary)}

## Performance context

{markdown_table(benchmark_summary)}

## Correlation / overlap context

The table below shows highly correlated final holdings if the strategy output file exists. High correlation means two ETFs may move similarly, but it does not automatically mean one must be removed because the model also considers score, risk, and turnover.

{markdown_table(corr_summary, max_rows=20)}

## How to explain this to a non-technical person

- The model does not simply buy the highest-return ETFs.
- It first checks whether each ETF is in an uptrend and has positive momentum.
- It avoids owning too many ETFs that behave almost the same.
- It uses a risk optimizer to spread the portfolio across the selected ETFs.
- It gives a small extra push to ETFs with stronger scores.
- It parks part of the portfolio in `{cash_ticker}` when the opportunity set is not strong enough or when the selected basket is too volatile.
- It limits monthly trading so the portfolio does not churn too aggressively.

## What this report can and cannot prove

This report explains the allocation using files already generated by V5.16.

It can explain:
- final weights,
- trend and momentum reasons,
- cash/SGOV logic,
- turnover impact,
- correlation/overlap context,
- and benchmark performance context.

If `final_allocation_attribution.csv` exists, this report can include raw CVaR weights, score-tilt multipliers, cash-scaled weights, turnover-capped weights, and final pruned weights. If that file does not exist, the report falls back to the older summary-level explanation.

To get that level of detail, the main V5.16 strategy script would need to save an additional internal attribution file during each monthly rebalance.
"""


def write_outputs(
    output_dir: Path,
    window_name: str,
    window_dir: Path,
    explanation: pd.DataFrame,
    report_md: str,
    zip_pack: bool,
) -> dict[str, Path]:
    report_dir = output_dir / "allocation_explanation_reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    safe_window = re.sub(r"[^A-Za-z0-9_.-]+", "_", window_name)

    md_path = report_dir / f"allocation_explanation_{safe_window}.md"
    html_path = report_dir / f"allocation_explanation_{safe_window}.html"
    csv_path = report_dir / f"final_allocation_explanation_{safe_window}.csv"
    json_path = report_dir / f"allocation_explanation_snapshot_{safe_window}.json"

    md_path.write_text(report_md, encoding="utf-8")
    html_path.write_text(markdown_to_simple_html(report_md, f"V5.16 Allocation Explanation - {window_name}"), encoding="utf-8")
    explanation.to_csv(csv_path, index=False)

    snapshot = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "output_dir": str(output_dir),
        "window_name": window_name,
        "window_dir": str(window_dir),
        "files_used": [
            "final_target_weights.csv",
            "final_target_weights_tradeable.csv",
            "final_portfolio_selection_reasons.csv",
            "signal_cash_history.csv",
            "turnover_by_rebalance.csv",
            "weights_by_rebalance.csv",
            "eligibility_history.csv",
            "benchmark_comparison.csv",
            "final_portfolio_high_correlation_pairs.csv",
        ],
        "known_limitations": [
            "Raw Riskfolio CVaR weights before score tilt are not saved in V5.16 outputs.",
            "Exact score-tilt multipliers are not saved in V5.16 outputs.",
            "Exact pre-cash, post-cash, pre-turnover, and post-turnover ticker-level attribution is not saved in V5.16 outputs.",
        ],
        "final_holdings": explanation[["Ticker", "FinalWeight", "SelectionBucket", "PlainEnglishExplanation"]].to_dict(orient="records"),
    }
    json_path.write_text(json.dumps(snapshot, indent=2, default=str), encoding="utf-8")

    paths = {"markdown": md_path, "html": html_path, "csv": csv_path, "json": json_path}

    if zip_pack:
        zip_path = report_dir / f"allocation_explanation_pack_{safe_window}.zip"
        source_files = [
            window_dir / "final_target_weights_tradeable.csv",
            window_dir / "final_portfolio_selection_reasons.csv",
            window_dir / "signal_cash_history.csv",
            window_dir / "turnover_by_rebalance.csv",
            window_dir / "benchmark_comparison.csv",
            window_dir / "final_portfolio_high_correlation_pairs.csv",
            window_dir / "final_portfolio_correlation_heatmap.png",
        ]
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for p in [md_path, html_path, csv_path, json_path]:
                zf.write(p, arcname=p.name)
            for p in source_files:
                if p.exists():
                    zf.write(p, arcname=str(Path("source_outputs") / p.name))
        paths["zip"] = zip_path

    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a plain-English explanation report from V5.16 outputs.")
    parser.add_argument("--output-dir", default="outputs_option2_v5_16_score_tilted_cvar")
    parser.add_argument("--window", default=None, help="Walk-forward window folder, e.g. 2023. Defaults to latest numeric window.")
    parser.add_argument("--cash-ticker", default=DEFAULT_CASH_TICKER)
    parser.add_argument("--benchmarks", nargs="*", default=DEFAULT_BENCHMARKS)
    parser.add_argument("--zip", action="store_true", help="Create a zip pack with report + key source files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory not found: {output_dir}. Run the V5.16 strategy first.")

    window_name, window_dir = find_window_dir(output_dir, args.window)
    data = load_data(window_dir)
    explanation = build_explanation_table(data, args.cash_ticker)
    cash_summary = make_cash_summary(data, args.cash_ticker)
    turnover_summary = make_turnover_summary(data)
    benchmark_summary = make_benchmark_summary(data, args.benchmarks)
    corr_summary = make_corr_summary(data)

    report_md = build_report(
        output_dir=output_dir,
        window_name=window_name,
        window_dir=window_dir,
        explanation=explanation,
        cash_summary=cash_summary,
        turnover_summary=turnover_summary,
        benchmark_summary=benchmark_summary,
        corr_summary=corr_summary,
        cash_ticker=args.cash_ticker,
    )

    paths = write_outputs(output_dir, window_name, window_dir, explanation, report_md, args.zip)

    print("\nV5.16 allocation explanation created.")
    print(f"Window: {window_name}")
    print(f"Source folder: {window_dir}")
    print("\nFiles:")
    for label, path in paths.items():
        print(f"- {label}: {path}")
    print("\nMost useful file to share with non-technical readers:")
    print(f"  {paths['html']}")
    print("\nMost useful file for detailed review:")
    print(f"  {paths['csv']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
