from __future__ import annotations

from v516_strategies.correlation_control import CorrelationControlPlugin
from v516_strategies.game_theory_allocator import GameTheoryAllocatorPlugin
from v516_strategies.rsi_momentum import RSIMomentumPlugin
from v516_strategies.stale_position import StalePositionPlugin


PLUGIN_FACTORIES = {
    "stale_position": StalePositionPlugin,
    "correlation_control": CorrelationControlPlugin,
    "rsi_momentum": RSIMomentumPlugin,
    "game_theory_allocator": GameTheoryAllocatorPlugin,
}


def build_plugins(config: dict, order: list[str]) -> list:
    plugins = []

    for name in order:
        plugin_config = dict(config.get(name, {}))
        enabled = bool(plugin_config.pop("enabled", False))

        if not enabled:
            continue

        if name not in PLUGIN_FACTORIES:
            raise KeyError(f"Unknown V5.16 strategy plug-in: {name}")

        plugins.append(PLUGIN_FACTORIES[name](**plugin_config))

    return plugins
