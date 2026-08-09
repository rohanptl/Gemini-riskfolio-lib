from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

def allocation_run_allowed(
    lock_dir: Path, current_month: str, replace_official_target: bool = False
) -> tuple[bool, str | None]:
    datetime.strptime(current_month, "%Y-%m")
    metadata_path = lock_dir / "current_target.json"
    if not metadata_path.exists():
        return True, None
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    locked_month = str(metadata["official_month"])
    if locked_month == current_month and not replace_official_target:
        return False, locked_month
    return True, locked_month


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prevent an accidental second official allocation in one month."
    )
    parser.add_argument("--lock-dir", type=Path, default=Path("live_targets/v516"))
    parser.add_argument(
        "--current-month",
        default=datetime.now(timezone.utc).strftime("%Y-%m"),
    )
    parser.add_argument("--replace-official-target", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    allowed, locked_month = allocation_run_allowed(
        args.lock_dir,
        args.current_month,
        replace_official_target=args.replace_official_target,
    )
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with Path(github_output).open("a", encoding="utf-8") as handle:
            handle.write(f"should_run={str(allowed).lower()}\n")
            handle.write(f"locked_month={locked_month or ''}\n")
    if allowed:
        print(f"Allocation run allowed for official month {args.current_month}.")
    else:
        print(
            f"Official target for {args.current_month} is already locked; "
            "no new target will be calculated or published."
        )


if __name__ == "__main__":
    main()
