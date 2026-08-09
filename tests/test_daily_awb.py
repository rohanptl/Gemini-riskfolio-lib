from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from experiment_oversold_reversal_sleeve import (
    calculate_indicators,
    chaikin_money_flow,
    rsi_wilder,
)
from awb_sleeves.validation import next_open_trade_ledger


def synthetic_daily_frame() -> pd.DataFrame:
    index = pd.bdate_range("2023-01-03", "2026-07-31")
    steps = np.arange(len(index), dtype=float)
    close = pd.Series(
        100.0 + 0.025 * steps + 7.0 * np.sin(steps / 31.0),
        index=index,
    )
    open_price = close.shift(1).fillna(close.iloc[0]) * (
        1.0 + 0.0015 * np.sin(steps / 7.0)
    )
    return pd.DataFrame(
        {
            "Open": open_price,
            "High": np.maximum(open_price, close) * 1.008,
            "Low": np.minimum(open_price, close) * 0.992,
            "Close": close,
            "Volume": 2_000_000.0 + 200_000.0 * np.cos(steps / 11.0),
        },
        index=index,
    )


class DailyAWBAsOfTests(unittest.TestCase):
    def test_midweek_features_are_prefix_invariant(self) -> None:
        frame = synthetic_daily_frame()
        date = next(
            value for value in reversed(frame.index[:-20]) if value.weekday() == 2
        )
        full = calculate_indicators(frame)
        truncated = calculate_indicators(frame.loc[:date])

        for column in [
            "WeeklyRSI14",
            "WeeklyMACDHist",
            "WeeklyMACDHistDelta1",
            "WeeklyCMF20",
            "WeeklySMA40",
        ]:
            self.assertAlmostEqual(
                float(full.loc[date, column]),
                float(truncated.loc[date, column]),
                places=12,
                msg=column,
            )
        self.assertEqual(
            bool(full.loc[date, "SignalTwoStageQuality10ATR125"]),
            bool(truncated.loc[date, "SignalTwoStageQuality10ATR125"]),
        )

    def test_friday_features_match_completed_week_calculation(self) -> None:
        frame = synthetic_daily_frame()
        calculated = calculate_indicators(frame)
        periods = frame.index.to_period("W-FRI")
        grouped = frame.groupby(periods)
        weekly = grouped.agg(
            Open=("Open", "first"),
            High=("High", "max"),
            Low=("Low", "min"),
            Close=("Close", "last"),
            Volume=("Volume", "sum"),
        )
        completed_dates = grouped.apply(
            lambda values: values.index.max(), include_groups=False
        )
        weekly_rsi = rsi_wilder(weekly["Close"], 14)
        ema12 = weekly["Close"].ewm(span=12, adjust=False).mean()
        ema26 = weekly["Close"].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        weekly_cmf = chaikin_money_flow(weekly, 20)
        weekly_sma = weekly["Close"].rolling(40, min_periods=40).mean()

        period = weekly.index[-5]
        date = pd.Timestamp(completed_dates.loc[period])
        self.assertEqual(date.weekday(), 4)
        expected = {
            "WeeklyRSI14": weekly_rsi.loc[period],
            "WeeklyMACDHist": histogram.loc[period],
            "WeeklyMACDHistDelta1": histogram.diff().loc[period],
            "WeeklyCMF20": weekly_cmf.loc[period],
            "WeeklySMA40": weekly_sma.loc[period],
        }
        for column, value in expected.items():
            self.assertAlmostEqual(
                float(calculated.loc[date, column]),
                float(value),
                places=12,
                msg=column,
            )

    def test_trade_ledger_executes_on_next_session_open(self) -> None:
        dates = pd.bdate_range("2026-01-05", periods=5)
        asset = pd.DataFrame(
            {
                "Open": [100.0, 101.0, 102.0, 103.0, 104.0],
                "Close": [100.5, 101.5, 102.5, 103.5, 104.5],
            },
            index=dates,
        )
        spy = pd.DataFrame(
            {
                "Open": [200.0, 201.0, 202.0, 203.0, 204.0],
                "Close": [200.5, 201.5, 202.5, 203.5, 204.5],
            },
            index=dates,
        )
        signal_log = pd.DataFrame(
            [
                {
                    "Date": dates[0],
                    "Ticker": "ETF",
                    "Action": "Enter",
                    "ExitReason": "",
                },
                {
                    "Date": dates[2],
                    "Ticker": "ETF",
                    "Action": "Exit",
                    "ExitReason": "ATRProfitStop",
                },
            ]
        )
        ledger = next_open_trade_ledger(
            signal_log, {"ETF": asset, "SPY": spy}, cost_bps_per_side=0.0
        )
        trade = ledger.iloc[0]
        self.assertEqual(trade["EntryDate"], dates[1])
        self.assertEqual(trade["ExitDate"], dates[3])
        self.assertAlmostEqual(trade["GrossReturn"], 103.0 / 101.0 - 1.0)


if __name__ == "__main__":
    unittest.main()
