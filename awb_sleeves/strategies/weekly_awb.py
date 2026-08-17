from __future__ import annotations

import pandas as pd

from ..config import WeeklyAWBConfig


NAME = "Weekly ATR-Confirmed Washout Base ETF Sleeve"
SHORT_NAME = "Weekly AWB Sleeve"


def add_weekly_awb_signal(
    features: pd.DataFrame, config: WeeklyAWBConfig
) -> pd.DataFrame:
    weekly = features.copy()
    washout_memory = (
        weekly["RecentWeeklyRSIMin26"].le(config.washout_rsi_max)
        & weekly["RecentDrawdownMin26"].le(config.washout_drawdown_max)
        & weekly["WeeksSinceLow26"].between(
            config.min_base_weeks, config.max_base_weeks, inclusive="both"
        )
    )
    confirmation = (
        weekly["WeeklyRSI14"].between(
            config.confirmation_rsi_min,
            config.confirmation_rsi_max,
            inclusive="both",
        )
        & weekly["RSICross50Memory"].fillna(False)
        & weekly["WeeklyMACDHist"].gt(0.0)
        & weekly["WeeklyMACDHistDelta1"].gt(0.0)
        & weekly["WeeklyCMF20"].gt(0.0)
        & weekly["Close"].gt(weekly["WeeklySMA40"])
        & weekly["DistanceAboveSMA40"].between(
            0.0, config.max_distance_above_sma, inclusive="both"
        )
        & weekly["VolatilityContracting"].fillna(False)
        & weekly["DollarVolume20"].ge(config.minimum_dollar_volume)
    )
    weekly["WeeklyWashoutMemory"] = washout_memory
    weekly["WeeklyAWBSignal"] = washout_memory & confirmation
    weekly["RSIRecoveryFromWashout"] = (
        weekly["WeeklyRSI14"] - weekly["RecentWeeklyRSIMin26"]
    )
    return weekly


def rank_weekly_candidates(snapshot: pd.DataFrame) -> pd.Series:
    """Rank confirmed bases; higher scores are preferred."""
    components = pd.DataFrame(index=snapshot.index)
    components["RSIRecovery"] = snapshot["RSIRecoveryFromWashout"].rank(pct=True)
    components["MACDAcceleration"] = (
        snapshot["WeeklyMACDHistDelta1"] / snapshot["Close"]
    ).rank(pct=True)
    components["MoneyFlow"] = snapshot["WeeklyCMF20"].rank(pct=True)
    components["LowVolatility"] = (-snapshot["WeeklyATR14Pct"]).rank(pct=True)
    components["NotExtended"] = (-snapshot["DistanceAboveSMA40"]).rank(pct=True)
    return components.mean(axis=1)


def build_signal_table(
    weekly_features: dict[str, pd.DataFrame], config: WeeklyAWBConfig
) -> pd.DataFrame:
    rows = []
    for ticker, features in weekly_features.items():
        signaled = add_weekly_awb_signal(features, config)
        item = signaled.reset_index()
        item.insert(1, "Ticker", ticker)
        rows.append(item)
    if not rows:
        return pd.DataFrame()
    return pd.concat(rows, ignore_index=True).set_index(["Date", "Ticker"]).sort_index()
