from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

import main_option2_all_etfs_v5_16_rolling_asof_monthly_attribution_dynamic_enddate as production
from experiment_oversold_reversal_sleeve import (
    backtest_daily_confirmation_variant,
    build_long_indicator_table,
    load_or_calculate_indicators,
    load_or_download_ohlcv,
)
from .validation import (
    SELECTED_SLUG,
    bootstrap_trade_excess,
    leave_one_ticker_out,
    load_signal_log,
    market_frames,
    next_open_trade_ledger,
)


@dataclass(frozen=True)
class PreSampleConfig:
    data_start: str = "2005-01-01"
    evaluation_start: str = "2007-01-01"
    evaluation_end: str = "2020-10-08"
    market_cache: Path = Path(
        "outputs_experiment_market_data_cache/adjusted_ohlcv_pre2020.pkl"
    )
    indicator_cache: Path = Path(
        "outputs_experiment_market_data_cache/indicators_pre2020.pkl"
    )
    current_market_cache: Path = Path(
        "outputs_experiment_market_data_cache/adjusted_ohlcv.pkl"
    )
    current_experiment_dir: Path = Path(
        "outputs_experiment_oversold_reversal_sleeve_v7_causal_validation"
    )
    output_dir: Path = Path(
        "outputs_experiment_daily_awb_presample_validation"
    )
    refresh_data: bool = False
    bootstrap_samples: int = 20_000
    seed: int = 42


FROZEN_EXIT_VARIANTS = {
    "Profit3Trail15": (0.03, 1.5, True),
    "Profit3Trail20": (0.03, 2.0, True),
    "Profit3Trail25": (0.03, 2.5, True),
    "Profit3Trail275": (0.03, 2.75, True),
    "Profit3Trail30": (0.03, 3.0, True),
    "Profit3Trail25NoFloor": (0.03, 2.5, False),
    "Profit3Trail30NoFloor": (0.03, 3.0, False),
    "Profit4Trail25": (0.04, 2.5, True),
    "Profit5Trail15": (0.05, 1.5, True),
    "Profit5Trail20": (0.05, 2.0, True),
    "Profit5Trail25": (0.05, 2.5, True),
}


def _risk_tickers() -> list[str]:
    tickers = production.load_tickers(production.CSV_FILE)
    categorization = pd.read_csv(production.CSV_FILE)
    risk_assets = set(
        categorization.loc[
            ~categorization["Asset_Class"].isin(
                {"Fixed Income & Cash", "Cryptocurrency"}
            ),
            "Ticker",
        ].astype(str)
    )
    return sorted(
        ticker
        for ticker in tickers
        if ticker in risk_assets
        and ticker not in production.CASH_EQUIVALENT_TICKERS
    )


def _entry_whitelist(signal_log: pd.DataFrame) -> dict[pd.Timestamp, set[str]]:
    whitelist: dict[pd.Timestamp, set[str]] = {}
    for row in signal_log[signal_log["Action"].eq("Enter")].itertuples(index=False):
        whitelist.setdefault(pd.Timestamp(row.Date), set()).add(str(row.Ticker))
    return whitelist


def _trade_summary(name: str, ledger: pd.DataFrame) -> dict[str, object]:
    closed = ledger[ledger["Status"].eq("Closed")]
    return {
        "Variant": name,
        "ClosedTrades": len(closed),
        "WinRate": closed["NetReturn"].gt(0.0).mean(),
        "MeanNetReturn": closed["NetReturn"].mean(),
        "MedianNetReturn": closed["NetReturn"].median(),
        "MeanExcessReturnVsSPY": closed["ExcessReturnVsSPY"].mean(),
        "MedianExcessReturnVsSPY": closed["ExcessReturnVsSPY"].median(),
        "BeatSPYRate": closed["ExcessReturnVsSPY"].gt(0.0).mean(),
        "WorstTrade": closed["NetReturn"].min(),
    }


