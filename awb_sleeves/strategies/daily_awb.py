from __future__ import annotations

import pandas as pd


NAME = "ATR-Confirmed Washout Breakout ETF Sleeve"
SHORT_NAME = "AWB Sleeve"
SIGNAL_COLUMN = "SignalTwoStageQuality10ATR125"


def eligible_candidates(snapshot: pd.DataFrame) -> pd.DataFrame:
    """Return the final high-quality daily AWB candidates from an indicator snapshot."""
    mask = (
        snapshot[SIGNAL_COLUMN].fillna(False)
        & snapshot["DollarVolume20"].ge(10_000_000.0)
    )
    return snapshot.loc[mask].copy()
