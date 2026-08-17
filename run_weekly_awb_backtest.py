from __future__ import annotations

import argparse
from pathlib import Path
from time import perf_counter

from awb_sleeves.backtest import run_weekly_awb_backtest
from awb_sleeves.config import DataConfig, ExecutionConfig, WeeklyAWBConfig
from awb_sleeves.data import load_baseline_returns, load_market_data, load_risk_universe
from awb_sleeves.indicators import build_feature_sets
from awb_sleeves.reporting import trade_summary, write_outputs
from awb_sleeves.strategies.weekly_awb import build_signal_table
from awb_sleeves.visuals import generate_visuals


DEFAULT_OUTPUT_DIR = Path("outputs_experiment_weekly_awb_sleeve_v1")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backtest the universe-wide Weekly AWB Sleeve independently."
    )
    parser.add_argument("--start-date", default="2019-01-01")
    parser.add_argument("--end-date", default="2026-08-09")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--market-data-cache",
        type=Path,
        default=Path("outputs_experiment_market_data_cache/adjusted_ohlcv.pkl"),
    )
    parser.add_argument(
        "--baseline-csv",
        type=Path,
        default=Path(
            "outputs_milestone_prod_mom126_skip21"
            "/walk_forward_windows/2020/portfolio_backtest.csv"
        ),
    )
    parser.add_argument("--refresh-data", action="store_true")
    parser.add_argument("--no-visuals", action="store_true")
    parser.add_argument("--overlay-weight", type=float, default=0.05)
    parser.add_argument("--max-holding-days", type=int, default=90)
    parser.add_argument("--cost-bps", type=float, default=10.0)
    parser.add_argument(
        "--initial-stop-atr",
        type=float,
        default=None,
        help="Optional immediately active initial-loss stop in daily ATR units.",
    )
    parser.add_argument(
        "--replacement-min-holding-days",
        type=int,
        default=None,
        help="Allow a new weekly candidate to replace a stale holding after this age.",
    )
    return parser.parse_args()


def main() -> None:
    started = perf_counter()
    args = parse_args()
    data_config = DataConfig(
        start_date=args.start_date,
        end_date=args.end_date,
        market_data_cache=args.market_data_cache,
        baseline_csv=args.baseline_csv,
    )
    execution_config = ExecutionConfig(
        overlay_weight=args.overlay_weight,
        cost_bps_per_side=args.cost_bps,
        max_holding_days=args.max_holding_days,
        initial_stop_atr_multiple=args.initial_stop_atr,
        replacement_min_holding_days=args.replacement_min_holding_days,
    )
    strategy_config = WeeklyAWBConfig()

    tickers = load_risk_universe(data_config.universe_csv)
    market_data, source = load_market_data(
        data_config, tickers, refresh=args.refresh_data
    )
    print(f"Loaded {len(market_data)} risk ETFs from {source}.")
    daily_features, weekly_features = build_feature_sets(
        market_data, strategy_config
    )
    signal_table = build_signal_table(weekly_features, strategy_config)
    baseline_returns = load_baseline_returns(data_config)
    result = run_weekly_awb_backtest(
        daily_features=daily_features,
        signal_table=signal_table,
        baseline_returns=baseline_returns,
        execution=execution_config,
        strategy=strategy_config,
    )
    stats = write_outputs(
        args.output_dir,
        result.daily,
        result.trades,
        result.candidates,
        signal_table,
    )
    written_daily = result.daily.copy()
    written_daily["BaselineEquity"] = (
        1.0 + written_daily["BaselineReturn"]
    ).cumprod()
    written_daily["OverlayEquity"] = (
        1.0 + written_daily["OverlayReturn"]
    ).cumprod()
    written_daily["BaselineDrawdown"] = (
        written_daily["BaselineEquity"]
        / written_daily["BaselineEquity"].cummax()
        - 1.0
    )
    written_daily["OverlayDrawdown"] = (
        written_daily["OverlayEquity"]
        / written_daily["OverlayEquity"].cummax()
        - 1.0
    )
    if not args.no_visuals:
        generate_visuals(written_daily, result.trades, args.output_dir)

    print("\nPerformance summary:")
    print(stats[["CAGR", "Sharpe", "MaxDrawdown", "MAR", "Sortino"]])
    print("\nTrade summary:")
    print(trade_summary(result.trades).to_string(index=False))
    print(f"\nOutputs written to {args.output_dir}")
    print(f"Total runtime: {perf_counter() - started:.1f}s")


if __name__ == "__main__":
    main()