def _subperiod_summary(ledger: pd.DataFrame) -> pd.DataFrame:
    periods = [
        ("2007-2009 GFC", 2007, 2009),
        ("2010-2012", 2010, 2012),
        ("2013-2015", 2013, 2015),
        ("2016-2018", 2016, 2018),
        ("2019-Oct 2020", 2019, 2020),
    ]
    closed = ledger[ledger["Status"].eq("Closed")]
    rows = []
    for label, first_year, last_year in periods:
        sample = closed[closed["EntryDate"].dt.year.between(first_year, last_year)]
        rows.append(
            {
                "Period": label,
                "ClosedTrades": len(sample),
                "WinRate": sample["NetReturn"].gt(0.0).mean(),
                "MeanNetReturn": sample["NetReturn"].mean(),
                "MeanExcessReturnVsSPY": sample["ExcessReturnVsSPY"].mean(),
                "BeatSPYRate": sample["ExcessReturnVsSPY"].gt(0.0).mean(),
            }
        )
    return pd.DataFrame(rows)


def _walk_forward_exit_choice(
    ledgers: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    blocks = [
        ("2010-2012", 2010, 2012),
        ("2013-2015", 2013, 2015),
        ("2016-2018", 2016, 2018),
        ("2019-Oct 2020", 2019, 2020),
    ]
    rows = []
    for label, first_year, last_year in blocks:
        training_scores = {}
        for name, ledger in ledgers.items():
            closed = ledger[ledger["Status"].eq("Closed")]
            training = closed[closed["EntryDate"].dt.year < first_year]
            if len(training) >= 3:
                training_scores[name] = training["ExcessReturnVsSPY"].mean()
        if not training_scores:
            continue
        chosen = max(training_scores, key=training_scores.get)
        closed = ledgers[chosen][ledgers[chosen]["Status"].eq("Closed")]
        test = closed[closed["EntryDate"].dt.year.between(first_year, last_year)]
        rows.append(
            {
                "TestPeriod": label,
                "ChosenVariant": chosen,
                "TrainingMeanExcess": training_scores[chosen],
                "TestTrades": len(test),
                "TestMeanNetReturn": test["NetReturn"].mean(),
                "TestMeanExcessReturnVsSPY": test["ExcessReturnVsSPY"].mean(),
                "TestBeatSPYRate": test["ExcessReturnVsSPY"].gt(0.0).mean(),
            }
        )
    return pd.DataFrame(rows)


def _bootstrap_samples(
    presample: pd.DataFrame,
    current: pd.DataFrame,
    samples: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    combined = pd.concat(
        [
            presample.assign(Sample="Pre-2020"),
            current.assign(Sample="2020-2026"),
        ],
        ignore_index=True,
    ).sort_values("EntryDate")
    rows = []
    for offset, (name, ledger) in enumerate(
        [
            ("Pre-2020", presample),
            ("2020-2026", current),
            ("Combined", combined),
        ]
    ):
        summary = bootstrap_trade_excess(ledger, samples, seed + offset)
        summary.insert(0, "Sample", name)
        rows.append(summary)
    return pd.concat(rows, ignore_index=True), combined


def _validation_gates(
    selected: pd.DataFrame,
    parameter: pd.DataFrame,
    subperiod: pd.DataFrame,
    walk_forward: pd.DataFrame,
    bootstrap: pd.DataFrame,
    combined: pd.DataFrame,
) -> pd.DataFrame:
    pre_closed = selected[selected["Status"].eq("Closed")]
    combined_closed = combined[combined["Status"].eq("Closed")]
    pre_bootstrap = bootstrap[bootstrap["Sample"].eq("Pre-2020")].iloc[0]
    combined_bootstrap = bootstrap[bootstrap["Sample"].eq("Combined")].iloc[0]
    nonempty_periods = subperiod[subperiod["ClosedTrades"].gt(0)]
    gates = [
        (
            "Untouched pre-2020 excess",
            pre_closed["ExcessReturnVsSPY"].mean() > 0.0,
            f"Mean next-open excess {pre_closed['ExcessReturnVsSPY'].mean():.2%}",
        ),
        (
            "Pre-2020 bootstrap confidence",
            pre_bootstrap["Lower95MeanExcess"] > 0.0,
            f"95% lower bound {pre_bootstrap['Lower95MeanExcess']:.2%}",
        ),
        (
            "Combined bootstrap confidence",
            combined_bootstrap["Lower95MeanExcess"] > 0.0,
            f"95% lower bound {combined_bootstrap['Lower95MeanExcess']:.2%}",
        ),
        (
            "Combined minimum sample",
            len(combined_closed) >= 30,
            f"{len(combined_closed)} closed trades",
        ),
        (
            "Pre-sample regime consistency",
            nonempty_periods["MeanExcessReturnVsSPY"].gt(0.0).mean() >= 0.6,
            f"{nonempty_periods['MeanExcessReturnVsSPY'].gt(0.0).sum()}/{len(nonempty_periods)} regimes positive",
        ),
        (
            "Pre-sample parameter neighborhood",
            parameter["MeanExcessReturnVsSPY"].gt(0.0).mean() >= 0.8,
            f"{parameter['MeanExcessReturnVsSPY'].gt(0.0).sum()}/{len(parameter)} exits positive",
        ),
        (
            "Pre-sample walk-forward exits",
            walk_forward["TestMeanExcessReturnVsSPY"].gt(0.0).mean() >= 0.75,
            f"{walk_forward['TestMeanExcessReturnVsSPY'].gt(0.0).sum()}/{len(walk_forward)} test blocks positive",
        ),
    ]
    return pd.DataFrame(
        {"Gate": [item[0] for item in gates],
         "Passed": [bool(item[1]) for item in gates],
         "Evidence": [item[2] for item in gates]}
    )


def _write_report(
    config: PreSampleConfig,
    selected: pd.DataFrame,
    current: pd.DataFrame,
    combined: pd.DataFrame,
    parameter: pd.DataFrame,
    subperiod: pd.DataFrame,
    walk_forward: pd.DataFrame,
    bootstrap: pd.DataFrame,
    gates: pd.DataFrame,
    eligible_tickers: int,
) -> Path:
    pre_closed = selected[selected["Status"].eq("Closed")]
    current_closed = current[current["Status"].eq("Closed")]
    combined_closed = combined[combined["Status"].eq("Closed")]
    pre_boot = bootstrap[bootstrap["Sample"].eq("Pre-2020")].iloc[0]
    combined_boot = bootstrap[bootstrap["Sample"].eq("Combined")].iloc[0]
    passed = int(gates["Passed"].sum())
    lines = [
        "# Frozen Daily AWB Pre-2020 Validation",
        "",
        f"**Additional gates passed: {passed}/{len(gates)}.**",
        "",
        "The causal 2020-2026 rules were frozen before this run and applied unchanged "
        f"from {config.evaluation_start} up to (but excluding) {config.evaluation_end}.",
        "",
        "## Pre-sample result",
        "",
        f"- Eligible current-universe ETFs with usable history: {eligible_tickers}",
        f"- Closed pre-2020 trades: {len(pre_closed)}",
        f"- Win rate: {pre_closed['NetReturn'].gt(0.0).mean():.1%}",
        f"- Mean net return: {pre_closed['NetReturn'].mean():.2%}",
        f"- Mean excess versus SPY: {pre_closed['ExcessReturnVsSPY'].mean():.2%}",
        f"- Beat-SPY rate: {pre_closed['ExcessReturnVsSPY'].gt(0.0).mean():.1%}",
        f"- Pre-sample bootstrap 95% interval: {pre_boot['Lower95MeanExcess']:.2%} to {pre_boot['Upper95MeanExcess']:.2%}",
        "",
        "## Combined evidence",
        "",
        f"- Closed 2020-2026 trades: {len(current_closed)}",
        f"- Total closed trades: {len(combined_closed)}",
        f"- Combined mean excess versus SPY: {combined_closed['ExcessReturnVsSPY'].mean():.2%}",
        f"- Combined bootstrap 95% interval: {combined_boot['Lower95MeanExcess']:.2%} to {combined_boot['Upper95MeanExcess']:.2%}",
        "",
        "## Additional validation gates",
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
            "## Important limitation",
            "",
            "The ETF list is today's production universe. Funds that closed before the "
            "universe file was created are absent, so the pre-sample test has survivorship "
            "bias. It is a useful frozen-rule stress test, not a point-in-time universe study.",
            "",
            "Detailed parameter, regime, walk-forward, bootstrap, trade, and concentration "
            "tables are stored beside this report.",
        ]
    )
    path = config.output_dir / "presample_validation_report.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_presample_validation(config: PreSampleConfig) -> tuple[pd.DataFrame, Path]:
    config.output_dir.mkdir(parents=True, exist_ok=True)
    risk_tickers = _risk_tickers()
    requested_tickers = sorted(set(risk_tickers + ["SPY"]))
    ohlcv, _ = load_or_download_ohlcv(
        requested_tickers,
        config.data_start,
        config.evaluation_end,
        config.market_cache,
        config.refresh_data,
    )
    indicators, _ = load_or_calculate_indicators(
        ohlcv,
        config.data_start,
        config.evaluation_end,
        config.indicator_cache,
        config.refresh_data,
    )
    candidate_tickers = [ticker for ticker in risk_tickers if ticker in indicators]
    if "SPY" not in indicators:
        raise RuntimeError("SPY data is required for the pre-sample calendar and benchmark.")
    calendar = indicators["SPY"].loc[
        config.evaluation_start:config.evaluation_end
    ].index
    zero_baseline = pd.Series(0.0, index=calendar, name="DailyReturn")
    long_table = build_long_indicator_table(
        {ticker: indicators[ticker] for ticker in candidate_tickers}
    )
    returns = pd.DataFrame(
        {ticker: indicators[ticker]["Close"].pct_change() for ticker in indicators}
    ).sort_index()

    _, _, control_log, _ = backtest_daily_confirmation_variant(
        variant="FrozenControlATR125",
        indicators=indicators,
        baseline_returns=zero_baseline,
        candidate_tickers=candidate_tickers,
        max_holdings=2,
        weight_per_holding=0.05,
        max_holding_days=20,
        cost_bps=10.0,
        rank_ascending=True,
        max_pair_correlation=0.80,
        signal_column="SignalTwoStageQuality10ATR125",
        prebuilt_long_table=long_table,
        precomputed_asset_returns=returns,
    )
    whitelist = _entry_whitelist(control_log)
    frames = {ticker: frame.copy() for ticker, frame in ohlcv.items()}
    ledgers: dict[str, pd.DataFrame] = {}
    summary_rows = []
    for name, (activation, trailing, floor) in FROZEN_EXIT_VARIANTS.items():
        _, _, signal_log, _ = backtest_daily_confirmation_variant(
            variant=name,
            indicators=indicators,
            baseline_returns=zero_baseline,
            candidate_tickers=candidate_tickers,
            max_holdings=2,
            weight_per_holding=0.05,
            max_holding_days=20,
            cost_bps=10.0,
            rank_ascending=True,
            max_pair_correlation=0.80,
            signal_column="SignalTwoStageQuality10ATR125",
            profit_stop_activation=activation,
            atr_trailing_multiple=trailing,
            atr_stop_floor_at_entry=floor,
            entry_event_whitelist=whitelist,
            prebuilt_long_table=long_table,
            precomputed_asset_returns=returns,
        )
        ledger = next_open_trade_ledger(signal_log, frames)
        ledgers[name] = ledger
        summary_rows.append(_trade_summary(name, ledger))
        signal_log.to_csv(config.output_dir / f"signal_log_{name.lower()}.csv", index=False)
    parameter = pd.DataFrame(summary_rows).sort_values(
        "MeanExcessReturnVsSPY", ascending=False
    )
    selected = ledgers["Profit3Trail30"]
    current_frames = market_frames(config.current_market_cache)
    current_log = load_signal_log(config.current_experiment_dir, SELECTED_SLUG)
    current = next_open_trade_ledger(current_log, current_frames)
    bootstrap, combined = _bootstrap_samples(
        selected, current, config.bootstrap_samples, config.seed
    )
    subperiod = _subperiod_summary(selected)
    walk_forward = _walk_forward_exit_choice(ledgers)
    concentration = leave_one_ticker_out(combined)
    gates = _validation_gates(
        selected, parameter, subperiod, walk_forward, bootstrap, combined
    )

    outputs = {
        "presample_selected_trades.csv": selected,
        "current_selected_trades.csv": current,
        "combined_selected_trades.csv": combined,
        "presample_parameter_sensitivity.csv": parameter,
        "presample_subperiods.csv": subperiod,
        "presample_walk_forward.csv": walk_forward,
        "presample_bootstrap_summary.csv": bootstrap,
        "combined_leave_one_ticker_out.csv": concentration,
        "presample_validation_gates.csv": gates,
    }
    for filename, frame in outputs.items():
        frame.to_csv(config.output_dir / filename, index=False)
    report = _write_report(
        config,
        selected,
        current,
        combined,
        parameter,
        subperiod,
        walk_forward,
        bootstrap,
        gates,
        len(candidate_tickers),
    )
    return gates, report
