# Deterministic Replay

Documents the seeded pseudo-random function and the `t` attribute fast-forward mechanism for reproducible animation states.

## $REQ_REPLAY_001: Time Counter Initialization
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

The global tick counter `t` starts at the value of the `t` attribute (default 0) when the element connects.

## $REQ_REPLAY_002: Time Counter Increment
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

The tick counter `t` increments by 1 each second (at the same time as velocity updates).

## $REQ_REPLAY_003: Tick Console Logging
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

On each tick, the element logs to console: `t=0`, `t=1`, `t=2`, etc.

## $REQ_REPLAY_004: Fast-Forward Simulation
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

When the `t` attribute is set to a value N > 0, the element fast-forwards to that state on initialization by simulating state from t=0 to t=N-1 without rendering (instant computation), then begins normal animation and console logging at t=N.

## $REQ_REPLAY_005: Deterministic PRNG Function
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

All random choices use a deterministic function `prng(t, salt) → boolean` where `t` is the current tick counter and `salt` is a unique string for each decision point. The function is deterministic: same `t` and `salt` always produce the same result.

## $REQ_REPLAY_006: PRNG Initial Velocity Direction
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

Initial velocity direction for each axis is determined by `prng(0, "{axis}-init")` where true = +1 and false = -1.

## $REQ_REPLAY_007: PRNG Velocity Magnitude Change
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

Velocity magnitude change at each tick is determined by `prng(t, "{axis}-vel")` where true = +1 and false = -1.

## $REQ_REPLAY_008: Fast-Forward State Equivalence
**Source:** ./specs/TESTING.md (Section: "Deterministic Replay Test")

An element with the `t` attribute set to N must produce identical position values at tick N as an element that ran in real-time from t=0 to t=N (within floating-point tolerance).
