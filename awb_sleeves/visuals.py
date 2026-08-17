from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def create_equity_drawdown_chart(daily: pd.DataFrame, output_file: Path) -> None:
    fig, axes = plt.subplots(
        2, 1, figsize=(12, 8), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
    )
    axes[0].plot(daily.index, daily["BaselineEquity"], label="Production baseline")
    axes[0].plot(daily.index, daily["OverlayEquity"], label="Weekly AWB 5% overlay")
    axes[0].set_title("Weekly AWB Sleeve: Equity and Drawdown")
    axes[0].set_ylabel("Growth of $1")
    axes[0].grid(alpha=0.25)
    axes[0].legend()
    axes[1].plot(daily.index, daily["BaselineDrawdown"] * 100.0, label="Baseline")
    axes[1].plot(daily.index, daily["OverlayDrawdown"] * 100.0, label="Overlay")
    axes[1].axhline(0.0, color="black", linewidth=0.8)
    axes[1].set_ylabel("Drawdown (%)")
    axes[1].set_xlabel("Date")
    axes[1].grid(alpha=0.25)
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(output_file, dpi=160, bbox_inches="tight")
    plt.close(fig)


def create_trade_return_chart(trades: pd.DataFrame, output_file: Path) -> None:
    closed = trades.loc[trades["Status"].eq("Closed")].copy()
    if closed.empty:
        return
    closed = closed.sort_values("EntryDate")
    labels = closed["Ticker"] + "\n" + pd.to_datetime(closed["EntryDate"]).dt.strftime(
        "%Y-%m"
    )
    colors = ["#2a9d8f" if value >= 0.0 else "#d1495b" for value in closed["NetReturn"]]
    fig, ax = plt.subplots(figsize=(max(10, len(closed) * 0.55), 5.5))
    ax.bar(labels, closed["NetReturn"] * 100.0, color=colors)
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.set_title("Weekly AWB Closed Trades")
    ax.set_ylabel("Net return (%)")
    ax.set_xlabel("ETF and entry month")
    ax.grid(axis="y", alpha=0.25)
    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    fig.savefig(output_file, dpi=160, bbox_inches="tight")
    plt.close(fig)


def generate_visuals(daily: pd.DataFrame, trades: pd.DataFrame, output_dir: Path) -> None:
    create_equity_drawdown_chart(daily, output_dir / "equity_drawdown.png")
    create_trade_return_chart(trades, output_dir / "trade_returns.png")


def create_strategy_comparison_chart(
    daily: pd.DataFrame, names: list[str], output_file: Path
) -> None:
    fig, axes = plt.subplots(
        2, 1, figsize=(12, 8), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
    )
    for name in names:
        axes[0].plot(daily.index, daily[f"{name}Equity"], label=name)
        axes[1].plot(
            daily.index, daily[f"{name}Drawdown"] * 100.0, label=name
        )
    axes[0].set_title("Standalone Weekly AWB Strategy vs Benchmarks")
    axes[0].set_ylabel("Growth of $1")
    axes[0].grid(alpha=0.25)
    axes[0].legend(ncol=2)
    axes[1].axhline(0.0, color="black", linewidth=0.8)
    axes[1].set_ylabel("Drawdown (%)")
    axes[1].set_xlabel("Date")
    axes[1].grid(alpha=0.25)
    axes[1].legend(ncol=2)
    fig.tight_layout()
    fig.savefig(output_file, dpi=160, bbox_inches="tight")
    plt.close(fig)


def generate_strategy_visuals(
    daily: pd.DataFrame,
    trades: pd.DataFrame,
    comparison_names: list[str],
    output_dir: Path,
) -> None:
    create_strategy_comparison_chart(
        daily, comparison_names, output_dir / "strategy_comparison.png"
    )
    create_trade_return_chart(trades, output_dir / "trade_returns.png")
