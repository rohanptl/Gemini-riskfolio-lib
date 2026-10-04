"""V5.16 plug-in configuration.

Production behavior:
- stale_position: ON (validated V3 logic)
- correlation_control: ON (validated V3 guardrail)
- rsi_momentum: OFF / research
- game_theory_allocator: OFF / research
"""

PLUGIN_CONFIG = {
    "stale_position": {
        "enabled": True,
        "soft_reduction_fraction": 0.50,
    },
    "correlation_control": {
        "enabled": True,
        "corr_threshold": 0.85,
        "max_pair_weight": 0.15,
    },
    "rsi_momentum": {
        "enabled": False,
        "rsi_period": 14,
        "pullback_low": 40.0,
        "pullback_high": 50.0,
        "staged_entry_fraction": 0.50,
        "ema_period": 20,
        "breakout_lookback": 5,
    },
    "game_theory_allocator": {
        "enabled": False,
        "robustness_weight": 0.35,
        "minimum_strategy_weight": 0.0,
    },
}

TARGET_PLUGIN_ORDER = [
    "stale_position",
    "correlation_control",
    "rsi_momentum",
    "game_theory_allocator",
]

RISK_OVERRIDE_PLUGIN_ORDER = [
    "stale_position",
]
