from __future__ import annotations

import argparse
from pathlib import Path
from time import perf_counter

from awb_sleeves.backtest import run_weekly_awb_strategy
from awb_sleeves.config import DataConfig, StandalonePortfolioConfig, WeeklyAWBConfig
from awb_sleeves.data import load_baseline_returns, load_market_data, load_risk_universe
from awb_sleeves.indicators import build_feature_sets
from awb_sleeves.reporting import trade_summary, write_strategy_outputs
from awb_sleeves.strategies.weekly_awb import build_signal_table
from awb_sleeves.visuals import generate_strategy_visuals


BENCHMARKS = ["SPY", "QQQ", "VTI"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backtest Weekly AWB as an independent multi-position strategy."
    )
    parser.add_argument("--start-date", default="2019-01-01")
    parser.add_argument("--end-date", default="2026-08-09")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs_experiment_weekly_awb_strategy_v1_max3"),
    )
    parser.add_argument("--max-positions", type=int, default=3)
    parser.add_argument("--max-holding-days", type=int, default=90)
    parser.add_argument("--cost-bps", type=float, default=10.0)
    parser.add_argument("--initial-stop-atr", type=float, default=3.0)
    parser.add_argument("--refresh-data", action="store_true")
    parser.add_argument("--no-visuals", action="store_true")
    return parser.parse_args()


def main() -> None:
    started = perf_counter()
    args = parse_args()
    if args.max_positions < 1:
        raise ValueError("--max-positions must be at least 1")
    data_config = DataConfig(start_date=args.start_date, end_date=args.end_date)
    strategy_config = WeeklyAWBConfig()
    execution_config = StandalonePortfolioConfig(
        max_positions=args.max_positions,
        max_holding_days=args.max_holding_days,
        cost_bps_per_side=args.cost_bps,
        initial_stop_atr_multiple=args.initial_stop_atr,
    )

    risk_tickers = load_risk_universe(data_config.universe_csv)
    requested = sorted(set(risk_tickers + BENCHMARKS))
    market_data, source = load_market_data(
        data_config, requested, refresh=args.refresh_data
    )
    print(f"Loaded {len(market_data)} ETFs from {source}.")
    daily_features, weekly_features = build_feature_sets(
        market_data, strategy_config
    )
    risk_weekly = {
        ticker: weekly_features[ticker]
        for ticker in risk_tickers
        if ticker in weekly_features
    }
    signal_table = build_signal_table(risk_weekly, strategy_config)
    production_returns = load_baseline_returns(data_config)
    calendar = production_returns.index.intersection(
        next(iter(daily_features.values())).index
    )
    result = run_weekly_awb_strategy(
        daily_features=daily_features,
        signal_table=signal_table,
        calendar=calendar,
        execution=execution_config,
        strategy=strategy_config,
    )
    benchmarks = {"ProductionBaseline": production_returns}
    for ticker in BENCHMARKS:
        if ticker in daily_features:
            benchmarks[ticker] = daily_features[ticker]["Close"].pct_change()
    stats, output_daily = write_strategy_outputs(
        args.output_dir,
        result.daily,
        result.trades,
        result.candidates,
        benchmarks,
    )
    if not args.no_visuals:
        generate_strategy_visuals(
            output_daily,
            result.trades,
            ["WeeklyAWBStrategy", *benchmarks.keys()],
            args.output_dir,
        )

    print("\nPerformance summary:")
    print(stats[["CAGR", "Sharpe", "MaxDrawdown", "MAR", "Sortino"]])
    print("\nTrade summary:")
    print(trade_summary(result.trades).to_string(index=False))
    print(f"\nOutputs written to {args.output_dir}")
    print(f"Total runtime: {perf_counter() - started:.1f}s")


if __name__ == "__main__":
    main()
