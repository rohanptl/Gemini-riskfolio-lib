from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


TRADING_DAYS = 252
ANNUAL_RISK_FREE_RATE = 0.02
DAILY_RISK_FREE_RATE = ANNUAL_RISK_FREE_RATE / TRADING_DAYS


def performance_stats(returns: pd.Series, name: str) -> dict:
    values = returns.dropna().astype(float)
    equity = (1.0 + values).cumprod()
    total_return = equity.iloc[-1] - 1.0
    years = len(values) / TRADING_DAYS
    cagr = equity.iloc[-1] ** (1.0 / years) - 1.0 if years > 0.0 else np.nan
    volatility = values.std(ddof=1) * np.sqrt(TRADING_DAYS)
    sharpe = (
        (values.mean() - DAILY_RISK_FREE_RATE)
        / values.std(ddof=1)
        * np.sqrt(TRADING_DAYS)
        if values.std(ddof=1) > 0.0
        else np.nan
    )
    drawdown = equity / equity.cummax().clip(lower=1.0) - 1.0
    max_drawdown = drawdown.min()
    excess = values - DAILY_RISK_FREE_RATE
    downside = excess.clip(upper=0.0)
    downside_deviation = np.sqrt((downside.pow(2)).mean())
    sortino = (
        excess.mean() / downside_deviation * np.sqrt(TRADING_DAYS)
        if downside_deviation > 0.0
        else np.nan
    )
    return {
        "Name": name,
        "TotalReturn": total_return,
        "CAGR": cagr,
        "AnnualVolatility": volatility,
        "Sharpe": sharpe,
        "MaxDrawdown": max_drawdown,
        "MAR": cagr / abs(max_drawdown) if max_drawdown < 0.0 else np.nan,
        "Sortino": sortino,
    }


def annual_returns(return_map: dict[str, pd.Series]) -> pd.DataFrame:
    rows = []
    for name, series in return_map.items():
        clean = series.dropna()
        for year, values in clean.groupby(clean.index.year):
            rows.append(
                {
                    "Name": name,
                    "Year": int(year),
                    "Return": (1.0 + values).prod() - 1.0,
                }
            )
    return pd.DataFrame(rows)


def trade_summary(trades: pd.DataFrame) -> pd.DataFrame:
    closed = trades.loc[trades["Status"].eq("Closed")].copy()
    if closed.empty:
        return pd.DataFrame(
            [{"ClosedTrades": 0, "WinRate": np.nan, "AverageReturn": np.nan}]
        )
    return pd.DataFrame(
        [
            {
                "ClosedTrades": len(closed),
                "WinningTrades": int(closed["NetReturn"].gt(0.0).sum()),
                "WinRate": closed["NetReturn"].gt(0.0).mean(),
                "AverageReturn": closed["NetReturn"].mean(),
                "MedianReturn": closed["NetReturn"].median(),
                "BestReturn": closed["NetReturn"].max(),
                "WorstReturn": closed["NetReturn"].min(),
                "AverageHoldingDays": closed["HoldingDays"].mean(),
            }
        ]
    )


def write_outputs(
    output_dir: Path,
    daily: pd.DataFrame,
    trades: pd.DataFrame,
    candidates: pd.DataFrame,
    signal_table: pd.DataFrame,
) -> pd.DataFrame:
    output_dir.mkdir(parents=True, exist_ok=True)
    daily = daily.copy()
    daily["BaselineEquity"] = (1.0 + daily["BaselineReturn"]).cumprod()
    daily["OverlayEquity"] = (1.0 + daily["OverlayReturn"]).cumprod()
    daily["OverlayDrawdown"] = (
        daily["OverlayEquity"] / daily["OverlayEquity"].cummax() - 1.0
    )
    daily["BaselineDrawdown"] = (
        daily["BaselineEquity"] / daily["BaselineEquity"].cummax() - 1.0
    )
    stats = pd.DataFrame(
        [
            performance_stats(daily["BaselineReturn"], "ProductionBaseline"),
            performance_stats(daily["OverlayReturn"], "WeeklyAWB5PctOverlay"),
            performance_stats(
                daily["StandaloneSleeveReturn"], "WeeklyAWBStandalone"
            ),
        ]
    ).set_index("Name")
    baseline = stats.loc["ProductionBaseline"]
    for metric in ["CAGR", "Sharpe", "MaxDrawdown", "MAR", "Sortino"]:
        stats[f"Delta{metric}VsBaseline"] = stats[metric] - baseline[metric]

    daily.to_csv(output_dir / "daily_returns.csv")
    trades.to_csv(output_dir / "trades.csv", index=False)
    candidates.to_csv(output_dir / "weekly_candidates.csv", index=False)
    stats.to_csv(output_dir / "performance_summary.csv")
    trade_summary(trades).to_csv(output_dir / "trade_summary.csv", index=False)
    annual_returns(
        {
            "ProductionBaseline": daily["BaselineReturn"],
            "WeeklyAWB5PctOverlay": daily["OverlayReturn"],
            "WeeklyAWBStandalone": daily["StandaloneSleeveReturn"],
        }
    ).to_csv(output_dir / "annual_returns.csv", index=False)

    if not signal_table.empty and "XLV" in signal_table.index.get_level_values("Ticker"):
        signal_table.xs("XLV", level="Ticker").loc[
            "2025-03-01":"2025-12-31"
        ].to_csv(output_dir / "xlv_weekly_diagnostics.csv")
    return stats


def write_strategy_outputs(
    output_dir: Path,
    daily: pd.DataFrame,
    trades: pd.DataFrame,
    candidates: pd.DataFrame,
    benchmarks: dict[str, pd.Series],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    output_dir.mkdir(parents=True, exist_ok=True)
    comparison_returns: dict[str, pd.Series] = {
        "WeeklyAWBStrategy": daily["StrategyReturn"]
    }
    output_daily = daily.copy()
    for name, returns in benchmarks.items():
        aligned = returns.reindex(daily.index).fillna(0.0)
        output_daily[f"{name}Return"] = aligned
        comparison_returns[name] = aligned

    for name, returns in comparison_returns.items():
        output_daily[f"{name}Equity"] = (1.0 + returns).cumprod()
        output_daily[f"{name}Drawdown"] = (
            output_daily[f"{name}Equity"]
            / output_daily[f"{name}Equity"].cummax().clip(lower=1.0)
            - 1.0
        )
    stats = pd.DataFrame(
        [performance_stats(returns, name) for name, returns in comparison_returns.items()]
    ).set_index("Name")
    output_daily.to_csv(output_dir / "daily_returns.csv")
    trades.to_csv(output_dir / "trades.csv", index=False)
    candidates.to_csv(output_dir / "weekly_candidates.csv", index=False)
    stats.to_csv(output_dir / "performance_summary.csv")
    trade_summary(trades).to_csv(output_dir / "trade_summary.csv", index=False)
    annual_returns(comparison_returns).to_csv(
        output_dir / "annual_returns.csv", index=False
    )
    return stats, output_daily
