from __future__ import annotations

from pathlib import Path
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

    if not weights_file.exists():
        latest = "missing"
    else:
        weights = pd.read_csv(weights_file, index_col=0)
        latest = str(pd.Timestamp(weights.index[-1]).date()) if not weights.empty else "empty"

    print(f"Latest rebalance date: {latest}")
    set_output("latest_rebalance_date", latest)


if __name__ == "__main__":
    main()