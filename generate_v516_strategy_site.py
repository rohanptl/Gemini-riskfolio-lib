from __future__ import annotations

import argparse
import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from verify_v516_plugin_parity import (
    FILE_RULES,
    compare_file,
    load_manifest,
    validate_manifest,
)


DEFAULT_OUTPUT_DIR = Path("outputs_option2_v5_16_score_tilted_cvar")
DEFAULT_SITE_DIR = Path("site/v516")
DEFAULT_PARITY_DIR = Path("parity_baselines/v516")
DEFAULT_LIVE_TARGET_DIR = Path("live_targets/v516")


def read_csv(path: Path, index_col: int | None = None) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path, index_col=index_col)
    except Exception:
        return pd.DataFrame()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def fmt_pct(value: Any, digits: int = 1) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "—"
    if not np.isfinite(value):
        return "—"
    return f"{value * 100:.{digits}f}%"


def fmt_num(value: Any, digits: int = 2) -> str:
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "—"
    if not np.isfinite(value):
        return "—"
    return f"{value:.{digits}f}"


def safe_date(value: Any) -> str:
    if value is None or not str(value).strip():
        return "—"
    try:
        return pd.Timestamp(value).date().isoformat()
    except Exception:
        return str(value)


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def save_figure(fig: plt.Figure, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=145, bbox_inches="tight")
    plt.close(fig)


def plot_allocation(weights: pd.Series, path: Path) -> bool:
    if weights.empty:
        return False
    values = (weights.astype(float) * 100).sort_values()
    fig, ax = plt.subplots(figsize=(9, max(4.5, len(values) * 0.38)))
    ax.barh(values.index.astype(str), values.values)
    ax.set_xlabel("Weight (%)")
    ax.set_title("Current target allocation")
    ax.grid(axis="x", alpha=0.25)
    save_figure(fig, path)
    return True


def plot_cumulative(monthly: pd.DataFrame, path: Path) -> bool:
    if monthly.empty:
        return False
    frame = monthly.copy()
    frame.index = pd.to_datetime(frame.index, errors="coerce")
    frame = frame.loc[frame.index.notna()]
    columns = [c for c in ["Strategy", "SPY", "QQQ", "VTI"] if c in frame.columns]
    if not columns:
        return False
    cumulative = (1 + frame[columns].fillna(0.0)).cumprod()
    fig, ax = plt.subplots(figsize=(10, 5.2))
    for column in columns:
        ax.plot(cumulative.index, cumulative[column], label=column)
    ax.set_title("Cumulative growth of $1")
    ax.set_ylabel("Growth of $1")
    ax.legend()
    ax.grid(alpha=0.25)
    save_figure(fig, path)
    return True


def plot_drawdown(drawdowns: pd.DataFrame, path: Path) -> bool:
    if drawdowns.empty:
        return False
    frame = drawdowns.copy()
    frame.index = pd.to_datetime(frame.index, errors="coerce")
    frame = frame.loc[frame.index.notna()]
    columns = [c for c in ["Strategy", "SPY", "QQQ", "VTI"] if c in frame.columns]
    if not columns:
        return False
    fig, ax = plt.subplots(figsize=(10, 5.2))
    for column in columns:
        ax.plot(frame.index, frame[column] * 100, label=column)
    ax.set_title("Drawdown history")
    ax.set_ylabel("Drawdown (%)")
    ax.legend()
    ax.grid(alpha=0.25)
    save_figure(fig, path)
    return True


