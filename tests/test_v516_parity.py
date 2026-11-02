from pathlib import Path
import tempfile
import unittest

import pandas as pd

import verify_v516_plugin_parity as parity


BASELINE_DIR = Path("parity_baselines/v516")


class V516ParityRegressionTests(unittest.TestCase):
    def test_committed_manifest_matches_current_production_snapshot(self) -> None:
        ok, messages = parity.validate_manifest(BASELINE_DIR)
        self.assertTrue(ok, "\n".join(messages))

    def test_frozen_target_has_production_invariants(self) -> None:
        path = BASELINE_DIR / "final_target_weights_tradeable.csv"
        df = pd.read_csv(path)

        self.assertEqual(list(df.columns), ["Ticker", "Weight"])
        self.assertFalse(df["Ticker"].duplicated().any())
        self.assertIn("SGOV", set(df["Ticker"]))

        weights = df.set_index("Ticker")["Weight"].astype(float)
        self.assertAlmostEqual(float(weights.sum()), 1.0, places=12)

        pct = weights * 100.0
        for ticker, value in pct.items():
            self.assertAlmostEqual(float(value), round(float(value)), places=9)
            if ticker != "SGOV":
                self.assertGreaterEqual(float(value), 1.0)
                self.assertLessEqual(float(value), 18.0)

        noncash = weights.drop("SGOV", errors="ignore")
        self.assertLessEqual(int((noncash > 0).sum()), 15)

    def test_compare_file_detects_weight_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            baseline = tmpdir / "baseline.csv"
            changed = tmpdir / "changed.csv"

            pd.DataFrame(
                {
                    "Ticker": ["SGOV", "AAA"],
                    "Weight": [0.50, 0.50],
                }
            ).to_csv(baseline, index=False)

            pd.DataFrame(
                {
                    "Ticker": ["SGOV", "AAA"],
                    "Weight": [0.49, 0.51],
                }
            ).to_csv(changed, index=False)

            ok, details = parity.compare_file(
                baseline_path=baseline,
                modular_path=changed,
                tolerance=1e-9,
                allowed_extra_columns=set(),
            )

            self.assertFalse(ok)
            self.assertIn("max_numeric_diff", details)

    def test_compare_file_accepts_identical_output(self) -> None:
        path = BASELINE_DIR / "final_target_weights_tradeable.csv"
        ok, details = parity.compare_file(
            baseline_path=path,
            modular_path=path,
            tolerance=1e-9,
            allowed_extra_columns=set(),
        )

        self.assertTrue(ok, details)


if __name__ == "__main__":
    unittest.main()
