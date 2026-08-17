from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

from lock_v516_monthly_target import read_target_weights


DEFAULT_LOCK_DIR = Path("live_targets/v516")
DEFAULT_OUTPUT_DIR = Path("outputs_monitor_v516")


@dataclass(frozen=True)
class MonitorResult:
    status: str
    summary: dict[str, object]
    drift: pd.DataFrame
    equity: pd.DataFrame


def _json_safe(value: object) -> object:
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, (float, np.floating)) and not np.isfinite(value):
        return None
    return value


def _format_percent(value: object) -> str:
    if value is None or not np.isfinite(float(value)):
        return "N/A"
    return f"{float(value):.2%}"


def _format_number(value: object, decimals: int = 2) -> str:
    if value is None or not np.isfinite(float(value)):
        return "N/A"
    return f"{float(value):.{decimals}f}"


def _extract_adjusted_close(raw: pd.DataFrame, tickers: list[str]) -> pd.DataFrame:
    if raw.empty:
        raise ValueError("Price download returned no data.")
    if isinstance(raw.columns, pd.MultiIndex):
        level0 = raw.columns.get_level_values(0)
        level1 = raw.columns.get_level_values(1)
        if "Adj Close" in level0:
            prices = raw.xs("Adj Close", axis=1, level=0)
        elif "Adj Close" in level1:
            prices = raw.xs("Adj Close", axis=1, level=1)
        elif "Close" in level0:
            prices = raw.xs("Close", axis=1, level=0)
        elif "Close" in level1:
            prices = raw.xs("Close", axis=1, level=1)
        else:
            raise KeyError("Downloaded data has no adjusted-close or close panel.")
    else:
        column = "Adj Close" if "Adj Close" in raw.columns else "Close"
        prices = raw[[column]].rename(columns={column: tickers[0]})
    prices.columns = [str(column).upper() for column in prices.columns]
    prices.index = pd.to_datetime(prices.index).tz_localize(None)
    return prices.sort_index().replace([np.inf, -np.inf], np.nan)


def download_prices(
    tickers: list[str], start_date: pd.Timestamp, end_date: pd.Timestamp
) -> pd.DataFrame:
    raw = yf.download(
        tickers,
        start=str(start_date.date()),
        end=str((end_date + pd.Timedelta(days=2)).date()),
        auto_adjust=False,
        progress=False,
        group_by="column",
        threads=False,
    )
    return _extract_adjusted_close(raw, tickers)


def read_actual_weights(path: Path | None) -> pd.Series | None:
    if path is None:
        return None
    return read_target_weights(path).rename("ActualWeight")