def plot_weights_history(
    weights: pd.DataFrame,
    final_weights: pd.Series,
    path: Path,
) -> bool:
    if weights.empty:
        return False
    frame = weights.copy()
    frame.index = pd.to_datetime(frame.index, errors="coerce")
    frame = frame.loc[frame.index.notna()]
    preferred = [
        ticker
        for ticker in final_weights.sort_values(ascending=False).index
        if ticker in frame.columns
    ]
    columns = preferred[:10]
    if "SGOV" in frame.columns and "SGOV" not in columns:
        columns = ["SGOV", *columns[:9]]
    if not columns:
        return False
    fig, ax = plt.subplots(figsize=(10, 5.6))
    for column in columns:
        ax.plot(frame.index, frame[column] * 100, label=column)
    ax.set_title("Portfolio weights through time")
    ax.set_ylabel("Weight (%)")
    ax.legend(ncol=2, fontsize=8)
    ax.grid(alpha=0.25)
    save_figure(fig, path)
    return True


def plot_turnover(turnover: pd.DataFrame, path: Path) -> bool:
    if (
        turnover.empty
        or "Date" not in turnover.columns
        or "Turnover" not in turnover.columns
    ):
        return False
    frame = turnover.copy()
    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    frame = frame.dropna(subset=["Date"])
    if frame.empty:
        return False
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(frame["Date"], frame["Turnover"] * 100)
    ax.axhline(
        20.0,
        linestyle="--",
        linewidth=1.0,
        label="Normal turnover cap",
    )
    ax.set_title("One-way turnover by rebalance")
    ax.set_ylabel("Turnover (%)")
    ax.legend()
    ax.grid(alpha=0.25)
    save_figure(fig, path)
    return True


def plot_cash_breadth(signal: pd.DataFrame, path: Path) -> bool:
    required = {"Date", "SignalBreadth", "CashWeight"}
    if signal.empty or not required.issubset(signal.columns):
        return False
    frame = signal.copy()
    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce")
    frame = frame.dropna(subset=["Date"])
    if frame.empty:
        return False
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(
        frame["Date"],
        frame["SignalBreadth"] * 100,
        label="Signal breadth",
    )
    ax.plot(
        frame["Date"],
        frame["CashWeight"] * 100,
        label="SGOV / cash",
    )
    ax.set_title("Breadth and cash sleeve")
    ax.set_ylabel("Percent")
    ax.legend()
    ax.grid(alpha=0.25)
    save_figure(fig, path)
    return True


def plot_monthly_heatmap(monthly: pd.DataFrame, path: Path) -> bool:
    if monthly.empty or "Strategy" not in monthly.columns:
        return False
    returns = monthly["Strategy"].copy()
    returns.index = pd.to_datetime(returns.index, errors="coerce")
    returns = returns.loc[returns.index.notna()]
    if returns.empty:
        return False

    table = pd.DataFrame({"return": returns})
    table["year"] = table.index.year
    table["month"] = table.index.month
    pivot = table.pivot(
        index="year",
        columns="month",
        values="return",
    ).reindex(columns=range(1, 13))
    if pivot.empty:
        return False

    fig, ax = plt.subplots(figsize=(11, max(3.6, len(pivot) * 0.55)))
    image = ax.imshow(pivot.values * 100, aspect="auto")
    fig.colorbar(image, ax=ax, fraction=0.025, pad=0.02, label="Return (%)")
    ax.set_xticks(range(12))
    ax.set_xticklabels(
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    )
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index.astype(str))
    ax.set_title("Strategy monthly returns")
    save_figure(fig, path)
    return True


def copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def evaluate_parity(
    baseline_dir: Path,
    window_dir: Path,
) -> tuple[str, list[dict[str, str]]]:
    details: list[dict[str, str]] = []

    try:
        manifest_ok, messages = validate_manifest(baseline_dir)
        details.append(
            {
                "check": "Manifest / production configuration",
                "status": "PASS" if manifest_ok else "FAIL",
                "detail": "; ".join(messages),
            }
        )

        manifest = load_manifest(baseline_dir)
        frozen = set(manifest.get("frozen_files", []))
        all_ok = manifest_ok

        for filename in frozen:
            rules = FILE_RULES.get(filename)
            if rules is None:
                continue

            current_path = window_dir / filename
            if not current_path.exists():
                details.append(
                    {
                        "check": filename,
                        "status": "FAIL",
                        "detail": "Current output missing",
                    }
                )
                all_ok = False
                continue

            ok, comparison = compare_file(
                baseline_path=baseline_dir / filename,
                modular_path=current_path,
                tolerance=float(rules["tolerance"]),
                allowed_extra_columns=rules["allowed_extra_columns"],
            )
            details.append(
                {
                    "check": filename,
                    "status": "PASS" if ok else "FAIL",
                    "detail": comparison,
                }
            )
            all_ok = all_ok and ok

        return ("PASS" if all_ok else "FAIL"), details

    except Exception as exc:
        return (
            "UNKNOWN",
            [
                {
                    "check": "Parity evaluation",
                    "status": "UNKNOWN",
                    "detail": str(exc),
                }
            ],
        )


def metric_cards(strategy: pd.Series) -> list[tuple[str, str]]:
    return [
        ("CAGR", fmt_pct(strategy.get("CAGR"))),
        ("Sharpe", fmt_num(strategy.get("Sharpe"))),
        ("Max drawdown", fmt_pct(strategy.get("Max Drawdown"))),
        ("Total return", fmt_pct(strategy.get("Total Return"))),
        ("Volatility", fmt_pct(strategy.get("Annual Volatility"))),
        ("Sortino", fmt_num(strategy.get("Sortino"))),
    ]


