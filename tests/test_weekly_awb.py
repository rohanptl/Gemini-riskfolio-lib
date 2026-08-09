from __future__ import annotations

import unittest

import pandas as pd

from awb_sleeves.config import WeeklyAWBConfig
from awb_sleeves.strategies.weekly_awb import (
    add_weekly_awb_signal,
    rank_weekly_candidates,
)


class WeeklyAWBSignalTests(unittest.TestCase):
    def test_confirmed_washout_base_qualifies(self) -> None:
        features = pd.DataFrame(
            {
                "RecentWeeklyRSIMin26": [34.0],
                "RecentDrawdownMin26": [-0.12],
                "WeeksSinceLow26": [13.0],
                "WeeklyRSI14": [53.0],
                "RSICross50Memory": [True],
                "WeeklyMACDHist": [0.6],
                "WeeklyMACDHistDelta1": [0.3],
                "WeeklyCMF20": [0.05],
                "Close": [136.0],
                "WeeklySMA40": [135.8],
                "DistanceAboveSMA40": [0.0015],
                "VolatilityContracting": [True],
                "DollarVolume20": [100_000_000.0],
                "WeeklyATR14Pct": [0.035],
            },
            index=pd.to_datetime(["2025-08-22"]),
        )
        result = add_weekly_awb_signal(features, WeeklyAWBConfig())
        self.assertTrue(bool(result.iloc[0]["WeeklyAWBSignal"]))

    def test_rank_prefers_stronger_unextended_candidate(self) -> None:
        snapshot = pd.DataFrame(
            {
                "RSIRecoveryFromWashout": [19.0, 12.0],
                "WeeklyMACDHistDelta1": [0.30, 0.05],
                "Close": [100.0, 100.0],
                "WeeklyCMF20": [0.10, 0.01],
                "WeeklyATR14Pct": [0.02, 0.04],
                "DistanceAboveSMA40": [0.01, 0.06],
            },
            index=["STRONG", "WEAK"],
        )
        scores = rank_weekly_candidates(snapshot)
        self.assertGreater(scores["STRONG"], scores["WEAK"])


if __name__ == "__main__":
    unittest.main()
