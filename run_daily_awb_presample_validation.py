from __future__ import annotations

import argparse
from pathlib import Path

from awb_sleeves.presample import PreSampleConfig, run_presample_validation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply the frozen causal Daily AWB rules to pre-2020 data."
    )
    parser.add_argument("--data-start", default="2005-01-01")
    parser.add_argument("--evaluation-start", default="2007-01-01")
    parser.add_argument("--evaluation-end", default="2020-10-08")
    parser.add_argument(
        "--market-cache",
        type=Path,
        default=Path(
            "outputs_experiment_market_data_cache/adjusted_ohlcv_pre2020.pkl"
        ),
    )
    parser.add_argument(
        "--indicator-cache",
        type=Path,
        default=Path(
            "outputs_experiment_market_data_cache/indicators_pre2020.pkl"
        ),
    )
    parser.add_argument(
        "--current-market-cache",
        type=Path,
        default=Path("outputs_experiment_market_data_cache/adjusted_ohlcv.pkl"),
    )
    parser.add_argument(
        "--current-experiment-dir",
        type=Path,
        default=Path(
            "outputs_experiment_oversold_reversal_sleeve_v7_causal_validation"
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs_experiment_daily_awb_presample_validation"),
    )
    parser.add_argument("--bootstrap-samples", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--refresh-data", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    gates, report = run_presample_validation(
        PreSampleConfig(
            data_start=args.data_start,
            evaluation_start=args.evaluation_start,
            evaluation_end=args.evaluation_end,
            market_cache=args.market_cache,
            indicator_cache=args.indicator_cache,
            current_market_cache=args.current_market_cache,
            current_experiment_dir=args.current_experiment_dir,
            output_dir=args.output_dir,
            refresh_data=args.refresh_data,
            bootstrap_samples=args.bootstrap_samples,
            seed=args.seed,
        )
    )
    print(gates.to_string(index=False))
    print(f"\nReport written to {report}")


if __name__ == "__main__":
    main()