def benchmark_table(benchmark: pd.DataFrame) -> str:
    if benchmark.empty:
        return "<p class='muted'>Benchmark metrics unavailable.</p>"

    wanted = [
        "CAGR",
        "Sharpe",
        "Max Drawdown",
        "Annual Volatility",
        "Sortino",
        "MAR",
    ]

    rows = []
    for name, row in benchmark.iterrows():
        cells = [f"<td><strong>{esc(name)}</strong></td>"]
        for column in wanted:
            value = row.get(column)
            if column in {
                "CAGR",
                "Max Drawdown",
                "Annual Volatility",
            }:
                cells.append(f"<td>{fmt_pct(value)}</td>")
            else:
                cells.append(f"<td>{fmt_num(value)}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")

    headers = "".join(
        f"<th>{esc(column)}</th>"
        for column in ["Name", *wanted]
    )
    return (
        "<div class='table-wrap'><table><thead><tr>"
        + headers
        + "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def weights_table(
    weights: pd.Series,
    reasons: pd.DataFrame,
) -> str:
    if weights.empty:
        return "<p class='muted'>Current allocation unavailable.</p>"

    reason_map: dict[str, tuple[str, str]] = {}
    if not reasons.empty and "Ticker" in reasons.columns:
        for _, row in reasons.iterrows():
            reason_map[str(row["Ticker"])] = (
                str(row.get("SelectionBucket", "")),
                str(
                    row.get(
                        "PlainEnglishExplanation",
                        row.get("SelectionReason", ""),
                    )
                ),
            )

    rows = []
    for ticker, weight in weights.sort_values(ascending=False).items():
        bucket, explanation = reason_map.get(str(ticker), ("", ""))
        rows.append(
            "<tr>"
            f"<td><strong>{esc(ticker)}</strong></td>"
            f"<td>{fmt_pct(weight, 0)}</td>"
            f"<td>{esc(bucket)}</td>"
            f"<td class='explain'>{esc(explanation)}</td>"
            "</tr>"
        )

    return (
        "<div class='table-wrap'><table><thead><tr>"
        "<th>Ticker</th><th>Weight</th><th>Role</th>"
        "<th>Why it is here</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def parity_table(details: list[dict[str, str]]) -> str:
    rows = []
    for item in details:
        status = item["status"]
        rows.append(
            "<tr>"
            f"<td>{esc(item['check'])}</td>"
            f"<td><span class='status {status.lower()}'>"
            f"{esc(status)}</span></td>"
            f"<td class='explain'>{esc(item['detail'])}</td>"
            "</tr>"
        )

    return (
        "<div class='table-wrap'><table><thead><tr>"
        "<th>Check</th><th>Status</th><th>Detail</th>"
        "</tr></thead><tbody>"
        + "".join(rows)
        + "</tbody></table></div>"
    )


def artifact_links(
    site_dir: Path,
    output_dir: Path,
    window_dir: Path,
    live_target_dir: Path,
    parity_dir: Path,
    window: str,
) -> list[tuple[str, str]]:
    artifacts_dir = site_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    candidates = [
        ("Official target CSV", live_target_dir / "current_target.csv"),
        ("Official target JSON", live_target_dir / "current_target.json"),
        (
            "Final target weights",
            window_dir / "final_target_weights_tradeable.csv",
        ),
        (
            "Benchmark comparison",
            window_dir / "benchmark_comparison.csv",
        ),
        (
            "Turnover history",
            window_dir / "turnover_by_rebalance.csv",
        ),
        (
            "Selection reasons",
            window_dir / "final_portfolio_selection_reasons.csv",
        ),
        (
            "Plugin summary",
            window_dir / "risk_overlay_summary_by_rebalance.csv",
        ),
        ("Parity manifest", parity_dir / "manifest.json"),
        (
            "Allocation explanation HTML",
            output_dir
            / "allocation_explanation_reports"
            / f"allocation_explanation_{window}.html",
        ),
        (
            "Allocation explanation JSON",
            output_dir
            / "allocation_explanation_reports"
            / f"allocation_explanation_snapshot_{window}.json",
        ),
        (
            "Allocation explanation ZIP",
            output_dir
            / "allocation_explanation_reports"
            / f"allocation_explanation_pack_{window}.zip",
        ),
    ]

    links: list[tuple[str, str]] = []
    for label, src in candidates:
        if not src.exists():
            continue
        dst = artifacts_dir / src.name
        shutil.copy2(src, dst)
        links.append((label, f"artifacts/{dst.name}"))

    return links


def build_site(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    window: str = "2023",
    site_dir: Path = DEFAULT_SITE_DIR,
    parity_dir: Path = DEFAULT_PARITY_DIR,
    live_target_dir: Path = DEFAULT_LIVE_TARGET_DIR,
) -> Path:
    window_dir = output_dir / "walk_forward_windows" / window
    if not window_dir.exists():
        raise FileNotFoundError(
            f"Missing V5.16 window output directory: {window_dir}"
        )

    site_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = site_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)

    benchmark = read_csv(
        window_dir / "benchmark_comparison.csv",
        index_col=0,
    )
    final_weights_df = read_csv(
        window_dir / "final_target_weights_tradeable.csv",
        index_col=0,
    )
    final_weights = (
        final_weights_df["Weight"].astype(float)
        if "Weight" in final_weights_df.columns
        else pd.Series(dtype=float)
    )

    monthly = read_csv(
        window_dir / "monthly_returns.csv",
        index_col=0,
    )
    drawdowns = read_csv(
        window_dir / "drawdown_data.csv",
        index_col=0,
    )
    weights_history = read_csv(
        window_dir / "weights_by_rebalance.csv",
        index_col=0,
    )
    signal = read_csv(
        window_dir / "signal_cash_history.csv"
    )
    turnover = read_csv(
        window_dir / "turnover_by_rebalance.csv"
    )
    reasons = read_csv(
        window_dir / "final_portfolio_selection_reasons.csv"
    )
    overlay = read_csv(
        window_dir / "risk_overlay_summary_by_rebalance.csv"
    )
    walk_forward = read_csv(
        output_dir / "walk_forward_summary.csv",
        index_col=0,
    )

    live_target = read_json(
        live_target_dir / "current_target.json"
    )
    parity_manifest = read_json(
        parity_dir / "manifest.json"
    )
    parity_status, parity_details = evaluate_parity(
        parity_dir,
        window_dir,
    )

    strategy = (
        benchmark.loc["Strategy"]
        if not benchmark.empty and "Strategy" in benchmark.index
        else pd.Series(dtype=float)
    )

    generated_charts: list[tuple[str, str, str]] = []
    chart_specs = [
        (
            "Current allocation",
            "allocation.png",
            plot_allocation,
            (final_weights,),
        ),
        (
            "Cumulative performance",
            "cumulative_performance.png",
            plot_cumulative,
            (monthly,),
        ),
        (
            "Drawdown",
            "drawdown.png",
            plot_drawdown,
            (drawdowns,),
        ),
        (
            "Weight history",
            "weights_history.png",
            plot_weights_history,
            (weights_history, final_weights),
        ),
        (
            "Turnover",
            "turnover.png",
            plot_turnover,
            (turnover,),
        ),
        (
            "Breadth and cash sleeve",
            "cash_breadth.png",
            plot_cash_breadth,
            (signal,),
        ),
        (
            "Monthly returns",
            "monthly_returns_heatmap.png",
            plot_monthly_heatmap,
            (monthly,),
        ),
    ]

    for title, filename, func, func_args in chart_specs:
        target = assets_dir / filename
        if func(*func_args, target):
            generated_charts.append(
                (title, f"assets/{filename}", "")
            )

    correlation_src = (
        window_dir / "final_portfolio_correlation_heatmap.png"
    )
    if copy_if_exists(
        correlation_src,
        assets_dir / "final_portfolio_correlation_heatmap.png",
    ):
        generated_charts.append(
            (
                "Final portfolio correlation",
                "assets/final_portfolio_correlation_heatmap.png",
                "Correlation matrix for the current target holdings.",
            )
        )

    latest_turnover = (
        turnover.iloc[-1]
        if not turnover.empty
        else pd.Series(dtype=float)
    )
    latest_signal = (
        signal.iloc[-1]
        if not signal.empty
        else pd.Series(dtype=float)
    )
    latest_overlay = (
        overlay.iloc[-1]
        if not overlay.empty
        else pd.Series(dtype=float)
    )

    production_snapshot = parity_manifest.get(
        "production_snapshot",
        {},
    )

    run_setup = [
        ("Universe", "214 Wealthfront ETFs"),
        ("Window", window),
        (
            "Signal date",
            safe_date(
                live_target.get("source_signal_date")
                or parity_manifest.get("source_signal_date")
            ),
        ),
        ("Rebalance", "Rolling monthly as-of"),
        ("Benchmarks", "SPY · QQQ · VTI"),
        ("Cash sleeve", "SGOV"),
        (
            "Max ETF weight",
            fmt_pct(
                production_snapshot.get(
                    "max_risk_asset_weight",
                    0.18,
                ),
                0,
            ),
        ),
        (
            "Normal turnover cap",
            fmt_pct(
                production_snapshot.get(
                    "max_turnover_per_rebalance",
                    0.20,
                ),
                0,
            ),
        ),
        ("Execution weights", "Whole percentage points"),
        ("Short momentum", "Mom126Skip21"),
        ("Data source", "yfinance"),
        ("Parity", parity_status),
    ]

    execution_rows = [
        (
            "Latest turnover",
            fmt_pct(latest_turnover.get("Turnover")),
        ),
        (
            "Average turnover",
            (
                fmt_pct(turnover["Turnover"].dropna().mean())
                if "Turnover" in turnover.columns
                else "—"
            ),
        ),
        (
            "Median turnover",
            (
                fmt_pct(turnover["Turnover"].dropna().median())
                if "Turnover" in turnover.columns
                else "—"
            ),
        ),
        (
            "Latest signal breadth",
            fmt_pct(latest_signal.get("SignalBreadth")),
        ),
        (
            "Latest SGOV / cash weight",
            fmt_pct(
                latest_signal.get(
                    "CashWeight",
                    final_weights.get("SGOV", np.nan),
                )
            ),
        ),
        (
            "Eligible ETF count",
            fmt_num(latest_signal.get("EligibleCount"), 0),
        ),
        (
            "Hard exits latest rebalance",
            fmt_num(latest_overlay.get("HardExitActions"), 0),
        ),
        (
            "Correlation trims latest rebalance",
            fmt_num(
                latest_overlay.get("CorrelationActions"),
                0,
            ),
        ),
    ]

    links = artifact_links(
        site_dir,
        output_dir,
        window_dir,
        live_target_dir,
        parity_dir,
        window,
    )

    cards_html = "".join(
        (
            "<div class='metric-card'>"
            f"<div class='metric-label'>{esc(label)}</div>"
            f"<div class='metric-value'>{esc(value)}</div>"
            "</div>"
        )
        for label, value in metric_cards(strategy)
    )

    setup_html = "".join(
        (
            "<div class='setup-item'>"
            f"<span>{esc(label)}</span>"
            f"<strong>{esc(value)}</strong>"
            "</div>"
        )
        for label, value in run_setup
    )

    execution_html = "".join(
        (
            "<tr>"
            f"<td>{esc(label)}</td>"
            f"<td><strong>{esc(value)}</strong></td>"
            "</tr>"
        )
        for label, value in execution_rows
    )

    charts_html = "".join(
        (
            "<figure class='chart-card'>"
            f"<a href='{esc(src)}'>"
            f"<img src='{esc(src)}' alt='{esc(title)}'>"
            "</a>"
            "<figcaption>"
            f"<strong>{esc(title)}</strong>"
            + (
                f"<span>{esc(note)}</span>"
                if note
                else ""
            )
            + "</figcaption></figure>"
        )
        for title, src, note in generated_charts
    )

    artifacts_html = "".join(
        (
            f"<a class='artifact' href='{esc(href)}'>"
            f"<span>{esc(label)}</span>"
            f"<code>{esc(Path(href).name)}</code>"
            "</a>"
        )
        for label, href in links
    )

    walk_forward_html = (
        walk_forward.round(4).to_html(
            classes="data-table",
            border=0,
        )
        if not walk_forward.empty
        else "<p class='muted'>Walk-forward summary unavailable.</p>"
    )

    now = datetime.now(timezone.utc).isoformat()
    parity_class = parity_status.lower()

    snapshot = {
        "generated_at_utc": now,
        "strategy": "V5.16 ETF Rotation",
        "window": window,
        "parity_status": parity_status,
        "signal_date": (
            live_target.get("source_signal_date")
            or parity_manifest.get("source_signal_date")
        ),
        "metrics": {
            key: (
                None
                if pd.isna(value)
                else float(value)
            )
            for key, value in strategy.items()
            if isinstance(
                value,
                (int, float, np.integer, np.floating),
            )
        },
        "holdings": [
            {
                "ticker": str(ticker),
                "weight": float(weight),
            }
            for ticker, weight in final_weights.items()
        ],
        "production_snapshot": production_snapshot,
        "parity_checks": parity_details,
    }

    (site_dir / "strategy_snapshot.json").write_text(
        json.dumps(snapshot, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>V5.16 ETF Rotation · Evidence Packet</title>
<style>
:root {{
  --bg:#f5f7fb; --card:#ffffff; --ink:#151a24; --muted:#687386;
  --line:#e1e6ef; --accent:#2c3e62; --ok:#19733a;
  --bad:#a62b2b; --warn:#8a6214;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg:#0e1117; --card:#161b22; --ink:#e6edf3; --muted:#9aa7b5;
    --line:#2c3440; --accent:#b9c9ea; --ok:#55c77a;
    --bad:#ff7b72; --warn:#d7ad55;
  }}
}}
* {{ box-sizing:border-box; }}
html {{ scroll-behavior:smooth; }}
body {{
  margin:0; background:var(--bg); color:var(--ink);
  font:15px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
}}
a {{ color:inherit; }}
.shell {{ max-width:1180px; margin:0 auto; padding:24px; }}
.topnav {{
  position:sticky; top:0; z-index:5;
  background:color-mix(in srgb,var(--bg) 92%,transparent);
  backdrop-filter:blur(12px); border-bottom:1px solid var(--line);
}}
.topnav .inner {{
  max-width:1180px; margin:auto; display:flex; gap:20px;
  overflow:auto; padding:12px 24px;
}}
.topnav a {{
  text-decoration:none; color:var(--muted); white-space:nowrap;
}}
.hero {{ padding:44px 0 20px; }}
.eyebrow {{
  text-transform:uppercase; letter-spacing:.12em; color:var(--muted);
  font-size:12px; font-weight:700;
}}
h1 {{ font-size:44px; line-height:1.05; margin:8px 0 14px; }}
h2 {{ font-size:26px; margin:0 0 18px; }}
.subtitle {{
  max-width:800px; color:var(--muted); font-size:18px;
}}
.badges {{
  display:flex; gap:8px; flex-wrap:wrap; margin-top:18px;
}}
.badge,.status {{
  display:inline-block; border:1px solid var(--line);
  border-radius:999px; padding:5px 10px; font-size:12px; font-weight:700;
}}
.pass {{ color:var(--ok); }}
.fail {{ color:var(--bad); }}
.unknown {{ color:var(--warn); }}
.section {{ margin:28px 0; }}
.panel {{
  background:var(--card); border:1px solid var(--line);
  border-radius:16px; padding:22px;
}}
.setup-grid {{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
  gap:10px;
}}
.setup-item {{
  border-bottom:1px solid var(--line); padding:10px 0;
  display:flex; justify-content:space-between; gap:18px;
}}
.setup-item span {{ color:var(--muted); }}
.metrics {{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr));
  gap:12px;
}}
.metric-card {{
  background:var(--card); border:1px solid var(--line);
  border-radius:14px; padding:18px;
}}
.metric-label {{ color:var(--muted); font-size:13px; }}
.metric-value {{ font-size:27px; font-weight:750; margin-top:5px; }}
.two-col {{ display:grid; grid-template-columns:1fr 1fr; gap:18px; }}
.chart-grid {{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(360px,1fr));
  gap:16px;
}}
.chart-card {{
  margin:0; background:var(--card); border:1px solid var(--line);
  border-radius:14px; overflow:hidden;
}}
.chart-card img {{ width:100%; display:block; background:white; }}
.chart-card figcaption {{
  padding:12px 14px; display:flex; flex-direction:column;
}}
.chart-card figcaption span {{
  color:var(--muted); font-size:13px;
}}
.table-wrap {{ overflow:auto; }}
table,.dataframe {{ width:100%; border-collapse:collapse; }}
th,td {{
  padding:10px 12px; border-bottom:1px solid var(--line);
  text-align:right; vertical-align:top;
}}
th:first-child,td:first-child {{ text-align:left; }}
th {{
  color:var(--muted); font-size:12px; text-transform:uppercase;
  letter-spacing:.04em;
}}
.explain {{
  text-align:left; min-width:340px; color:var(--muted);
}}
.artifacts {{
  display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr));
  gap:10px;
}}
.artifact {{
  text-decoration:none; border:1px solid var(--line);
  background:var(--card); border-radius:12px; padding:14px;
  display:flex; flex-direction:column;
}}
.artifact code {{ color:var(--muted); margin-top:5px; }}
.muted {{ color:var(--muted); }}
.footer {{
  color:var(--muted); padding:30px 0 55px; font-size:13px;
}}
@media(max-width:760px) {{
  .two-col {{ grid-template-columns:1fr; }}
  h1 {{ font-size:34px; }}
  .chart-grid {{ grid-template-columns:1fr; }}
}}
</style>
</head>
<body>
<nav class="topnav"><div class="inner">
<a href="#overview">Overview</a>
<a href="#setup">Run setup</a>
<a href="#dashboard">Dashboard</a>
<a href="#allocation">Allocation</a>
<a href="#plots">Plots</a>
<a href="#metrics">Metrics</a>
<a href="#parity">Parity</a>
<a href="#artifacts">Artifacts</a>
</div></nav>
<main class="shell">
<section id="overview" class="hero">
<div class="eyebrow">Production evidence packet</div>
<h1>V5.16 ETF Rotation</h1>
<p class="subtitle">
Monthly tactical ETF allocation using trend and momentum screening,
score-tilted CVaR sizing, correlation controls, a dynamic SGOV cash sleeve,
turnover limits, and whole-percentage execution.
</p>
<div class="badges">
<span class="badge">Long / cash</span>
<span class="badge">Monthly rolling-as-of</span>
<span class="badge status {parity_class}">Parity {parity_status}</span>
</div>
</section>