def build_monitor_result(
    locked_weights: pd.Series,
    metadata: dict[str, object],
    prices: pd.DataFrame,
    as_of_date: pd.Timestamp,
    *,
    actual_weights: pd.Series | None = None,
    drift_review_percentage_points: float = 2.0,
    stale_calendar_days: int = 4,
) -> MonitorResult:
    tickers = locked_weights.index.astype(str).str.upper().tolist()
    prices = prices.reindex(columns=tickers).sort_index()
    source_signal_date = pd.Timestamp(
        str(metadata.get("source_signal_date", metadata["rebalance_date"]))
    ).normalize()
    lock_date = pd.Timestamp(
        str(metadata.get("live_effective_date", metadata["rebalance_date"]))
    ).normalize()
    as_of_date = pd.Timestamp(as_of_date).normalize()
    if as_of_date < lock_date:
        drift = pd.DataFrame(
            {
                "LockedTargetWeight": locked_weights,
                "EstimatedCurrentWeight": np.nan,
                "EstimatedDriftPercentagePoints": np.nan,
                "LockedAdjustedClose": np.nan,
                "LatestAdjustedClose": np.nan,
                "ReturnSinceLock": np.nan,
            }
        )
        drift.index.name = "Ticker"
        summary = {
            "status": "PENDING_EFFECTIVE_DATE_NO_TRADE",
            "policy": "NO_TRADE_MONITOR_ONLY",
            "official_month": metadata["official_month"],
            "source_signal_date": str(source_signal_date.date()),
            "allocation_submitted_date": metadata.get("allocation_submitted_date"),
            "live_effective_date": str(lock_date.date()),
            "monitor_as_of_date": str(as_of_date.date()),
            "latest_common_price_date": None,
            "calendar_days_stale": None,
            "missing_tickers": [],
            "drift_source": "EstimatedCurrentWeight",
            "max_absolute_drift_percentage_points": None,
            "drift_review_threshold_percentage_points": drift_review_percentage_points,
            "estimated_portfolio_return_since_lock": None,
            "current_drawdown_since_lock": None,
            "max_drawdown_since_lock": None,
            "next_scheduled_rebalance_date": metadata[
                "next_scheduled_rebalance_date"
            ],
            "instruction": (
                "The live target is not effective yet. Do not trade again; "
                "wait for the effective date."
            ),
            "estimation_limitations": [],
        }
        return MonitorResult(
            status="PENDING_EFFECTIVE_DATE_NO_TRADE",
            summary=summary,
            drift=drift,
            equity=pd.DataFrame(columns=["Equity", "Drawdown"]),
        )

    available = prices.loc[:as_of_date]
    missing = [ticker for ticker in tickers if available[ticker].dropna().empty]
    last_dates = {
        ticker: available[ticker].dropna().index.max()
        for ticker in tickers
        if ticker not in missing
    }
    common_date = min(last_dates.values()) if last_dates else pd.NaT
    window = available.loc[:common_date].ffill() if pd.notna(common_date) else available
    lock_prices = pd.Series(index=tickers, dtype=float)
    latest_prices = pd.Series(index=tickers, dtype=float)
    for ticker in tickers:
        history = window.loc[:lock_date, ticker].dropna()
        lock_prices[ticker] = history.iloc[-1] if not history.empty else np.nan
        latest = window[ticker].dropna()
        latest_prices[ticker] = latest.iloc[-1] if not latest.empty else np.nan
    missing_lock = lock_prices[lock_prices.isna()].index.tolist()
    missing_all = sorted(set(missing + missing_lock))

    ratios = window.loc[lock_date:, tickers].divide(lock_prices, axis=1)
    equity_curve = ratios.mul(locked_weights, axis=1).sum(axis=1, min_count=len(tickers))
    equity = pd.DataFrame({"Equity": equity_curve.dropna()})
    if not equity.empty:
        equity["Drawdown"] = equity["Equity"] / equity["Equity"].cummax() - 1.0
        portfolio_return = float(equity["Equity"].iloc[-1] - 1.0)
        drawdown = float(equity["Drawdown"].iloc[-1])
        max_drawdown = float(equity["Drawdown"].min())
    else:
        equity["Drawdown"] = pd.Series(dtype=float)
        portfolio_return = drawdown = max_drawdown = np.nan
    portfolio_return = 0.0 if abs(portfolio_return) < 1e-12 else portfolio_return
    drawdown = 0.0 if abs(drawdown) < 1e-12 else drawdown
    max_drawdown = 0.0 if abs(max_drawdown) < 1e-12 else max_drawdown

    current_values = locked_weights * (latest_prices / lock_prices)
    estimated_weights = current_values / current_values.sum()
    drift = pd.DataFrame(
        {
            "LockedTargetWeight": locked_weights,
            "EstimatedCurrentWeight": estimated_weights,
            "EstimatedDriftPercentagePoints": (
                estimated_weights - locked_weights
            ) * 100.0,
            "LockedAdjustedClose": lock_prices,
            "LatestAdjustedClose": latest_prices,
            "ReturnSinceLock": latest_prices / lock_prices - 1.0,
        }
    )
    drift.index.name = "Ticker"
    drift_source = "EstimatedCurrentWeight"
    if actual_weights is not None:
        actual = actual_weights.reindex(tickers).fillna(0.0)
        if actual.sum() > 0.0:
            actual = actual / actual.sum()
        drift["ActualWeight"] = actual
        drift["ActualDriftPercentagePoints"] = (
            actual - locked_weights
        ) * 100.0
        drift_source = "ActualWeight"
        max_abs_drift = float(drift["ActualDriftPercentagePoints"].abs().max())
    else:
        max_abs_drift = float(
            drift["EstimatedDriftPercentagePoints"].abs().max()
        )
    max_abs_drift = 0.0 if abs(max_abs_drift) < 1e-12 else max_abs_drift

    stale_days = (
        int((as_of_date - pd.Timestamp(common_date)).days)
        if pd.notna(common_date)
        else None
    )
    if missing_all:
        status = "DATA_ERROR"
    elif stale_days is None or stale_days > stale_calendar_days:
        status = "STALE_DATA"
    elif max_abs_drift >= drift_review_percentage_points:
        status = "REVIEW_DRIFT_NO_TRADE"
    else:
        status = "NORMAL_NO_TRADE"

    summary = {
        "status": status,
        "policy": "NO_TRADE_MONITOR_ONLY",
        "official_month": metadata["official_month"],
        "source_signal_date": str(source_signal_date.date()),
        "allocation_submitted_date": metadata.get("allocation_submitted_date"),
        "live_effective_date": str(lock_date.date()),
        "monitor_as_of_date": str(as_of_date.date()),
        "latest_common_price_date": (
            str(pd.Timestamp(common_date).date()) if pd.notna(common_date) else None
        ),
        "calendar_days_stale": stale_days,
        "missing_tickers": missing_all,
        "drift_source": drift_source,
        "max_absolute_drift_percentage_points": max_abs_drift,
        "drift_review_threshold_percentage_points": drift_review_percentage_points,
        "estimated_portfolio_return_since_lock": portfolio_return,
        "current_drawdown_since_lock": drawdown,
        "max_drawdown_since_lock": max_drawdown,
        "next_scheduled_rebalance_date": metadata[
            "next_scheduled_rebalance_date"
        ],
        "instruction": (
            "Do not change Wealthfront targets from this report. "
            "Use the locked target until the next scheduled monthly rebalance."
        ),
        "estimation_limitations": [
            "Estimated weights assume the locked target was filled exactly.",
            "The estimate excludes deposits, withdrawals, fees, taxes, and Wealthfront substitutions.",
            "Provide an actual-weights CSV to report observed drift instead.",
        ],
    }
    return MonitorResult(status=status, summary=summary, drift=drift, equity=equity)


