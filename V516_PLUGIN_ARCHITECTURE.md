# V5.16 Plug-in Strategy Architecture

## Objective

Keep the validated V5.16 engine stable while making strategy overlays plug-and-play.

Production defaults intentionally preserve the validated V3 behavior:

- `stale_position`: enabled
- `correlation_control`: enabled
- `rsi_momentum`: disabled / research
- `game_theory_allocator`: disabled / research

Configuration lives in `strategy_config.py`.

## Pipeline stages

1. V5.16 builds the normal target portfolio.
2. Enabled target-overlay plug-ins run in `TARGET_PLUGIN_ORDER`.
3. The normal V5.16 turnover cap is applied.
4. Enabled risk-override plug-ins run in `RISK_OVERRIDE_PLUGIN_ORDER`.
5. The base engine continues with pruning, attribution, and reporting.

This preserves the V3 principle:

- soft stale reductions are normal portfolio rotation and stay inside turnover control;
- correlation adjustments are normal portfolio rotation and stay inside turnover control;
- only hard stale exits may override turnover.

## Files

```text
strategy_config.py
v516_plugins/
    __init__.py
    types.py
    registry.py
    pipeline.py
v516_strategies/
    __init__.py
    stale_position.py
    correlation_control.py
    rsi_momentum.py
    game_theory_allocator.py
main_option2_all_etfs_v5_16_risk_overlay_v3.py
```

## Add a strategy

Create one file under `v516_strategies/`, implement:

```python
class MyStrategyPlugin:
    name = "my_strategy"

    def apply_target(...):
        ...

    def apply_risk_override(...):
        ...
```

Register the class in `v516_plugins/registry.py`, add its configuration to
`strategy_config.py`, and place its name in the desired stage order.

Keep new strategies disabled until their backtests pass.

## RSI momentum plug-in

The initial research implementation does not choose ETFs and never forces an exit.

For a V5.16-requested increase it checks:

- Wilder RSI(14)
- recent RSI pullback into 40-50
- RSI turning upward
- completed weekly close above a rising 20-week SMA
- daily close above EMA20 OR above the previous 5-day high

If confirmation is absent, the default experimental behavior deploys 50% of
the requested increase and holds the other 50% temporarily in SGOV.

It is disabled by default.

## Game-theory allocator plug-in

The initial research implementation is a meta allocator, not a stock picker.

It accepts:

- a strategy x regime payoff matrix,
- optional regime probabilities,
- strategy-specific target portfolios.

It solves a mixed-strategy linear program that maximizes a blend of:

- Bayesian expected payoff, and
- worst-regime (maximin) payoff.

This is a direct way to use incomplete-information and mixed-strategy ideas:
the true market regime is uncertain, so the allocator need not bet everything
on the single regime estimate with the highest probability.

It is disabled by default because V5.16 does not yet generate the required
strategy payoff matrix and alternative strategy target portfolios.

## Validation gate

Before merging the modular refactor, run the same V5.16 command on the same
fixed end date using:

1. current production V3 on `main`;
2. the modular branch.

The following should match (allowing only tiny numerical optimizer noise):

- final target weights,
- benchmark comparison,
- turnover history,
- stale-position action counts,
- correlation action counts,
- walk-forward performance.

Do not enable RSI or game theory for the parity test.