<section id="setup" class="section panel">
<h2>Run setup</h2>
<div class="setup-grid">{setup_html}</div>
</section>

<section id="dashboard" class="section">
<h2>Dashboard</h2>
<div class="metrics">{cards_html}</div>
</section>

<section id="allocation" class="section panel">
<h2>Current target</h2>
<p class="muted">
Official/live metadata and the latest tradeable model target are shown
separately from historical backtest results.
</p>
{weights_table(final_weights, reasons)}
</section>

<section id="plots" class="section">
<h2>Selected plot gallery</h2>
<div class="chart-grid">{charts_html}</div>
</section>

<section id="metrics" class="section">
<div class="two-col">
<div class="panel">
<h2>Benchmark comparison</h2>
{benchmark_table(benchmark)}
</div>
<div class="panel">
<h2>Execution &amp; signals</h2>
<div class="table-wrap"><table><tbody>{execution_html}</tbody></table></div>
</div>
</div>
</section>

<section class="section panel">
<h2>Walk-forward validation</h2>
<p class="muted">
Separate start windows help distinguish historical backtest behavior from
the current live target.
</p>
{walk_forward_html}
</section>

<section id="parity" class="section panel">
<h2>Production parity</h2>
<p class="muted">
This compares the current run with the frozen V5.16 regression fixture.
A failed check should be investigated rather than silently rebasing it.
</p>
{parity_table(parity_details)}
</section>

