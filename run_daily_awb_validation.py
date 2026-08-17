from __future__ import annotations

import argparse
from pathlib import Path

from awb_sleeves.validation import ValidationPaths, run_historical_validation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Daily AWB historical robustness validation suite."
    )
    parser.add_argument(
        "--experiment-dir",
        type=Path,
        default=Path("outputs_experiment_oversold_reversal_sleeve_v7_causal_validation"),
    )
    parser.add_argument(
        "--market-data-cache",
        type=Path,
        default=Path("outputs_experiment_market_data_cache/adjusted_ohlcv.pkl"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs_experiment_daily_awb_historical_validation"),
    )
    parser.add_argument("--bootstrap-samples", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    gates, report = run_historical_validation(
        ValidationPaths(
            experiment_dir=args.experiment_dir,
            market_data_cache=args.market_data_cache,
            output_dir=args.output_dir,
        ),
        bootstrap_samples=args.bootstrap_samples,
        seed=args.seed,
    )
    print(gates.to_string(index=False))
    print(f"\nReport written to {report}")


if __name__ == "__main__":
    main()
