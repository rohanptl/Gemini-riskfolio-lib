from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

import main_option2_all_etfs_v5_16_rolling_asof_monthly_attribution_dynamic_enddate as production
from experiment_oversold_reversal_sleeve import calculate_indicators


SELECTED_NAME = "TwoStageATR125Profit3Trail30"
SELECTED_SLUG = SELECTED_NAME.lower()
CONTROL_SLUG = "twostagequality10risk20datr125"


@dataclass(frozen=True)
class ValidationPaths:
    experiment_dir: Path
    market_data_cache: Path
    output_dir: Path


def load_daily_output(experiment_dir: Path, slug: str) -> pd.DataFrame:
    path = experiment_dir / f"daily_returns_{slug}.csv"
    return pd.read_csv(path, parse_dates=["Date"]).set_index("Date").sort_index()


def load_signal_log(experiment_dir: Path, slug: str) -> pd.DataFrame:
    path = experiment_dir / f"signal_log_{slug}.csv"
    return pd.read_csv(path, parse_dates=["Date"]).sort_values("Date")


def performance_delta(
    candidate: pd.Series, baseline: pd.Series, label: str
) -> dict[str, float | str | int]:
    candidate = candidate.dropna()
    baseline = baseline.reindex(candidate.index).dropna()
    candidate = candidate.reindex(baseline.index)
    candidate_stats = production.performance_stats(candidate, label)
    baseline_stats = production.performance_stats(baseline, "Baseline")
    return {
        "Period": label,
        "Observations": len(candidate),
        "CandidateCAGR": candidate_stats["CAGR"],
        "BaselineCAGR": baseline_stats["CAGR"],
        "DeltaCAGR": candidate_stats["CAGR"] - baseline_stats["CAGR"],
        "CandidateSharpe": candidate_stats["Sharpe"],
        "BaselineSharpe": baseline_stats["Sharpe"],
        "DeltaSharpe": candidate_stats["Sharpe"] - baseline_stats["Sharpe"],
        "CandidateMaxDrawdown": candidate_stats["Max Drawdown"],
        "BaselineMaxDrawdown": baseline_stats["Max Drawdown"],
        "DeltaMaxDrawdown": (
            candidate_stats["Max Drawdown"] - baseline_stats["Max Drawdown"]
        ),
    }


def parameter_sensitivity(experiment_dir: Path) -> pd.DataFrame:
    summary = pd.read_csv(experiment_dir / "variant_summary.csv")
    result = summary[
        summary["Name"].str.startswith("TwoStageATR125Profit")
    ].copy()
    columns = [
        "Name",
        "CAGR",
        "Sharpe",
        "Max Drawdown",
        "MAR",
        "Sortino",
        "DeltaCAGRVsBaseline",
        "DeltaSharpeVsBaseline",
        "DeltaMaxDrawdownVsBaseline",
    ]
    return result[columns].sort_values("CAGR", ascending=False)


def subperiod_performance(daily: pd.DataFrame) -> pd.DataFrame:
    periods = [
        ("2020-2022", "2020-10-08", "2022-12-31"),
        ("2023-2024", "2023-01-01", "2024-12-31"),
        ("2025", "2025-01-01", "2025-12-31"),
        ("2026 YTD", "2026-01-01", "2026-12-31"),
    ]
    rows = []
    for label, start, end in periods:
        window = daily.loc[start:end]
        if not window.empty:
            rows.append(
                performance_delta(
                    window["NetCombinedReturn"], window["BaselineReturn"], label
                )
            )
    return pd.DataFrame(rows)