def write_outputs(result: MonitorResult, output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    drift_path = output_dir / "v516_locked_target_drift.csv"
    equity_path = output_dir / "v516_since_lock_equity.csv"
    json_path = output_dir / "v516_midmonth_monitor.json"
    markdown_path = output_dir / "v516_midmonth_monitor.md"
    result.drift.to_csv(drift_path)
    result.equity.to_csv(equity_path)
    json_path.write_text(
        json.dumps(_json_safe(result.summary), indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )

    summary = result.summary
    valid_drift = result.drift.dropna(subset=["EstimatedCurrentWeight"])
    top_drift = valid_drift.reindex(
        valid_drift["EstimatedDriftPercentagePoints"].abs().sort_values(
            ascending=False
        ).index
    ).head(10)
    lines = [
        "# V5.16 Mid-Month Monitor",
        "",
        f"**Status: {result.status}**",
        "",
        "**Instruction: NO TRADE. Keep the locked monthly Wealthfront targets.**",
        "",
        f"- Official month: {summary['official_month']}",
        f"- Source market-close signal date: {summary['source_signal_date']}",
        f"- Allocation submitted date: {summary.get('allocation_submitted_date') or 'not recorded'}",
        f"- Live effective date: {summary['live_effective_date']}",
        f"- Latest common price date: {summary['latest_common_price_date']}",
        f"- Next scheduled rebalance: {summary['next_scheduled_rebalance_date']}",
        f"- Estimated return since lock: {_format_percent(summary['estimated_portfolio_return_since_lock'])}",
        f"- Current drawdown since lock: {_format_percent(summary['current_drawdown_since_lock'])}",
        f"- Maximum drawdown since lock: {_format_percent(summary['max_drawdown_since_lock'])}",
        f"- Maximum estimated weight drift: {_format_number(summary['max_absolute_drift_percentage_points'])} percentage points",
    ]
    if summary.get("data_error"):
        lines.append(f"- Data error: {summary['data_error']}")
    lines.extend(
        [
            "",
            "## Largest estimated drifts",
            "",
            "| Ticker | Locked target | Estimated weight | Drift (percentage points) |",
            "|---|---:|---:|---:|",
        ]
    )
    for ticker, row in top_drift.iterrows():
        lines.append(
            f"| {ticker} | {row['LockedTargetWeight']:.2%} | "
            f"{row['EstimatedCurrentWeight']:.2%} | "
            f"{row['EstimatedDriftPercentagePoints']:+.2f} |"
        )
    lines.extend(
        [
            "",
            "## How to use this report",
            "",
            "- `NORMAL_NO_TRADE`: everything is operating normally; take no action.",
            "- `PENDING_EFFECTIVE_DATE_NO_TRADE`: the submitted target is not effective yet; wait.",
            "- `REVIEW_DRIFT_NO_TRADE`: drift is notable, but wait for the monthly rebalance.",
            "- `STALE_DATA` or `DATA_ERROR`: do not trade; repair the data problem.",
            "- Market declines alone are not an emergency exit rule.",
            "",
            "This report never computes or publishes a new model target.",
        ]
    )
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "drift": drift_path,
        "equity": equity_path,
        "json": json_path,
        "markdown": markdown_path,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitor drift from the locked V5.16 monthly target without trading."
    )
    parser.add_argument("--lock-dir", type=Path, default=DEFAULT_LOCK_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--as-of", default="auto")
    parser.add_argument("--actual-weights-csv", type=Path)
    parser.add_argument("--prices-csv", type=Path)
    parser.add_argument("--drift-review-pp", type=float, default=2.0)
    parser.add_argument("--stale-calendar-days", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    weights = read_target_weights(args.lock_dir / "current_target.csv")
    metadata = json.loads(
        (args.lock_dir / "current_target.json").read_text(encoding="utf-8")
    )
    as_of = (
        pd.Timestamp(date.today())
        if args.as_of.lower() == "auto"
        else pd.Timestamp(args.as_of)
    )
    lock_date = pd.Timestamp(
        metadata.get("live_effective_date", metadata["rebalance_date"])
    )
    if as_of.normalize() < lock_date.normalize():
        prices = pd.DataFrame(columns=weights.index, dtype=float)
        download_error = None
    elif args.prices_csv:
        prices = pd.read_csv(args.prices_csv, parse_dates=["Date"]).set_index("Date")
        download_error = None
    else:
        cache_dir = args.output_dir / ".yfinance_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        yf.set_tz_cache_location(str(cache_dir))
        try:
            prices = download_prices(
                weights.index.tolist(), lock_date - pd.Timedelta(days=7), as_of
            )
            download_error = None
        except Exception as exc:
            prices = pd.DataFrame(columns=weights.index, dtype=float)
            download_error = f"{type(exc).__name__}: {exc}"
    result = build_monitor_result(
        weights,
        metadata,
        prices,
        as_of,
        actual_weights=read_actual_weights(args.actual_weights_csv),
        drift_review_percentage_points=args.drift_review_pp,
        stale_calendar_days=args.stale_calendar_days,
    )
    if download_error:
        result.summary["data_error"] = download_error
    paths = write_outputs(result, args.output_dir)
    print(json.dumps(result.summary, indent=2))
    print(f"\nMonitor report: {paths['markdown']}")


if __name__ == "__main__":
    main()
