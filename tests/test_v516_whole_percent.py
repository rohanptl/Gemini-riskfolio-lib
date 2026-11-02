import importlib.util
from pathlib import Path
import unittest

import pandas as pd


ENGINE_PATH = Path(
    "main_option2_all_etfs_v5_16_rolling_asof_monthly_attribution_dynamic_enddate.py"
)


def load_engine():
    spec = importlib.util.spec_from_file_location("v516_engine_test", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


engine = load_engine()


class WholePercentAllocationTests(unittest.TestCase):
    def test_production_configuration(self) -> None:
        self.assertAlmostEqual(engine.MAX_RISK_ASSET_WEIGHT, 0.18)
        self.assertAlmostEqual(engine.MAX_TURNOVER_PER_REBALANCE, 0.20)
        self.assertTrue(engine.USE_WHOLE_PERCENT_FINAL_WEIGHTS)
        self.assertEqual(engine.WHOLE_PERCENT_STEP_PERCENT, 1)
        self.assertEqual(engine.MIN_WHOLE_PERCENT_NONCASH, 1)
        self.assertAlmostEqual(engine.TRADEABLE_MIN_WEIGHT, 0.01)

    def test_quantized_weights_are_whole_percent_and_sum_to_one(self) -> None:
        weights = pd.Series(
            {
                "SGOV": 0.490,
                "AAA": 0.176,
                "BBB": 0.174,
                "CCC": 0.160,
            }
        )

        result = engine.quantize_whole_percent_weights(weights)

        self.assertAlmostEqual(float(result.sum()), 1.0, places=12)

        for ticker, weight in result.items():
            pct = float(weight) * 100.0
            self.assertAlmostEqual(pct, round(pct), places=9)

            if ticker != engine.CASH_TICKER and weight > 0:
                self.assertGreaterEqual(pct, 1.0)
                self.assertLessEqual(pct, 18.0)

    def test_surviving_non_cash_positions_are_not_rounded_to_zero(self) -> None:
        weights = pd.Series(
            {
                "SGOV": 0.90,
                "AAA": 0.01,
                "BBB": 0.01,
                "CCC": 0.01,
                "DDD": 0.01,
                "EEE": 0.01,
                "FFF": 0.01,
                "GGG": 0.01,
                "HHH": 0.01,
                "III": 0.01,
                "JJJ": 0.01,
            }
        )

        result = engine.quantize_whole_percent_weights(weights)

        self.assertAlmostEqual(float(result.sum()), 1.0, places=12)

        for ticker in weights.index:
            if ticker == engine.CASH_TICKER:
                continue
            self.assertGreaterEqual(float(result[ticker]), 0.01)

    def test_tradeable_display_keeps_one_percent_positions(self) -> None:
        weights = pd.Series(
            {
                "SGOV": 0.90,
                "AAA": 0.09,
                "BBB": 0.01,
            }
        )

        display = engine.make_tradeable_display_weights(weights)

        self.assertIn("BBB", display.index)
        self.assertAlmostEqual(float(display.sum()), 1.0, places=12)


if __name__ == "__main__":
    unittest.main()
