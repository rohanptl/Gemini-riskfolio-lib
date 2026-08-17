from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DataConfig:
    start_date: str = "2019-01-01"
    end_date: str = "2026-08-09"
    universe_csv: Path = Path("Wealthfront_ETF_Categorization.csv")
    market_data_cache: Path = Path(
        "outputs_experiment_market_data_cache/adjusted_ohlcv.pkl"
    )
    baseline_csv: Path = Path(
        "outputs_milestone_prod_mom126_skip21"
        "/walk_forward_windows/2020/portfolio_backtest.csv"
    )


@dataclass(frozen=True)
class ExecutionConfig:
    overlay_weight: float = 0.05
    cost_bps_per_side: float = 10.0
    max_holding_days: int = 90
    profit_activation: float = 0.03
    atr_trailing_multiple: float = 3.0
    stop_floor_at_entry: bool = True
    initial_stop_atr_multiple: float | None = None
    replacement_min_holding_days: int | None = None


@dataclass(frozen=True)
class StandalonePortfolioConfig:
    max_positions: int = 3
    cost_bps_per_side: float = 10.0
    max_holding_days: int = 90
    profit_activation: float = 0.03
    atr_trailing_multiple: float = 3.0
    stop_floor_at_entry: bool = True
    initial_stop_atr_multiple: float = 3.0
    annual_cash_return: float = 0.02


@dataclass(frozen=True)
class WeeklyAWBConfig:
    name: str = "Weekly ATR-Confirmed Washout Base ETF Sleeve"
    short_name: str = "Weekly AWB Sleeve"
    rsi_length: int = 14
    washout_lookback_weeks: int = 26
    washout_rsi_max: float = 35.0
    washout_drawdown_max: float = -0.08
    min_base_weeks: int = 6
    max_base_weeks: int = 26
    confirmation_rsi_min: float = 50.0
    confirmation_rsi_max: float = 62.0
    rsi_cross_memory_weeks: int = 4
    weekly_sma_length: int = 40
    max_distance_above_sma: float = 0.08
    volatility_lookback_weeks: int = 13
    minimum_dollar_volume: float = 10_000_000.0
    thesis_failure_rsi: float = 40.0
