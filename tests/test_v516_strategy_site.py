from pathlib import Path
import tempfile
import unittest

import pandas as pd

from generate_v516_strategy_site import build_site


class V516StrategySiteTests(unittest.TestCase):
    def test_build_site_from_minimal_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_dir = root / "outputs"
            window_dir = output_dir / "walk_forward_windows" / "2023"
            site_dir = root / "site"
            window_dir.mkdir(parents=True)

            pd.DataFrame(
                {
                    "Weight": [0.50, 0.30, 0.20],
                },
                index=["SGOV", "AAA", "BBB"],
            ).to_csv(
                window_dir / "final_target_weights_tradeable.csv"
            )

            pd.DataFrame(
                {
                    "Total Return": [0.25, 0.20],
                    "CAGR": [0.12, 0.10],
                    "Annual Volatility": [0.11, 0.14],
                    "Sharpe": [1.0, 0.7],
                    "Max Drawdown": [-0.09, -0.14],
                    "EV": [0.0004, 0.0003],
                    "MAR": [1.33, 0.71],
                    "Calmar": [1.10, 0.65],
                    "PF": [1.2, 1.1],
                    "GtP": [0.2, 0.1],
                    "Sortino": [1.4, 0.9],
                    "Daily Observations": [500, 500],
                },
                index=["Strategy", "SPY"],
            ).to_csv(window_dir / "benchmark_comparison.csv")

            path = build_site(
                output_dir=output_dir,
                window="2023",
                site_dir=site_dir,
                parity_dir=root / "missing-parity",
                live_target_dir=root / "missing-live-target",
            )

            self.assertTrue(path.exists())
            self.assertTrue((site_dir / "strategy_snapshot.json").exists())
            self.assertTrue((site_dir / "assets" / "allocation.png").exists())

            page = path.read_text(encoding="utf-8")
            self.assertIn("V5.16 ETF Rotation", page)
            self.assertIn("Current target", page)
            self.assertIn("Benchmark comparison", page)
            self.assertIn("Parity UNKNOWN", page)


if __name__ == "__main__":
    unittest.main()
