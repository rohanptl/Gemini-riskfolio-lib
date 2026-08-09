from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_OUTPUT_DIR = Path("outputs_option2_v5_16_score_tilted_cvar")
DEFAULT_LOCK_DIR = Path("live_targets/v516")


@dataclass(frozen=True)
class LockResult:
    changed: bool
    weights_path: Path
    metadata_path: Path
    rebalance_date: pd.Timestamp
    official_month: str


def read_target_weights(path: Path) -> pd.Series:
    frame = pd.read_csv(path)
    if "Weight" not in frame.columns:
        raise ValueError(f"Target file has no Weight column: {path}")
    ticker_column = "Ticker" if "Ticker" in frame.columns else frame.columns[0]
    tickers = frame[ticker_column].astype(str).str.strip().str.upper()
    weights = pd.to_numeric(frame["Weight"], errors="raise")
    result = pd.Series(weights.to_numpy(), index=tickers, name="Weight")
    result.index.name = "Ticker"
    result = result[result.abs() > 1e-12].sort_values(ascending=False)
    if result.index.has_duplicates:
        raise ValueError("Target file contains duplicate tickers.")
    if not np.isfinite(result.to_numpy()).all() or result.lt(0.0).any():
        raise ValueError("Target weights must be finite and nonnegative.")
    total = float(result.sum())
    if not 0.995 <= total <= 1.005:
        raise ValueError(f"Target weights sum to {total:.6f}, expected approximately 1.0.")
    return result


def latest_rebalance_date(path: Path) -> pd.Timestamp:
    frame = pd.read_csv(path, usecols=["Date"], parse_dates=["Date"])
    if frame.empty or frame["Date"].isna().all():
        raise ValueError(f"No rebalance dates found in {path}")
    return pd.Timestamp(frame["Date"].max()).normalize()


def _next_month_first_day(official_month: str) -> str:
    month = pd.Period(official_month, freq="M")
    return str((month + 1).start_time.date())


def _portable_source_path(path: Path) -> str:
    return path.name if path.is_absolute() else path.as_posix()


def _write_github_outputs(result: LockResult) -> None:
    github_output = os.environ.get("GITHUB_OUTPUT")
    if not github_output:
        return
    with Path(github_output).open("a", encoding="utf-8") as handle:
        handle.write(f"lock_changed={str(result.changed).lower()}\n")
        handle.write(f"official_month={result.official_month}\n")
        handle.write(f"rebalance_date={result.rebalance_date.date()}\n")


