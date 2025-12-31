# Deterministic Replay

Documents reproducible animation state via the `t` attribute fast-forward, seeded PRNG function, and console tick logging.

## $REQ_REPLAY_001: Time Counter Starts at t Attribute Value
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

A global tick counter `t` starts at the value of the `t` attribute (default 0) when the element connects to the document.

## $REQ_REPLAY_002: Time Counter Increments Each Second
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

The tick counter `t` increments by 1 each second, at the same time as velocity updates.

## $REQ_REPLAY_003: Console Tick Logging
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

On each tick, log to console: `t=0`, `t=1`, `t=2`, etc.

## $REQ_REPLAY_004: Animation Begins at Specified Tick
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

After fast-forward simulation, normal animation and console logging begin at t=N.

## $REQ_REPLAY_005: Deterministic PRNG Function
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

All random choices use a deterministic function `prng(t, salt) → boolean` where `t` is the current tick counter and `salt` is a unique string for each decision point (e.g., `"panX-init"`, `"rotY-vel"`). Same inputs always produce the same result.

## $REQ_REPLAY_006: Initial Velocity Direction via PRNG
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

Initial velocity direction for each axis is determined by `prng(0, "{axis}-init")` where true = +1 and false = -1.

## $REQ_REPLAY_007: Velocity Magnitude Change via PRNG
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

Velocity magnitude change at each tick for each axis is determined by `prng(t, "{axis}-vel")` where true = +1 and false = -1.

## $REQ_REPLAY_008: Fast-Forward Produces Identical State
**Source:** ./specs/TESTING.md (Section: "Deterministic Replay Test")

Setting `t="29"` and waiting 1 second to reach t=30 produces identical position values as running from `t="0"` for 30 seconds, within floating-point tolerance.
