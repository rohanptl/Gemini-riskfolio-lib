from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


FILE_RULES = {
    "final_target_weights_tradeable.csv": {
        "tolerance": 1e-6,
        "allowed_extra_columns": set(),
    },
    "benchmark_comparison.csv": {
        "tolerance": 5e-6,
        "allowed_extra_columns": set(),
    },
    "turnover_by_rebalance.csv": {
        "tolerance": 5e-6,
        "allowed_extra_columns": set(),
    },
    "risk_overlay_summary_by_rebalance.csv": {
        "tolerance": 5e-6,
        "allowed_extra_columns": {
            "EnabledTargetPlugins",
            "EnabledRiskOverridePlugins",
        },
    },
}


def _numeric_columns(
    left: pd.DataFrame,
    right: pd.DataFrame,
    common_columns: list[str],
) -> list[str]:
    return [
        col
        for col in common_columns
        if pd.api.types.is_numeric_dtype(left[col])
        and pd.api.types.is_numeric_dtype(right[col])
    ]


def _max_numeric_diff(
    left: pd.DataFrame,
    right: pd.DataFrame,
    numeric_columns: list[str],
) -> float:
    if not numeric_columns or len(left) == 0:
        return 0.0

    a = left[numeric_columns].reset_index(drop=True).to_numpy(dtype=float)
    b = right[numeric_columns].reset_index(drop=True).to_numpy(dtype=float)

    diff = np.abs(a - b)

    # Treat paired NaNs as equal.
    both_nan = np.isnan(a) & np.isnan(b)
    diff[both_nan] = 0.0

    # A NaN on only one side is a real mismatch.
    one_nan = np.isnan(a) ^ np.isnan(b)
    if np.any(one_nan):
        return float("inf")

    finite = diff[np.isfinite(diff)]
    return float(finite.max()) if finite.size else 0.0


def _non_numeric_mismatches(
    left: pd.DataFrame,
    right: pd.DataFrame,
    common_columns: list[str],
    numeric_columns: list[str],
) -> list[str]:
    numeric_set = set(numeric_columns)
    mismatches: list[str] = []

    for col in common_columns:
        if col in numeric_set:
            continue

        l = left[col].reset_index(drop=True).fillna("<NA>").astype(str)
        r = right[col].reset_index(drop=True).fillna("<NA>").astype(str)

        if not l.equals(r):
            mismatches.append(col)

    return mismatches


def compare_file(
    baseline_path: Path,
    modular_path: Path,
    tolerance: float,
    allowed_extra_columns: set[str],
) -> tuple[bool, str]:
    left = pd.read_csv(baseline_path)
    right = pd.read_csv(modular_path)

    if len(left) != len(right):
        return (
            False,
            f"row count differs: {len(left)} vs {len(right)}",
        )

    baseline_columns = list(left.columns)
    modular_columns = list(right.columns)

    missing_from_modular = [
        col for col in baseline_columns if col not in right.columns
    ]
    if missing_from_modular:
        return (
            False,
            f"baseline columns missing from modular: {missing_from_modular}",
        )

    extra_in_modular = [
        col for col in modular_columns if col not in left.columns
    ]
    unexpected_extra = [
        col for col in extra_in_modular
        if col not in allowed_extra_columns
    ]

    if unexpected_extra:
        return (
            False,
            f"unexpected modular-only columns: {unexpected_extra}",
        )

    common_columns = [
        col for col in baseline_columns if col in right.columns
    ]

    # Compare in baseline column order.
    left_common = left[common_columns].reset_index(drop=True)
    right_common = right[common_columns].reset_index(drop=True)

    numeric_columns = _numeric_columns(
        left_common,
        right_common,
        common_columns,
    )

    max_numeric_diff = _max_numeric_diff(
        left_common,
        right_common,
        numeric_columns,
    )

    non_numeric_mismatches = _non_numeric_mismatches(
        left_common,
        right_common,
        common_columns,
        numeric_columns,
    )

    ok = (
        max_numeric_diff <= tolerance
        and not non_numeric_mismatches
    )

    details = (
        f"rows={len(left)}, "
        f"baseline_cols={len(baseline_columns)}, "
        f"modular_cols={len(modular_columns)}, "
        f"max_numeric_diff={max_numeric_diff:.12g}, "
        f"tolerance={tolerance:.1e}"
    )

    if extra_in_modular:
        details += f", allowed_extra_columns={extra_in_modular}"

    if non_numeric_mismatches:
        details += (
            f", non_numeric_mismatches={non_numeric_mismatches}"
        )

    return ok, details


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Verify that the modular V5.16 plug-in implementation preserves "
            "the legacy V3 production behavior."
        )
    )
    parser.add_argument("--baseline-dir", required=True)
    parser.add_argument("--modular-dir", required=True)
    parser.add_argument(
        "--tolerance",
        type=float,
        default=None,
        help=(
            "Optional global tolerance override. If omitted, uses strict "
            "file-specific tolerances."
        ),
    )
    args = parser.parse_args()

    baseline_dir = Path(args.baseline_dir)
    modular_dir = Path(args.modular_dir)

    failures = 0

    for filename, rules in FILE_RULES.items():
        baseline_path = baseline_dir / filename
        modular_path = modular_dir / filename

        if not baseline_path.exists() or not modular_path.exists():
            print(
                f"FAIL {filename}: missing file "
                f"(baseline={baseline_path.exists()}, "
                f"modular={modular_path.exists()})"
            )
            failures += 1
            continue

        tolerance = (
            args.tolerance
            if args.tolerance is not None
            else rules["tolerance"]
        )

        ok, details = compare_file(
            baseline_path=baseline_path,
            modular_path=modular_path,
            tolerance=tolerance,
            allowed_extra_columns=rules["allowed_extra_columns"],
        )

        print(f"{'PASS' if ok else 'FAIL'} {filename}: {details}")

        if not ok:
            failures += 1

    if failures:
        print()
        print(
            f"PARITY FAILED: {failures} comparison(s) failed."
        )
        raise SystemExit(1)

    print()
    print(
        "PARITY PASSED: modular V5.16 matches legacy V3 within "
        "production-safe numerical tolerances."
    )


if __name__ == "__main__":
    main()
