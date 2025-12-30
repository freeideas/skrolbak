# Animation System

Documents the animation model including state variables, velocity semantics, velocity evolution per tick, range boundary behavior, and initialization.

## $REQ_ANIM_001: State Variables Per Axis
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "State variables per axis")

For each axis and degree of freedom (pan-x, pan-y, pan-z, rot-x, rot-y, rot-z), the element must maintain a current value (position/rotation/zoom) and a velocity expressed as a signed percentage per second of the allowed range for that axis.

## $REQ_ANIM_002: Velocity Units
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Velocity semantics")

Velocity must be expressed in units of "percent of allowed range per second". A velocity magnitude of 1% means 1% of that axis's allowed range is traversed in one second. Velocities may be positive or negative, determining direction.

## $REQ_ANIM_003: No Zero Velocity
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Velocity semantics")

Zero velocity for any degree of freedom is not permitted as a stable state. When velocity changes would result in exactly 0%, the system must skip over 0 and choose a non-zero sign, preserving continuous motion.

## $REQ_ANIM_004: Velocity Update Timing
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Velocity evolution")

Velocity must be updated once per second (when the tick counter `t` increments).

## $REQ_ANIM_005: Velocity Magnitude Change
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Velocity evolution")

At each one-second tick, for each axis independently, the velocity magnitude must be either increased by 1 percentage point per second or decreased by 1 percentage point per second. The choice is determined by `prng(t, "{axis}-vel")` and the result must never be 0. Direction (sign) is preserved except when reversed at range boundaries.

## $REQ_ANIM_006: Range Boundary Reversal
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Range boundary behavior")

Motion must be constrained to the computed allowed interval for each axis. Whenever the current value reaches or attempts to exceed an endpoint of the interval, the velocity for that axis must be immediately reversed in sign.

## $REQ_ANIM_007: Initial Position Values
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Initialization")

On element connection to the document, all position values must start at 0 (centered for pan, no rotation for rot, nominal scale for zoom).

## $REQ_ANIM_008: Initial Velocity Assignment
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Initialization")

On element connection, each axis with a non-zero range must be assigned an initial velocity of either -1% or +1%, deterministically chosen using `prng(0, "{axis}-init")` where true = +1 and false = -1, ensuring continuous motion.

## $REQ_ANIM_009: Zero Range Axes Stationary
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Initialization")

Axes with range = 0 must have no velocity and remain stationary.

## $REQ_ANIM_010: Animation Loop Integration
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Animation loop")

A time-based animation loop must integrate velocities over time to update current values along each axis. Once per second, a separate tick must update velocities (increase/decrease magnitude by 1% per second, skipping 0, and handling sign reversals at boundaries).
