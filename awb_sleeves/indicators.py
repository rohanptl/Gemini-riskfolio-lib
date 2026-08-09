from __future__ import annotations

import numpy as np
import pandas as pd

from .config import WeeklyAWBConfig


def rsi_wilder(close: pd.Series, length: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1.0 / length, adjust=False, min_periods=length).mean()
    avg_loss = loss.ewm(alpha=1.0 / length, adjust=False, min_periods=length).mean()
    relative_strength = avg_gain / avg_loss.replace(0.0, np.nan)
    rsi = 100.0 - 100.0 / (1.0 + relative_strength)
    return rsi.where(avg_loss > 0.0, 100.0)


def average_true_range(frame: pd.DataFrame, length: int = 14) -> pd.Series:
    previous_close = frame["Close"].shift(1)
    true_range = pd.concat(
        [
            frame["High"] - frame["Low"],
            (frame["High"] - previous_close).abs(),
            (frame["Low"] - previous_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return true_range.ewm(
        alpha=1.0 / length, adjust=False, min_periods=length
    ).mean()


def chaikin_money_flow(frame: pd.DataFrame, length: int = 20) -> pd.Series:
    spread = (frame["High"] - frame["Low"]).replace(0.0, np.nan)
    multiplier = (
        (frame["Close"] - frame["Low"])
        - (frame["High"] - frame["Close"])
    ) / spread
    flow_volume = multiplier.fillna(0.0) * frame["Volume"].fillna(0.0)
    volume_sum = frame["Volume"].rolling(length, min_periods=length).sum()
    return flow_volume.rolling(length, min_periods=length).sum() / volume_sum.replace(
        0.0, np.nan
    )


def daily_execution_features(frame: pd.DataFrame) -> pd.DataFrame:
    daily = frame.copy().sort_index()
    daily["ATR14"] = average_true_range(daily, 14)
    daily["DollarVolume20"] = (
        daily["Close"] * daily["Volume"]
    ).rolling(20, min_periods=20).mean()
    return daily


def _weeks_since_rolling_low(close: pd.Series, lookback: int) -> pd.Series:
    return close.rolling(lookback, min_periods=max(13, lookback // 2)).apply(
        lambda values: len(values) - 1 - int(np.argmin(values)), raw=True
    )


def weekly_signal_features(
    daily: pd.DataFrame, config: WeeklyAWBConfig
) -> pd.DataFrame:
    periods = daily.index.to_period("W-FRI")
    grouped = daily.groupby(periods)
    weekly = grouped.agg(
        Open=("Open", "first"),
        High=("High", "max"),
        Low=("Low", "min"),
        Close=("Close", "last"),
        Volume=("Volume", "sum"),
        DollarVolume20=("DollarVolume20", "last"),
    )
    weekly.index = pd.DatetimeIndex(
        grouped.apply(lambda group: group.index.max(), include_groups=False).values,
        name="Date",
    )
    close = weekly["Close"]
    weekly["WeeklyRSI14"] = rsi_wilder(close, config.rsi_length)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    weekly["WeeklyMACDHist"] = macd - macd_signal
    weekly["WeeklyMACDHistDelta1"] = weekly["WeeklyMACDHist"].diff()
    weekly["WeeklyCMF20"] = chaikin_money_flow(weekly, 20)
    weekly["WeeklySMA40"] = close.rolling(
        config.weekly_sma_length, min_periods=config.weekly_sma_length
    ).mean()
    weekly["WeeklyATR14"] = average_true_range(weekly, 14)
    weekly["WeeklyATR14Pct"] = weekly["WeeklyATR14"] / close
    weekly["WeeklyATRMedian13"] = weekly["WeeklyATR14Pct"].rolling(
        config.volatility_lookback_weeks,
        min_periods=max(6, config.volatility_lookback_weeks // 2),
    ).median()
    weekly["VolatilityContracting"] = (
        weekly["WeeklyATR14Pct"] <= weekly["WeeklyATRMedian13"]
    )
    weekly["Drawdown26"] = close / close.rolling(
        config.washout_lookback_weeks,
        min_periods=config.washout_lookback_weeks,
    ).max() - 1.0
    weekly["RecentWeeklyRSIMin26"] = weekly["WeeklyRSI14"].rolling(
        config.washout_lookback_weeks,
        min_periods=max(13, config.washout_lookback_weeks // 2),
    ).min()
    weekly["RecentDrawdownMin26"] = weekly["Drawdown26"].rolling(
        config.washout_lookback_weeks,
        min_periods=max(13, config.washout_lookback_weeks // 2),
    ).min()
    weekly["WeeksSinceLow26"] = _weeks_since_rolling_low(
        close, config.washout_lookback_weeks
    )
    rsi_cross_50 = (
        weekly["WeeklyRSI14"].gt(config.confirmation_rsi_min)
        & weekly["WeeklyRSI14"].shift(1).le(config.confirmation_rsi_min)
    )
    weekly["RSICross50Memory"] = rsi_cross_50.rolling(
        config.rsi_cross_memory_weeks, min_periods=1
    ).max().astype(bool)
    weekly["DistanceAboveSMA40"] = close / weekly["WeeklySMA40"] - 1.0
    return weekly


def build_feature_sets(
    market_data: dict[str, pd.DataFrame], config: WeeklyAWBConfig
) -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    daily_features: dict[str, pd.DataFrame] = {}
    weekly_features: dict[str, pd.DataFrame] = {}
    for ticker, raw in market_data.items():
        if len(raw) < 220:
            continue
        daily = daily_execution_features(raw)
        weekly = weekly_signal_features(daily, config)
        daily_features[ticker] = daily
        weekly_features[ticker] = weekly
    return daily_features, weekly_features
