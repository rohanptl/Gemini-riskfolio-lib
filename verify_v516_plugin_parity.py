from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

from strategy_config import (
    PLUGIN_CONFIG,
    RISK_OVERRIDE_PLUGIN_ORDER,
    TARGET_PLUGIN_ORDER,
)


DEFAULT_BASELINE_DIR = Path("parity_baselines/v516")
DEFAULT_UNIVERSE_FILE = Path("Wealthfront_ETF_Categorization.csv")
ENGINE_PATH = Path(
    "main_option2_all_etfs_v5_16_rolling_asof_monthly_attribution_dynamic_enddate.py"
)

FILE_RULES = {
    "final_target_weights_tradeable.csv": {
        "tolerance": 1e-9,
        "allowed_extra_columns": set(),
        "required": True,
    },
    "benchmark_comparison.csv": {
        "tolerance": 5e-6,
        "allowed_extra_columns": set(),
        "required": False,
    },
    "turnover_by_rebalance.csv": {
        "tolerance": 5e-6,
        "allowed_extra_columns": set(),
        "required": False,
    },
    "risk_overlay_summary_by_rebalance.csv": {
        "tolerance": 5e-6,
        "allowed_extra_columns": {
            "EnabledTargetPlugins",
            "EnabledRiskOverridePlugins",
        },
        "required": False,
    },
}


