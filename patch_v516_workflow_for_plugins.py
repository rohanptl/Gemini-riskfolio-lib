from pathlib import Path

path = Path(".github/workflows/v516_rolling_asof_allocation_workflow.yml")

if not path.exists():
    raise FileNotFoundError(path)

text = path.read_text(encoding="utf-8")

text = text.replace(
    "- name: Run production V5.16 Mom126Skip21 allocation",
    "- name: Run production V5.16 modular strategy pipeline",
)

anchor = (
    "            outputs_option2_v5_16_score_tilted_cvar/"
    "walk_forward_windows/2023/risk_overlay_summary_by_rebalance.csv"
)

extra = (
    anchor
    + "\n"
    + "            outputs_option2_v5_16_score_tilted_cvar/"
    "walk_forward_windows/2023/strategy_plugin_adjustments.csv"
    + "\n"
    + "            outputs_option2_v5_16_score_tilted_cvar/"
    "walk_forward_windows/2023/strategy_plugin_summary_by_rebalance.csv"
)

if "strategy_plugin_adjustments.csv" not in text:
    if anchor not in text:
        raise RuntimeError("Artifact anchor not found in workflow.")
    text = text.replace(anchor, extra, 1)

path.write_text(text, encoding="utf-8")
print(f"Updated {path}")
