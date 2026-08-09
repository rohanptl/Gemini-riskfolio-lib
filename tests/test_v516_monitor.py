from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from lock_v516_monthly_target import lock_target, read_target_weights
from monitor_v516_midmonth import build_monitor_result, write_outputs
from check_v516_monthly_target_guard import allocation_run_allowed


class V516TargetLockTests(unittest.TestCase):
    def _write_source(self, root: Path, weight_a: float = 0.6) -> tuple[Path, Path]:
        target = root / "target.csv"
        attribution = root / "attribution.csv"
        pd.DataFrame(
            {"Ticker": ["AAA", "BBB"], "Weight": [weight_a, 1.0 - weight_a]}
        ).to_csv(target, index=False)
        pd.DataFrame(
            {"Date": ["2026-07-07", "2026-08-07"], "Ticker": ["AAA", "AAA"]}
        ).to_csv(attribution, index=False)
        return target, attribution

    def test_same_month_rerun_keeps_official_target(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target, attribution = self._write_source(root, weight_a=0.6)
            lock_dir = root / "lock"
            first = lock_target(
                target,
                attribution,
                lock_dir,
                locked_at_utc="2026-08-09T18:00:00+00:00",
            )
            self.assertTrue(first.changed)
            self._write_source(root, weight_a=0.2)
            second = lock_target(target, attribution, lock_dir)
            self.assertFalse(second.changed)
            locked = read_target_weights(lock_dir / "current_target.csv")
            self.assertAlmostEqual(locked["AAA"], 0.6)

    def test_lock_records_next_month_and_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target, attribution = self._write_source(root)
            lock_dir = root / "lock"
            lock_target(
                target,
                attribution,
                lock_dir,
                source_run_url="https://example.test/run/1",
                locked_at_utc="2026-08-09T18:00:00+00:00",
                allocation_submitted_date_override="2026-08-09",
                live_effective_date_override="2026-08-10",
            )
            metadata = json.loads(
                (lock_dir / "current_target.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["official_month"], "2026-08")
            self.assertEqual(metadata["source_signal_date"], "2026-08-07")
            self.assertEqual(metadata["allocation_submitted_date"], "2026-08-09")
            self.assertEqual(metadata["live_effective_date"], "2026-08-10")
            self.assertEqual(metadata["next_scheduled_rebalance_date"], "2026-09-01")
            self.assertEqual(metadata["source_run_url"], "https://example.test/run/1")

    def test_official_month_can_follow_prior_month_weekend_close(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target, attribution = self._write_source(root)
            lock_dir = root / "lock"
            lock_target(
                target,
                attribution,
                lock_dir,
                official_month_override="2026-09",
                locked_at_utc="2026-09-01T23:30:00+00:00",
            )
            metadata = json.loads(
                (lock_dir / "current_target.json").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata["official_month"], "2026-09")
            self.assertEqual(metadata["rebalance_date"], "2026-08-07")
            self.assertEqual(metadata["next_scheduled_rebalance_date"], "2026-10-01")

    def test_guard_skips_same_month_unless_recovery_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target, attribution = self._write_source(root)
            lock_dir = root / "lock"
            lock_target(
                target,
                attribution,
                lock_dir,
                official_month_override="2026-08",
                locked_at_utc="2026-08-09T18:00:00+00:00",
            )
            allowed, _ = allocation_run_allowed(lock_dir, "2026-08")
            forced, _ = allocation_run_allowed(
                lock_dir, "2026-08", replace_official_target=True
            )
            next_month, _ = allocation_run_allowed(lock_dir, "2026-09")
            self.assertFalse(allowed)
            self.assertTrue(forced)
            self.assertTrue(next_month)


class V516MonitorTests(unittest.TestCase):
    def test_monitor_waits_until_live_effective_date(self) -> None:
        weights = pd.Series([1.0], index=pd.Index(["AAA"], name="Ticker"))
        metadata = {
            "official_month": "2026-08",
            "source_signal_date": "2026-08-07",
            "rebalance_date": "2026-08-07",
            "allocation_submitted_date": "2026-08-09",
            "live_effective_date": "2026-08-10",
            "next_scheduled_rebalance_date": "2026-09-01",
        }
        result = build_monitor_result(
            weights,
            metadata,
            pd.DataFrame(columns=["AAA"], dtype=float),
            pd.Timestamp("2026-08-09"),
        )
        self.assertEqual(result.status, "PENDING_EFFECTIVE_DATE_NO_TRADE")
        self.assertEqual(result.summary["live_effective_date"], "2026-08-10")

    def test_monitor_uses_live_effective_price_as_baseline(self) -> None:
        weights = pd.Series([1.0], index=pd.Index(["AAA"], name="Ticker"))
        metadata = {
            "official_month": "2026-08",
            "source_signal_date": "2026-08-07",
            "rebalance_date": "2026-08-07",
            "allocation_submitted_date": "2026-08-09",
            "live_effective_date": "2026-08-10",
            "next_scheduled_rebalance_date": "2026-09-01",
        }
        prices = pd.DataFrame(
            {"AAA": [90.0, 100.0, 110.0]},
            index=pd.to_datetime(["2026-08-07", "2026-08-10", "2026-08-11"]),
        )
        result = build_monitor_result(
            weights, metadata, prices, pd.Timestamp("2026-08-11")
        )
        self.assertAlmostEqual(
            result.summary["estimated_portfolio_return_since_lock"], 0.10
        )

    def test_monitor_reports_drift_without_changing_target(self) -> None:
        weights = pd.Series(
            [0.5, 0.5], index=pd.Index(["AAA", "BBB"], name="Ticker")
        )
        metadata = {
            "official_month": "2026-08",
            "rebalance_date": "2026-08-07",
            "next_scheduled_rebalance_date": "2026-09-01",
        }
        prices = pd.DataFrame(
            {"AAA": [100.0, 200.0], "BBB": [100.0, 100.0]},
            index=pd.to_datetime(["2026-08-07", "2026-08-10"]),
        )
        result = build_monitor_result(
            weights,
            metadata,
            prices,
            pd.Timestamp("2026-08-10"),
            drift_review_percentage_points=2.0,
        )
        self.assertEqual(result.status, "REVIEW_DRIFT_NO_TRADE")
        self.assertAlmostEqual(
            result.drift.loc["AAA", "EstimatedCurrentWeight"], 2.0 / 3.0
        )
        self.assertAlmostEqual(weights["AAA"], 0.5)
        self.assertEqual(result.summary["policy"], "NO_TRADE_MONITOR_ONLY")

    def test_data_error_report_writes_strict_json(self) -> None:
        weights = pd.Series([1.0], index=pd.Index(["AAA"], name="Ticker"))
        metadata = {
            "official_month": "2026-08",
            "rebalance_date": "2026-08-07",
            "next_scheduled_rebalance_date": "2026-09-01",
        }
        result = build_monitor_result(
            weights,
            metadata,
            pd.DataFrame(columns=["AAA"], dtype=float),
            pd.Timestamp("2026-08-09"),
        )
        result.summary["data_error"] = "Price download returned no data."
        with tempfile.TemporaryDirectory() as directory:
            paths = write_outputs(result, Path(directory))
            payload = json.loads(paths["json"].read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "DATA_ERROR")
            self.assertIsNone(payload["estimated_portfolio_return_since_lock"])


if __name__ == "__main__":
    unittest.main()