def cost_sensitivity(daily: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cost_bps in [0.0, 10.0, 25.0, 50.0, 100.0]:
        candidate = (
            daily["GrossCombinedReturn"]
            - daily["Turnover"] * cost_bps / 10_000.0
        )
        row = performance_delta(
            candidate, daily["BaselineReturn"], f"{cost_bps:g} bps"
        )
        row["CostBpsPerSide"] = cost_bps
        rows.append(row)
    return pd.DataFrame(rows)


def walk_forward_parameter_selection(experiment_dir: Path) -> pd.DataFrame:
    files = sorted(experiment_dir.glob("daily_returns_twostageatr125profit*.csv"))
    variants = {
        path.stem.removeprefix("daily_returns_"): pd.read_csv(
            path, parse_dates=["Date"]
        ).set_index("Date")["NetCombinedReturn"]
        for path in files
    }
    if not variants:
        return pd.DataFrame()
    first = pd.read_csv(files[0], parse_dates=["Date"]).set_index("Date")
    baseline = first["BaselineReturn"]
    rows = []
    for year in range(2023, int(baseline.index.year.max()) + 1):
        training_end = pd.Timestamp(year=year - 1, month=12, day=31)
        training_scores = {
            name: production.performance_stats(series.loc[:training_end], name)[
                "Sharpe"
            ]
            for name, series in variants.items()
        }
        chosen = max(training_scores, key=training_scores.get)
        test = variants[chosen][variants[chosen].index.year == year]
        benchmark = baseline[baseline.index.year == year]
        if test.empty:
            continue
        rows.append(
            {
                "TestYear": year,
                "ChosenVariant": chosen,
                "TrainingSharpe": training_scores[chosen],
                "CandidateReturn": float((1.0 + test).prod() - 1.0),
                "BaselineReturn": float((1.0 + benchmark).prod() - 1.0),
                "ExcessReturn": float(
                    (1.0 + test).prod() - (1.0 + benchmark).prod()
                ),
            }
        )
    return pd.DataFrame(rows)


def market_frames(market_data_cache: Path) -> dict[str, pd.DataFrame]:
    market = pd.read_pickle(market_data_cache).copy()
    market["Date"] = pd.to_datetime(market["Date"])
    return {
        ticker: frame.set_index("Date").sort_index()
        for ticker, frame in market.groupby("Ticker")
    }


def _next_location(frame: pd.DataFrame, date: pd.Timestamp) -> int | None:
    location = int(frame.index.searchsorted(date, side="right"))
    return location if location < len(frame) else None


def next_open_trade_ledger(
    signal_log: pd.DataFrame,
    frames: dict[str, pd.DataFrame],
    cost_bps_per_side: float = 10.0,
) -> pd.DataFrame:
    open_positions: dict[str, pd.Timestamp] = {}
    rows: list[dict[str, object]] = []
    cost_rate = cost_bps_per_side / 10_000.0
    spy = frames["SPY"]

    def close_trade(
        ticker: str,
        entry_signal: pd.Timestamp,
        exit_signal: pd.Timestamp | None,
        reason: str,
    ) -> None:
        frame = frames[ticker]
        entry_location = _next_location(frame, entry_signal)
        if entry_location is None:
            return
        entry_date = frame.index[entry_location]
        entry_open = float(frame.iloc[entry_location]["Open"])
        exit_location = (
            _next_location(frame, exit_signal)
            if exit_signal is not None
            else None
        )
        if exit_signal is not None and exit_location is not None:
            exit_date = frame.index[exit_location]
            exit_price = float(frame.iloc[exit_location]["Open"])
            status = "Closed"
        else:
            exit_date = frame.index[-1]
            exit_price = float(frame.iloc[-1]["Close"])
            status = "Open" if exit_signal is None else "Marked"

        spy_entry_location = int(spy.index.searchsorted(entry_date))
        spy_exit_location = int(spy.index.searchsorted(exit_date))
        spy_entry = float(spy.iloc[spy_entry_location]["Open"])
        spy_exit = float(
            spy.iloc[spy_exit_location]["Open"]
            if status == "Closed"
            else spy.iloc[spy_exit_location]["Close"]
        )
        gross_return = exit_price / entry_open - 1.0
        net_return = (
            (1.0 - cost_rate) * exit_price
            / ((1.0 + cost_rate) * entry_open)
            - 1.0
        )
        spy_return = spy_exit / spy_entry - 1.0
        rows.append(
            {
                "Ticker": ticker,
                "EntrySignalDate": entry_signal,
                "EntryDate": entry_date,
                "EntryOpen": entry_open,
                "ExitSignalDate": exit_signal,
                "ExitDate": exit_date,
                "ExitPrice": exit_price,
                "ExitReason": reason,
                "Status": status,
                "GrossReturn": gross_return,
                "NetReturn": net_return,
                "SPYReturn": spy_return,
                "ExcessReturnVsSPY": net_return - spy_return,
            }
        )

    for event in signal_log.itertuples(index=False):
        if event.Action == "Enter":
            open_positions[str(event.Ticker)] = pd.Timestamp(event.Date)
        elif event.Action == "Exit" and event.Ticker in open_positions:
            close_trade(
                str(event.Ticker),
                open_positions.pop(str(event.Ticker)),
                pd.Timestamp(event.Date),
                str(event.ExitReason),
            )
    for ticker, entry_signal in open_positions.items():
        close_trade(ticker, entry_signal, None, "OpenMark")
    return pd.DataFrame(rows).sort_values("EntrySignalDate")


def bootstrap_trade_excess(
    ledger: pd.DataFrame, samples: int, seed: int
) -> pd.DataFrame:
    closed = ledger[ledger["Status"].eq("Closed")]
    values = closed["ExcessReturnVsSPY"].dropna().to_numpy(dtype=float)
    rng = np.random.default_rng(seed)
    draws = rng.choice(values, size=(samples, len(values)), replace=True).mean(axis=1)
    return pd.DataFrame(
        [
            {
                "ClosedTrades": len(values),
                "ObservedMeanExcess": float(values.mean()),
                "BootstrapSamples": samples,
                "ProbabilityMeanExcessPositive": float((draws > 0.0).mean()),
                "Lower95MeanExcess": float(np.quantile(draws, 0.025)),
                "MedianMeanExcess": float(np.quantile(draws, 0.5)),
                "Upper95MeanExcess": float(np.quantile(draws, 0.975)),
            }
        ]
    )


def leave_one_ticker_out(ledger: pd.DataFrame) -> pd.DataFrame:
    closed = ledger[ledger["Status"].eq("Closed")]
    rows = []
    for ticker in sorted(closed["Ticker"].unique()):
        remaining = closed[closed["Ticker"].ne(ticker)]
        rows.append(
            {
                "ExcludedTicker": ticker,
                "RemainingTrades": len(remaining),
                "MeanNetReturn": remaining["NetReturn"].mean(),
                "MeanExcessReturnVsSPY": remaining["ExcessReturnVsSPY"].mean(),
                "PositiveReturnRate": remaining["NetReturn"].gt(0.0).mean(),
                "BeatSPYRate": remaining["ExcessReturnVsSPY"].gt(0.0).mean(),
            }
        )
    return pd.DataFrame(rows)


KNOWN_CASES = [
    ("XHB", "2026-04-08", "Early XHB observation"),
    ("XHB", "2026-04-17", "Confirmed XHB entry"),
    ("XHB", "2026-05-21", "Second XHB observation"),
    ("GNR", "2026-07-13", "Early GNR observation"),
    ("GNR", "2026-07-21", "Former non-causal GNR entry"),
    ("GLD", "2026-07-24", "Late-July GLD observation"),
    ("GLD", "2026-07-31", "Month-end GLD observation"),
    ("GLDM", "2026-08-05", "Confirmed gold-proxy entry"),
]


def _condition_map(row: pd.Series, previous_rsi: float) -> dict[str, bool]:
    return {
        "watch_age_1_10": 1.0 <= row["WashoutWatchAge"] <= 10.0,
        "rsi_cross_50": row["RSI14"] > 50.0 and previous_rsi <= 50.0,
        "rsi_55_64": 55.0 <= row["RSI14"] <= 64.0,
        "close_gt_ema20": row["Close"] > row["EMA20"],
        "macd_hist_positive": row["MACDHist"] > 0.0,
        "breakout_20d": row["Close"] > row["Prior20High"],
        "weekly_rsi_35_52": 35.0 <= row["WeeklyRSI14"] <= 52.0,
        "weekly_macd_improving": row["WeeklyMACDHistDelta1"] > 0.0,
        "return5_nonnegative": row["Return5"] >= 0.0,
        "five_day_move_atr_le_1_25": row["FiveDayMoveATR14"] <= 1.25,
        "liquid": row["DollarVolume20"] >= 10_000_000.0,
    }


def known_case_and_asof_checks(
    frames: dict[str, pd.DataFrame], signal_log: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    cases = list(KNOWN_CASES)
    cases.extend(
        (str(row.Ticker), str(pd.Timestamp(row.Date).date()), "Selected entry")
        for row in signal_log[signal_log["Action"].eq("Enter")].itertuples(index=False)
    )
    diagnostics = []
    invariance = []
    indicator_cache: dict[str, pd.DataFrame] = {}
    for ticker, date_text, description in cases:
        date = pd.Timestamp(date_text)
        frame = frames.get(ticker)
        if frame is None or date not in frame.index:
            continue
        if ticker not in indicator_cache:
            indicator_cache[ticker] = calculate_indicators(
                frame[["Open", "High", "Low", "Close", "Volume"]]
            )
        full = indicator_cache[ticker]
        truncated = calculate_indicators(
            frame.loc[:date, ["Open", "High", "Low", "Close", "Volume"]]
        )
        row = full.loc[date]
        truncated_row = truncated.loc[date]
        conditions = _condition_map(row, float(full["RSI14"].shift(1).loc[date]))
        diagnostics.append(
            {
                "Ticker": ticker,
                "Date": date,
                "Description": description,
                "Signal": bool(row["SignalTwoStageQuality10ATR125"]),
                "Close": row["Close"],
                "RSI14": row["RSI14"],
                "WashoutWatchAge": row["WashoutWatchAge"],
                "Return5": row["Return5"],
                "FiveDayMoveATR14": row["FiveDayMoveATR14"],
                "WeeklyRSI14": row["WeeklyRSI14"],
                "WeeklyMACDHistDelta1": row["WeeklyMACDHistDelta1"],
                "FailedConditions": "; ".join(
                    name for name, passed in conditions.items() if not passed
                ),
            }
        )
        columns = [
            "WeeklyRSI14",
            "WeeklyMACDHist",
            "WeeklyMACDHistDelta1",
            "WeeklyCMF20",
            "WeeklySMA40",
        ]
        differences = {
            column: abs(float(row[column]) - float(truncated_row[column]))
            for column in columns
            if pd.notna(row[column]) and pd.notna(truncated_row[column])
        }
        invariance.append(
            {
                "Ticker": ticker,
                "Date": date,
                "Description": description,
                "FullSignal": bool(row["SignalTwoStageQuality10ATR125"]),
                "AsOfSignal": bool(
                    truncated_row["SignalTwoStageQuality10ATR125"]
                ),
                "SignalMatches": bool(
                    row["SignalTwoStageQuality10ATR125"]
                    == truncated_row["SignalTwoStageQuality10ATR125"]
                ),
                "MaxWeeklyFeatureDifference": max(differences.values(), default=0.0),
            }
        )
    return (
        pd.DataFrame(diagnostics).drop_duplicates(["Ticker", "Date", "Description"]),
        pd.DataFrame(invariance).drop_duplicates(["Ticker", "Date", "Description"]),
    )


def validation_gates(
    parameter: pd.DataFrame,
    subperiod: pd.DataFrame,
    costs: pd.DataFrame,
    walk_forward: pd.DataFrame,
    ledger: pd.DataFrame,
    bootstrap: pd.DataFrame,
    leave_one_out: pd.DataFrame,
    invariance: pd.DataFrame,
    full_period: dict[str, object],
) -> pd.DataFrame:
    closed = ledger[ledger["Status"].eq("Closed")]
    gates = [
        (
            "Full-period improvement",
            full_period["DeltaCAGR"] > 0.0 and full_period["DeltaSharpe"] > 0.0,
            f"CAGR delta {full_period['DeltaCAGR']:.2%}; Sharpe delta {full_period['DeltaSharpe']:.3f}",
        ),
        (
            "Parameter neighborhood",
            parameter["DeltaCAGRVsBaseline"].gt(0.0).mean() >= 0.8,
            f"{parameter['DeltaCAGRVsBaseline'].gt(0.0).sum()}/{len(parameter)} nearby exits improved CAGR",
        ),
        (
            "Subperiod consistency",
            subperiod["DeltaCAGR"].gt(0.0).mean() >= 0.75,
            f"{subperiod['DeltaCAGR'].gt(0.0).sum()}/{len(subperiod)} periods improved CAGR",
        ),
        (
            "50 bps cost stress",
            float(costs.loc[costs["CostBpsPerSide"].eq(50.0), "DeltaCAGR"].iloc[0]) > 0.0,
            "Requires positive CAGR delta at five times the modeled cost",
        ),
        (
            "Walk-forward parameter choice",
            walk_forward["ExcessReturn"].gt(0.0).mean() >= 0.75,
            f"{walk_forward['ExcessReturn'].gt(0.0).sum()}/{len(walk_forward)} test years beat baseline",
        ),
        (
            "Next-open trade excess",
            closed["ExcessReturnVsSPY"].mean() > 0.0,
            f"Mean closed-trade excess vs SPY {closed['ExcessReturnVsSPY'].mean():.2%}",
        ),
        (
            "Bootstrap confidence",
            float(bootstrap.iloc[0]["Lower95MeanExcess"]) > 0.0,
            f"95% interval lower bound {bootstrap.iloc[0]['Lower95MeanExcess']:.2%}",
        ),
        (
            "Ticker concentration",
            leave_one_out["MeanExcessReturnVsSPY"].min() > 0.0,
            f"Worst leave-one-ticker-out mean excess {leave_one_out['MeanExcessReturnVsSPY'].min():.2%}",
        ),
        (
            "As-of reproducibility",
            invariance["SignalMatches"].all()
            and invariance["MaxWeeklyFeatureDifference"].max() < 1e-10,
            f"{int((~invariance['SignalMatches']).sum())} signal mismatches; max feature difference {invariance['MaxWeeklyFeatureDifference'].max():.3g}",
        ),
        (
            "Minimum closed sample",
            len(closed) >= 30,
            f"{len(closed)} closed trades; target is at least 30",
        ),
    ]
    return pd.DataFrame(
        [
            {"Gate": name, "Passed": bool(passed), "Evidence": evidence}
            for name, passed, evidence in gates
        ]
    )


def write_report(
    output_dir: Path,
    full_period: dict[str, object],
    gates: pd.DataFrame,
    parameter: pd.DataFrame,
    subperiod: pd.DataFrame,
    costs: pd.DataFrame,
    walk_forward: pd.DataFrame,
    ledger: pd.DataFrame,
    bootstrap: pd.DataFrame,
) -> Path:
    passed = int(gates["Passed"].sum())
    total = len(gates)
    closed = ledger[ledger["Status"].eq("Closed")]
    overall = "NOT READY FOR 10% PRODUCTION" if passed < total else "READY"
    lines = [
        "# Daily AWB Historical Robustness Validation",
        "",
        f"**Decision: {overall} ({passed}/{total} gates passed).**",
        "",
        "The selected candidate uses causal week-to-date features, a 3% profit activation, "
        "a 3.0 ATR trailing stop with an entry-price floor, close-of-day signals, and "
        "next-session-open trade validation.",
        "",
        "## Full-period overlay result",
        "",
        f"- Candidate CAGR: {full_period['CandidateCAGR']:.2%}",
        f"- Baseline CAGR: {full_period['BaselineCAGR']:.2%}",
        f"- CAGR improvement: {full_period['DeltaCAGR']:.2%}",
        f"- Sharpe improvement: {full_period['DeltaSharpe']:.3f}",
        f"- Max-drawdown improvement: {full_period['DeltaMaxDrawdown']:.2%}",
        "",
        "## Next-open trade evidence",
        "",
        f"- Closed trades: {len(closed)}",
        f"- Win rate: {closed['NetReturn'].gt(0.0).mean():.1%}",
        f"- Mean net trade return: {closed['NetReturn'].mean():.2%}",
        f"- Mean excess return versus SPY: {closed['ExcessReturnVsSPY'].mean():.2%}",
        f"- Beat-SPY rate: {closed['ExcessReturnVsSPY'].gt(0.0).mean():.1%}",
        f"- Bootstrap probability mean excess is positive: {bootstrap.iloc[0]['ProbabilityMeanExcessPositive']:.1%}",
        f"- Bootstrap 95% interval: {bootstrap.iloc[0]['Lower95MeanExcess']:.2%} to {bootstrap.iloc[0]['Upper95MeanExcess']:.2%}",
        "",
        "## Validation gates",
        "",
        "| Gate | Result | Evidence |",
        "|---|---:|---|",
    ]
    for row in gates.itertuples(index=False):
        lines.append(
            f"| {row.Gate} | {'PASS' if row.Passed else 'FAIL'} | {row.Evidence} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The causal correction removed historical entries that would not have appeared "
            "in an as-of live run. The corrected candidate still improves the aggregate "
            "backtest and survives parameter, cost, and ticker-concentration checks. "
            "However, the closed-trade sample remains too small and the bootstrap interval "
            "still includes zero. Treat the result as promising research, not established alpha.",
            "",
            "Detailed CSV files in this directory contain parameter, subperiod, cost, "
            "walk-forward, trade, bootstrap, concentration, known-case, and as-of checks.",
        ]
    )
    path = output_dir / "historical_validation_report.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_historical_validation(
    paths: ValidationPaths, bootstrap_samples: int = 20_000, seed: int = 42
) -> tuple[pd.DataFrame, Path]:
    paths.output_dir.mkdir(parents=True, exist_ok=True)
    selected = load_daily_output(paths.experiment_dir, SELECTED_SLUG)
    parameter = parameter_sensitivity(paths.experiment_dir)
    subperiod = subperiod_performance(selected)
    costs = cost_sensitivity(selected)
    walk_forward = walk_forward_parameter_selection(paths.experiment_dir)
    frames = market_frames(paths.market_data_cache)
    selected_log = load_signal_log(paths.experiment_dir, SELECTED_SLUG)
    ledger = next_open_trade_ledger(selected_log, frames)
    bootstrap = bootstrap_trade_excess(ledger, bootstrap_samples, seed)
    concentration = leave_one_ticker_out(ledger)
    diagnostics, invariance = known_case_and_asof_checks(frames, selected_log)
    full_period = performance_delta(
        selected["NetCombinedReturn"], selected["BaselineReturn"], "Full Period"
    )
    gates = validation_gates(
        parameter,
        subperiod,
        costs,
        walk_forward,
        ledger,
        bootstrap,
        concentration,
        invariance,
        full_period,
    )

    outputs = {
        "validation_gates.csv": gates,
        "parameter_sensitivity.csv": parameter,
        "subperiod_performance.csv": subperiod,
        "cost_sensitivity.csv": costs,
        "walk_forward_parameter_selection.csv": walk_forward,
        "next_open_trade_ledger.csv": ledger,
        "bootstrap_summary.csv": bootstrap,
        "leave_one_ticker_out.csv": concentration,
        "known_case_diagnostics.csv": diagnostics,
        "asof_invariance.csv": invariance,
    }
    for filename, frame in outputs.items():
        frame.to_csv(paths.output_dir / filename, index=False)
    report = write_report(
        paths.output_dir,
        full_period,
        gates,
        parameter,
        subperiod,
        costs,
        walk_forward,
        ledger,
        bootstrap,
    )
    return gates, report