def _load_engine():
    spec = importlib.util.spec_from_file_location("v516_parity_engine", ENGINE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {ENGINE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def _git_head() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value or None


def _enabled_plugins(order: list[str]) -> list[str]:
    return [
        name
        for name in order
        if bool(PLUGIN_CONFIG.get(name, {}).get("enabled", False))
    ]


def production_snapshot(universe_file: Path = DEFAULT_UNIVERSE_FILE) -> dict:
    engine = _load_engine()
    return {
        "universe_git_blob_sha": _git_blob_sha(universe_file),
        "max_risk_asset_weight": float(engine.MAX_RISK_ASSET_WEIGHT),
        "max_turnover_per_rebalance": float(engine.MAX_TURNOVER_PER_REBALANCE),
        "use_whole_percent_final_weights": bool(
            engine.USE_WHOLE_PERCENT_FINAL_WEIGHTS
        ),
        "whole_percent_step_percent": int(engine.WHOLE_PERCENT_STEP_PERCENT),
        "min_whole_percent_noncash": int(engine.MIN_WHOLE_PERCENT_NONCASH),
        "tradeable_min_weight": float(engine.TRADEABLE_MIN_WEIGHT),
        "enabled_target_plugins": _enabled_plugins(TARGET_PLUGIN_ORDER),
        "enabled_risk_override_plugins": _enabled_plugins(
            RISK_OVERRIDE_PLUGIN_ORDER
        ),
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

    both_nan = np.isnan(a) & np.isnan(b)
    diff[both_nan] = 0.0

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
        return False, f"row count differs: {len(left)} vs {len(right)}"

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
        col for col in extra_in_modular if col not in allowed_extra_columns
    ]

    if unexpected_extra:
        return (
            False,
            f"unexpected modular-only columns: {unexpected_extra}",
        )

    common_columns = [
        col for col in baseline_columns if col in right.columns
    ]

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


def load_manifest(baseline_dir: Path) -> dict:
    path = baseline_dir / "manifest.json"
    if not path.exists():
        raise FileNotFoundError(f"Missing parity manifest: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_manifest(
    baseline_dir: Path,
    universe_file: Path = DEFAULT_UNIVERSE_FILE,
) -> tuple[bool, list[str]]:
    manifest = load_manifest(baseline_dir)
    messages: list[str] = []
    ok = True

    if manifest.get("format_version") != 1:
        ok = False
        messages.append(
            f"format_version expected 1, got {manifest.get('format_version')!r}"
        )

    expected = production_snapshot(universe_file)
    recorded = manifest.get("production_snapshot", {})

    for key, expected_value in expected.items():
        actual_value = recorded.get(key)
        if actual_value != expected_value:
            ok = False
            messages.append(
                f"{key} mismatch: baseline={actual_value!r}, "
                f"current={expected_value!r}"
            )

    frozen_files = set(manifest.get("frozen_files", []))
    for filename, rules in FILE_RULES.items():
        path = baseline_dir / filename
        if rules["required"]:
            if filename not in frozen_files:
                ok = False
                messages.append(
                    f"required file not declared frozen: {filename}"
                )
            if not path.exists():
                ok = False
                messages.append(f"required baseline file missing: {filename}")
        elif filename in frozen_files and not path.exists():
            ok = False
            messages.append(
                f"manifest declares frozen file but it is missing: {filename}"
            )

    if ok:
        messages.append(
            "manifest matches the current V5.16 production configuration "
            "and ETF universe"
        )

    return ok, messages


def _infer_signal_date(source_dir: Path) -> str | None:
    turnover_path = source_dir / "turnover_by_rebalance.csv"
    if not turnover_path.exists():
        return None

    df = pd.read_csv(turnover_path)
    if "Date" not in df.columns or df.empty:
        return None

    dates = pd.to_datetime(df["Date"], errors="coerce").dropna()
    if dates.empty:
        return None

    return dates.max().date().isoformat()


def freeze_baseline(
    source_dir: Path,
    baseline_dir: Path,
    universe_file: Path = DEFAULT_UNIVERSE_FILE,
    source_signal_date: str | None = None,
    force: bool = False,
) -> dict:
    if not source_dir.exists():
        raise FileNotFoundError(f"Source output directory not found: {source_dir}")

    existing = list(baseline_dir.glob("*")) if baseline_dir.exists() else []
    if existing and not force:
        raise FileExistsError(
            f"{baseline_dir} is not empty. Use --force only after a "
            "validated production run."
        )

    baseline_dir.mkdir(parents=True, exist_ok=True)

    frozen_files: list[str] = []
    for filename, rules in FILE_RULES.items():
        src = source_dir / filename
        dst = baseline_dir / filename

        if not src.exists():
            if rules["required"]:
                raise FileNotFoundError(
                    f"Validated output is missing required parity file: {src}"
                )
            continue

        shutil.copy2(src, dst)
        frozen_files.append(filename)

    signal_date = source_signal_date or _infer_signal_date(source_dir)

    manifest = {
        "format_version": 1,
        "strategy": "V5.16",
        "purpose": (
            "Frozen regression fixture for implementation/parity validation; "
            "not a parameter-optimization baseline."
        ),
        "source_signal_date": signal_date,
        "reference_commit": _git_head(),
        "production_snapshot": production_snapshot(universe_file),
        "frozen_files": frozen_files,
        "file_tolerances": {
            filename: rules["tolerance"]
            for filename, rules in FILE_RULES.items()
            if filename in frozen_files
        },
    }

    (baseline_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return manifest


def run_parity(
    baseline_dir: Path,
    modular_dir: Path,
    universe_file: Path = DEFAULT_UNIVERSE_FILE,
    tolerance_override: float | None = None,
) -> int:
    failures = 0

    manifest_ok, manifest_messages = validate_manifest(
        baseline_dir=baseline_dir,
        universe_file=universe_file,
    )
    for message in manifest_messages:
        print(f"{'PASS' if manifest_ok else 'FAIL'} manifest: {message}")

    if not manifest_ok:
        failures += 1

    manifest = load_manifest(baseline_dir)
    frozen_files = set(manifest.get("frozen_files", []))

    for filename, rules in FILE_RULES.items():
        if filename not in frozen_files:
            print(
                f"SKIP {filename}: not frozen in this baseline fixture"
            )
            continue

        baseline_path = baseline_dir / filename
        modular_path = modular_dir / filename

        if not modular_path.exists():
            print(
                f"FAIL {filename}: modular output missing: {modular_path}"
            )
            failures += 1
            continue

        tolerance = (
            tolerance_override
            if tolerance_override is not None
            else float(rules["tolerance"])
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
        print(f"PARITY FAILED: {failures} comparison(s) failed.")
        return 1

    print()
    print(
        "PARITY PASSED: current V5.16 output matches the frozen "
        "implementation baseline within production-safe tolerances."
    )
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Freeze or verify the V5.16 implementation regression baseline. "
            "This tool validates implementation parity; it does not optimize "
            "strategy parameters."
        )
    )
    parser.add_argument(
        "--baseline-dir",
        default=str(DEFAULT_BASELINE_DIR),
        help="Frozen parity fixture directory.",
    )
    parser.add_argument(
        "--modular-dir",
        default=None,
        help="Current V5.16 output directory to compare with the baseline.",
    )
    parser.add_argument(
        "--freeze-baseline-from",
        default=None,
        help=(
            "Copy parity files from a previously validated V5.16 output "
            "directory and write a manifest."
        ),
    )
    parser.add_argument(
        "--source-signal-date",
        default=None,
        help="Optional YYYY-MM-DD signal date recorded when freezing.",
    )
    parser.add_argument(
        "--universe-file",
        default=str(DEFAULT_UNIVERSE_FILE),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow replacement of an existing frozen baseline.",
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=None,
        help=(
            "Optional global comparison tolerance override. Normally leave "
            "unset so file-specific production tolerances are used."
        ),
    )
    args = parser.parse_args()

    baseline_dir = Path(args.baseline_dir)
    universe_file = Path(args.universe_file)

    if args.freeze_baseline_from:
        manifest = freeze_baseline(
            source_dir=Path(args.freeze_baseline_from),
            baseline_dir=baseline_dir,
            universe_file=universe_file,
            source_signal_date=args.source_signal_date,
            force=args.force,
        )
        print(f"Frozen V5.16 parity baseline: {baseline_dir}")
        print(f"Files: {', '.join(manifest['frozen_files'])}")
        print(
            "Universe Git blob SHA: "
            f"{manifest['production_snapshot']['universe_git_blob_sha']}"
        )
        return

    if not args.modular_dir:
        parser.error(
            "--modular-dir is required unless --freeze-baseline-from is used"
        )

    raise SystemExit(
        run_parity(
            baseline_dir=baseline_dir,
            modular_dir=Path(args.modular_dir),
            universe_file=universe_file,
            tolerance_override=args.tolerance,
        )
    )


if __name__ == "__main__":
    main()
