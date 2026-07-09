from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import os

import pandas as pd


def set_output(name: str, value: str) -> None:
    github_output = Path(os.environ["GITHUB_OUTPUT"])
    with github_output.open("a", encoding="utf-8") as fh:
        fh.write(f"{name}={value}\n")


def main() -> None:
    weights_file = Path(
        "outputs_option2_v5_16_score_tilted_cvar/"
        "walk_forward_windows/2023/weights_by_rebalance.csv"
    )

    now_ny = datetime.now(ZoneInfo("America/New_York")).date()
    set_output("run_month", now_ny.strftime("%Y-%m"))

    if not weights_file.exists():
        print(f"::warning::Missing {weights_file}")
        set_output("current_month_rebalance", "false")
        set_output("latest_rebalance_date", "missing")
        return

    weights = pd.read_csv(weights_file, index_col=0)
    if weights.empty:
        print(f"::warning::{weights_file} is empty")
        set_output("current_month_rebalance", "false")
        set_output("latest_rebalance_date", "empty")
        return

    latest_rebalance = pd.Timestamp(weights.index[-1]).date()

    is_current_month = (
        latest_rebalance.year == now_ny.year
        and latest_rebalance.month == now_ny.month
    )

    print(f"Latest rebalance date: {latest_rebalance}")
    print(f"Current New York date: {now_ny}")
    print(f"Current-month rebalance found: {is_current_month}")

    set_output("current_month_rebalance", "true" if is_current_month else "false")
    set_output("latest_rebalance_date", latest_rebalance.isoformat())


if __name__ == "__main__":
    main()