<section id="artifacts" class="section">
<h2>Artifacts</h2>
<div class="artifacts">{artifacts_html}</div>
</section>

<footer class="footer">
Generated {esc(now)} · Research/implementation report generated from V5.16
model outputs; not an investment recommendation.
</footer>
</main>
</body>
</html>
"""

    index_path = site_dir / "index.html"
    index_path.write_text(page, encoding="utf-8")
    (site_dir / ".nojekyll").write_text("", encoding="utf-8")
    return index_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a GitHub Pages-ready V5.16 strategy evidence packet."
        )
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
    )
    parser.add_argument(
        "--window",
        default="2023",
    )
    parser.add_argument(
        "--site-dir",
        default=str(DEFAULT_SITE_DIR),
    )
    parser.add_argument(
        "--parity-baseline-dir",
        default=str(DEFAULT_PARITY_DIR),
    )
    parser.add_argument(
        "--live-target-dir",
        default=str(DEFAULT_LIVE_TARGET_DIR),
    )
    args = parser.parse_args()

    path = build_site(
        output_dir=Path(args.output_dir),
        window=str(args.window),
        site_dir=Path(args.site_dir),
        parity_dir=Path(args.parity_baseline_dir),
        live_target_dir=Path(args.live_target_dir),
    )
    print(f"V5.16 strategy site generated: {path}")


if __name__ == "__main__":
    main()
