# Animated Background Component

Documents the `<animated-background>` custom HTML element, its attributes, and usage as a full-viewport tiled background.

## $REQ_ANIMATEDBG_001: Custom HTML Element
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Web Component")

The component is a custom HTML element named `<animated-background>`.

## $REQ_ANIMATEDBG_002: Source Image Attribute
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Attributes")

The element accepts a `src` attribute specifying the path to the background image.

## $REQ_ANIMATEDBG_003: Start Offset Attribute
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Attributes")

The element accepts a `start-offset` attribute specifying a time offset in seconds for debugging purposes. Defaults to 0.

## $REQ_ANIMATEDBG_004: X-Pan Velocity Attributes
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Attributes")

The element accepts `x-pan-pps-min` and `x-pan-pps-max` attributes specifying X-axis pan velocity bounds in pixels per second. Default to -5 and 5 respectively.

## $REQ_ANIMATEDBG_005: Y-Pan Velocity Attributes
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Attributes")

The element accepts `y-pan-pps-min` and `y-pan-pps-max` attributes specifying Y-axis pan velocity bounds in pixels per second. Default to -5 and 5 respectively.

## $REQ_ANIMATEDBG_006: X-Rotation Attributes
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Attributes")

The element accepts `x-rot-min` and `x-rot-max` attributes specifying X-axis rotation bounds in degrees. Default to -10 and 10 respectively.

## $REQ_ANIMATEDBG_007: Y-Rotation Attributes
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Attributes")

The element accepts `y-rot-min` and `y-rot-max` attributes specifying Y-axis rotation bounds in degrees. Default to -10 and 10 respectively.

## $REQ_ANIMATEDBG_008: Z-Rotation Attributes
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Attributes")

The element accepts `z-rot-min` and `z-rot-max` attributes specifying Z-axis rotation bounds in degrees. Default to -20 and 20 respectively.

## $REQ_ANIMATEDBG_009: Zoom Attributes
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Attributes")

The element accepts `z-pan-min` and `z-pan-max` attributes specifying zoom bounds in percent. Default to 50 and 200 respectively.

## $REQ_ANIMATEDBG_010: Fills Parent Container
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Usage")

The element fills its parent container.

## $REQ_ANIMATEDBG_011: Initial Camera State
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

Initial state has all velocities at 0, all rotations at 0 degrees, and zoom at 100%.

## $REQ_ANIMATEDBG_012: X-Pan Motion
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

The background supports horizontal scroll (X-pan) as an unbounded parameter measured in pixels per second.

## $REQ_ANIMATEDBG_013: Y-Pan Motion
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

The background supports vertical scroll (Y-pan) as an unbounded parameter measured in pixels per second.

## $REQ_ANIMATEDBG_014: X-Rotation Motion
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

The background supports tilt forward/backward (X-rotation) as a bounded parameter measured in degrees.

## $REQ_ANIMATEDBG_015: Y-Rotation Motion
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

The background supports tilt left/right (Y-rotation) as a bounded parameter measured in degrees.

## $REQ_ANIMATEDBG_016: Z-Rotation Motion
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

The background supports in-plane spin (Z-rotation) as a bounded parameter measured in degrees.

## $REQ_ANIMATEDBG_017: Zoom Motion
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Camera Model")

The background supports zoom (scale) as a bounded parameter measured in percent.

## $REQ_ANIMATEDBG_018: Deterministic Animation
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Animation System")

Animation uses a deterministic noise function: `noise(seconds, channel) = frac(sin(seconds × 12.9898 + channel × 78.233) × 43758.5453)`.

## $REQ_ANIMATEDBG_019: Bounded Parameter Behavior
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Boundary Behavior")

For bounded parameters (rotations, zoom), value clamps at limit and velocity reverses.

## $REQ_ANIMATEDBG_020: Unbounded Parameter Behavior
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Boundary Behavior")

For unbounded parameters (pan), velocity clamps at limit and acceleration reverses.

## $REQ_ANIMATEDBG_021: Frame-Rate Independence
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Frame-Rate Independence")

Animation state is computed analytically from elapsed time. Given time T, position is computed as the integral of velocity from 0 to T, guaranteeing identical output regardless of frame rate.

## $REQ_ANIMATEDBG_022: Debug Time Logging
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Debug Logging")

The component logs the current time offset to the console once per second in the format `t=0`, `t=1`, `t=2`, etc.

## $REQ_ANIMATEDBG_023: Dynamic Tiling Coverage
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Dynamic Tiling")

The viewport is always fully covered by tiles regardless of transform state. Tiles are rendered dynamically based on which grid cells intersect the visible area.

## $REQ_ANIMATEDBG_024: 3D Perspective Effect
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "3D Perspective")

CSS perspective is applied for realistic foreshortening on X/Y rotations.

## $REQ_ANIMATEDBG_025: Background Z-Index
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Z-Index")

The background renders behind all other content (lowest z-index).

## $REQ_ANIMATEDBG_026: Animation Visible Behind Content
**Source:** ./specs/TESTING.md (Section: "Test 3: Animation")

The background visibly animates (pan, rotation, zoom) over time while foreground content remains stationary.

## $REQ_ANIMATEDBG_027: Isolated X-Pan Motion
**Source:** ./specs/TESTING.md (Section: "X-Pan Only")

When only X-pan parameters are non-zero, the background exhibits horizontal scroll motion only.

## $REQ_ANIMATEDBG_028: Isolated Y-Pan Motion
**Source:** ./specs/TESTING.md (Section: "Y-Pan Only")

When only Y-pan parameters are non-zero, the background exhibits vertical scroll motion only.

## $REQ_ANIMATEDBG_029: Isolated X-Rotation Motion
**Source:** ./specs/TESTING.md (Section: "X-Rotation Only")

When only X-rotation parameters are non-zero, the background exhibits forward/backward tilt with perspective distortion.

## $REQ_ANIMATEDBG_030: Isolated Y-Rotation Motion
**Source:** ./specs/TESTING.md (Section: "Y-Rotation Only")

When only Y-rotation parameters are non-zero, the background exhibits left/right tilt with perspective distortion.

## $REQ_ANIMATEDBG_031: Isolated Z-Rotation Motion
**Source:** ./specs/TESTING.md (Section: "Z-Rotation Only")

When only Z-rotation parameters are non-zero, the background exhibits in-plane rotation only.

## $REQ_ANIMATEDBG_032: Isolated Zoom Motion
**Source:** ./specs/TESTING.md (Section: "Zoom Only")

When only zoom parameters allow variation, the background exhibits uniform scaling from center.
