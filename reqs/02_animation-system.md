# Animation System

Documents the deterministic random walk algorithm, boundary behavior for bounded and unbounded parameters, and frame-rate independent computation.

## $REQ_ANIM_001: Initial State
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

At time T=0, all parameters must be in their initial state: all velocities 0, all rotations 0°, zoom 100%.

## $REQ_ANIM_002: Deterministic Noise Function
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Random Walk")

Velocity changes are computed using the noise function: `noise(seconds, channel) = frac(sin(seconds × 12.9898 + channel × 78.233) × 43758.5453)`. Direction is -1 if noise < 0.5, otherwise +1.

## $REQ_ANIM_003: Channel Indices
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Random Walk")

The noise function channel indices are: 0=X-pan, 1=Y-pan, 2=X-rot, 3=Y-rot, 4=Z-rot, 5=Zoom.

## $REQ_ANIM_004: Velocity Acceleration Rate
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Random Walk")

Velocity changes by ±1% of the parameter range per second.

## $REQ_ANIM_005: Maximum Velocity
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Random Walk")

Maximum velocity is ±10% of the parameter range per second.

## $REQ_ANIM_006: Bounded Parameter Boundary Behavior
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Boundary Behavior")

For bounded parameters (rotations and zoom): when the value reaches a limit, it clamps at that limit and velocity reverses.

## $REQ_ANIM_007: Unbounded Parameter Boundary Behavior
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Boundary Behavior")

For unbounded parameters (pan): when velocity reaches its limit, velocity clamps at that limit and acceleration reverses.

## $REQ_ANIM_008: Frame-Rate Independence
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Frame-Rate Independence")

Animation state must be computed analytically from elapsed time, not accumulated per-frame. Given time T, position is computed as the integral of velocity from 0 to T, guaranteeing identical output regardless of frame rate.

## $REQ_ANIM_009: Debug Time Logging
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Debug Logging")

The current time offset must be logged to the console once per second in the format: `t=0`, `t=1`, `t=2`, etc.
