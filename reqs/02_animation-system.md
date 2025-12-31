# Animation System

Documents the continuous animation behavior: state variables per axis, velocity semantics, velocity evolution each tick, range boundary reversal, and initialization.

## $REQ_ANIM_001: State Variables Per Axis
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "State variables per axis")

For each of the six degrees of freedom (`pan-x`, `pan-y`, `pan-z`, `rot-x`, `rot-y`, `rot-z`), the element must maintain a current value (position/rotation/zoom) and a velocity expressed as a signed percentage per second of the allowed range.

## $REQ_ANIM_002: Velocity Units
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Velocity semantics")

Velocity units must be "percent of allowed range per second", where a velocity magnitude of 1% means 1% of that axis's allowed range is traversed in one second. Velocities may be positive or negative, determining direction.

## $REQ_ANIM_003: No Zero Velocity
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Velocity semantics")

Zero velocity for any degree of freedom with non-zero range is not permitted as a stable state. Transitions that would result in exactly 0% must skip over 0 and choose a non-zero sign, preserving continuous motion.

## $REQ_ANIM_004: Velocity Update Frequency
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Velocity evolution")

Velocity must be updated once per second (when `t` increments). Time discretization for velocity updates is per-second.

## $REQ_ANIM_005: Velocity Magnitude Change
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Velocity evolution")

At each one-second tick, the magnitude of each axis's velocity must be either increased by 1 percentage point per second or decreased by 1 percentage point per second. The choice is determined by `prng(t, "{axis}-vel")` and the result must never be 0. Direction (sign) is preserved except when reversed at range boundaries.

## $REQ_ANIM_006: Range Boundary Reversal
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Range boundary behavior")

For each axis, motion must be constrained to the computed allowed interval. Whenever the current value reaches or attempts to exceed an endpoint of that interval, the corresponding velocity for that axis must be immediately reversed in sign.

## $REQ_ANIM_007: Initial Position Values
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Initialization")

On element connection to the document, all position values must start at 0 (centered for pan, no rotation for rot, nominal scale for zoom).

## $REQ_ANIM_008: Initial Velocity Assignment
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Initialization")

On element connection, each axis with a non-zero range must be assigned an initial velocity of either -1% or +1%, deterministically chosen based on `prng(0, "{axis}-init")` where true = +1 and false = -1. This ensures continuous motion.

## $REQ_ANIM_009: Zero Range Axis Behavior
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Initialization")

Axes with range = 0 must have no velocity and remain stationary.

## $REQ_ANIM_010: Animation Loop Integration
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Animation loop")

A time-based animation loop must integrate velocities over time to update current values along each axis. Position updates must use effective velocity multiplied by delta time.

## $REQ_ANIM_011: Tick Console Logging
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

On each tick, the element must log to console: `t=0`, `t=1`, `t=2`, etc.

## $REQ_ANIM_012: Boost Effective Velocity
**Source:** ./specs/BOOST.md (Section: "Effective Velocity")

The effective velocity for each axis must be the sum of the base velocity and the boost: `effectiveVelocity = baseVelocity + boost`. Position updates must use this effective velocity.

## $REQ_ANIM_013: Boost Decay Per Tick
**Source:** ./specs/BOOST.md (Section: "Decay")

At each tick (when `t` increments), boost must decay toward zero: if boost > 0, boost = boost - 1 (not below 0); if boost < 0, boost = boost + 1 (not above 0); if boost is between -1 and +1, boost = 0. Decay is applied after velocity updates but before position updates.

## $REQ_ANIM_014: Boost Boundary Reversal
**Source:** ./specs/BOOST.md (Section: "Boundary Behavior")

When position reaches or exceeds a boundary, both base velocity and boost velocity must be reversed (sign flipped) to ensure both velocity components move the position away from the boundary.

## $REQ_ANIM_015: Boost Initial Value
**Source:** ./specs/BOOST.md (Section: "Initialization")

All boost values must start at 0 when the element connects to the document.

## $REQ_ANIM_016: Boost Not Simulated on Fast-Forward
**Source:** ./specs/BOOST.md (Section: "Initialization")

When using the `t` attribute for fast-forward, boost values are not simulated and remain at 0.
