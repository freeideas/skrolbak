# Camera Model

Documents the six degrees of freedom for the virtual camera: X-pan, Y-pan, X-rotation, Y-rotation, Z-rotation, and zoom.

## $REQ_CAMERA_001: Six Degrees of Freedom
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

The virtual camera MUST support six degrees of freedom: X-pan, Y-pan, X-rotation, Y-rotation, Z-rotation, and Zoom.

## $REQ_CAMERA_002: X-Pan Degree of Freedom
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

X-pan MUST measure horizontal scroll velocity in pixels/sec with infinite bounds.

## $REQ_CAMERA_003: Y-Pan Degree of Freedom
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

Y-pan MUST measure vertical scroll velocity in pixels/sec with infinite bounds.

## $REQ_CAMERA_004: X-Rotation Degree of Freedom
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

X-rotation MUST measure forward/backward tilt in degrees with bounded range.

## $REQ_CAMERA_005: Y-Rotation Degree of Freedom
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

Y-rotation MUST measure left/right tilt in degrees with bounded range.

## $REQ_CAMERA_006: Z-Rotation Degree of Freedom
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

Z-rotation MUST measure in-plane spin in degrees with bounded range.

## $REQ_CAMERA_007: Zoom Degree of Freedom
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

Zoom MUST measure scale in percent with bounded range (50-200%).

## $REQ_CAMERA_008: Initial Camera State
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

Initial state MUST be: all velocities 0, all rotations 0°, zoom 100%.

## $REQ_CAMERA_009: Bounded Parameter Boundary Behavior
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Boundary Behavior")

For bounded parameters (rotations, zoom), the value MUST clamp at the limit and velocity MUST reverse.

## $REQ_CAMERA_010: Unbounded Parameter Boundary Behavior
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Boundary Behavior")

For unbounded parameters (pan), the velocity MUST clamp at the limit and acceleration MUST reverse.

## $REQ_CAMERA_011: Frame-Rate Independent Animation
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Frame-Rate Independence")

Animation state MUST be computed analytically from elapsed time, guaranteeing identical output regardless of frame rate.

## $REQ_CAMERA_012: X-Pan Motion Isolation
**Source:** ./specs/TESTING.md (Section: "X-Pan Only")

When configured with only X-pan enabled, the background MUST exhibit horizontal scroll only.

## $REQ_CAMERA_013: Y-Pan Motion Isolation
**Source:** ./specs/TESTING.md (Section: "Y-Pan Only")

When configured with only Y-pan enabled, the background MUST exhibit vertical scroll only.

## $REQ_CAMERA_014: X-Rotation Motion Isolation
**Source:** ./specs/TESTING.md (Section: "X-Rotation Only")

When configured with only X-rotation enabled, the background MUST exhibit forward/backward tilt with perspective distortion.

## $REQ_CAMERA_015: Y-Rotation Motion Isolation
**Source:** ./specs/TESTING.md (Section: "Y-Rotation Only")

When configured with only Y-rotation enabled, the background MUST exhibit left/right tilt with perspective distortion.

## $REQ_CAMERA_016: Z-Rotation Motion Isolation
**Source:** ./specs/TESTING.md (Section: "Z-Rotation Only")

When configured with only Z-rotation enabled, the background MUST exhibit in-plane rotation only.

## $REQ_CAMERA_017: Zoom Motion Isolation
**Source:** ./specs/TESTING.md (Section: "Zoom Only")

When configured with only Zoom enabled, the background MUST exhibit uniform scaling from center.