def lock_target(
    source_target_csv: Path,
    source_attribution_csv: Path,
    lock_dir: Path,
    *,
    replace_same_month: bool = False,
    source_commit: str = "",
    source_run_url: str = "",
    source_artifact: str = "",
    locked_at_utc: str | None = None,
    official_month_override: str | None = None,
    live_effective_date_override: str | None = None,
    allocation_submitted_date_override: str | None = None,
) -> LockResult:
    weights = read_target_weights(source_target_csv)
    rebalance_date = latest_rebalance_date(source_attribution_csv)
    official_month = official_month_override or rebalance_date.strftime("%Y-%m")
    official_period = pd.Period(official_month, freq="M")
    live_effective_date = (
        pd.Timestamp(live_effective_date_override).normalize()
        if live_effective_date_override
        else max(rebalance_date, official_period.start_time)
    )
    allocation_submitted_date = (
        pd.Timestamp(allocation_submitted_date_override).normalize()
        if allocation_submitted_date_override
        else None
    )
    rebalance_period = rebalance_date.to_period("M")
    if official_period not in {rebalance_period, rebalance_period + 1}:
        raise ValueError(
            "Official month must match the rebalance month or immediately follow "
            "a prior-month weekend/holiday close."
        )
    if live_effective_date.to_period("M") != official_period:
        raise ValueError("Live effective date must be within the official month.")
    if (
        allocation_submitted_date is not None
        and allocation_submitted_date > live_effective_date
    ):
        raise ValueError("Allocation submission date cannot follow its effective date.")
    current_weights_path = lock_dir / "current_target.csv"
    current_metadata_path = lock_dir / "current_target.json"

    if current_metadata_path.exists():
        current = json.loads(current_metadata_path.read_text(encoding="utf-8"))
        current_month = str(current["official_month"])
        if official_month < current_month:
            raise ValueError(
                f"Refusing to replace newer official month {current_month} "
                f"with {official_month}."
            )
        if official_month == current_month and not replace_same_month:
            result = LockResult(
                changed=False,
                weights_path=current_weights_path,
                metadata_path=current_metadata_path,
                rebalance_date=pd.Timestamp(current["rebalance_date"]),
                official_month=current_month,
            )
            _write_github_outputs(result)
            return result

    timestamp = locked_at_utc or datetime.now(timezone.utc).isoformat()
    metadata = {
        "strategy": "V5.16 Mom126Skip21",
        "purpose": "Official monthly live target; immutable during the month",
        "official_month": official_month,
        "source_signal_date": str(rebalance_date.date()),
        "rebalance_date": str(rebalance_date.date()),
        "allocation_submitted_date": (
            str(allocation_submitted_date.date())
            if allocation_submitted_date is not None
            else None
        ),
        "live_effective_date": str(live_effective_date.date()),
        "next_scheduled_rebalance_month": str(
            (pd.Period(official_month, freq="M") + 1)
        ),
        "next_scheduled_rebalance_date": _next_month_first_day(official_month),
        "locked_at_utc": timestamp,
        "holdings": int(len(weights)),
        "weight_sum": float(weights.sum()),
        "source_target_csv": _portable_source_path(source_target_csv),
        "source_attribution_csv": _portable_source_path(source_attribution_csv),
        "source_commit": source_commit,
        "source_run_url": source_run_url,
        "source_artifact": source_artifact,
        "monitor_policy": "NO_TRADE_MONITOR_ONLY until next scheduled rebalance",
    }
    history_dir = lock_dir / "history"
    history_weights_path = history_dir / f"target_{live_effective_date.date()}.csv"
    history_metadata_path = history_dir / f"target_{live_effective_date.date()}.json"
    if history_metadata_path.exists() and not replace_same_month:
        raise FileExistsError(
            f"Historical lock already exists: {history_metadata_path}"
        )

    lock_dir.mkdir(parents=True, exist_ok=True)
    history_dir.mkdir(parents=True, exist_ok=True)
    csv_text = weights.to_csv(header=True, lineterminator="\n")
    json_text = json.dumps(metadata, indent=2) + "\n"
    current_weights_path.write_text(csv_text, encoding="utf-8")
    current_metadata_path.write_text(json_text, encoding="utf-8")
    history_weights_path.write_text(csv_text, encoding="utf-8")
    history_metadata_path.write_text(json_text, encoding="utf-8")
    result = LockResult(
        changed=True,
        weights_path=current_weights_path,
        metadata_path=current_metadata_path,
        rebalance_date=rebalance_date,
        official_month=official_month,
    )
    _write_github_outputs(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Lock a V5.16 monthly target for monitor-only mid-month use."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--window", default="2023")
    parser.add_argument("--source-target-csv", type=Path)
    parser.add_argument("--source-attribution-csv", type=Path)
    parser.add_argument("--lock-dir", type=Path, default=DEFAULT_LOCK_DIR)
    parser.add_argument("--replace-same-month", action="store_true")
    parser.add_argument(
        "--official-month",
        help="Official YYYY-MM month; use this when a month starts on a non-trading day.",
    )
    parser.add_argument(
        "--live-effective-date",
        help="Date the target becomes effective in the live account (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--allocation-submitted-date",
        help="Date the target change was submitted to the live account (YYYY-MM-DD).",
    )
    parser.add_argument("--source-commit", default=os.environ.get("GITHUB_SHA", ""))
    parser.add_argument("--source-run-url", default="")
    parser.add_argument("--source-artifact", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    window_dir = args.output_dir / "walk_forward_windows" / str(args.window)
    target_csv = args.source_target_csv or (
        window_dir / "final_target_weights_tradeable.csv"
    )
    attribution_csv = args.source_attribution_csv or (
        window_dir / "allocation_attribution_by_rebalance.csv"
    )
    result = lock_target(
        target_csv,
        attribution_csv,
        args.lock_dir,
        replace_same_month=args.replace_same_month,
        source_commit=args.source_commit,
        source_run_url=args.source_run_url,
        source_artifact=args.source_artifact,
        official_month_override=args.official_month,
        live_effective_date_override=args.live_effective_date,
        allocation_submitted_date_override=args.allocation_submitted_date,
    )
    action = "Updated" if result.changed else "Kept existing"
    print(
        f"{action} official {result.official_month} target from "
        f"rebalance {result.rebalance_date.date()}: {result.weights_path}"
    )


if __name__ == "__main__":
    main()
