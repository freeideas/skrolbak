# Drift-BG Component

Documents the `<drift-bg>` custom HTML element: its interface, coordinate system, animation drivers, follower smoothing system, mouse interaction, and tile rendering behavior.

## $REQ_DRIFTBG_001: Custom Element Tag Name
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "2. Component Interface")

The component must be available as a custom HTML element with tag name `<drift-bg>`.

## $REQ_DRIFTBG_002: Image Source Attribute
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "2. Component Interface")

The component must accept a `src` attribute specifying the URL of the image to display. When the `src` attribute is changed, the new image must load and replace the current one.

## $REQ_DRIFTBG_003: Canvas Fills Component
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "2. Component Interface")

The component must contain a `<canvas>` element that fills the component dimensions.

## $REQ_DRIFTBG_004: Default Background Color
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "2. Component Interface")

The component must have a default background color of black (#000).

## $REQ_DRIFTBG_005: World Coordinate Range
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "3. Coordinate System & Projection")

The logical world must extend from -50 to +50 on both X and Y axes (total range: 100 units).

## $REQ_DRIFTBG_006: Perspective Projection Scaling
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "3. Coordinate System & Projection")

The projection must be calculated such that 100 World Units exactly fill the canvas width when at depth Z=0, using a camera offset of 80 units.

## $REQ_DRIFTBG_007: Spiral Motion Pattern
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "4. Animation Drivers")

In Spiral Mode, the target X and Y positions must follow a spiral pattern with growth speed of 2.0 units/second and a cycle duration of 25 seconds.

## $REQ_DRIFTBG_008: Depth Oscillation
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "4. Animation Drivers")

The target depth (z) must oscillate as a sine wave with period 20 seconds and amplitude 48 units.

## $REQ_DRIFTBG_009: Pitch Oscillation
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "4. Animation Drivers")

The target pitch (v, X-axis tilt) must oscillate as a sine wave with period 13 seconds and maximum tilt of 20 degrees.

## $REQ_DRIFTBG_010: Yaw Oscillation
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "4. Animation Drivers")

The target yaw (w, Y-axis tilt) must oscillate as a cosine wave with period 17 seconds and maximum tilt of 20 degrees.

## $REQ_DRIFTBG_011: Roll Oscillation
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "4. Animation Drivers")

The target roll (u, Z-axis rotation) must oscillate as a sine wave with period 23 seconds and maximum tilt of 20 degrees.

## $REQ_DRIFTBG_012: Follower Smoothing System
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "5. The Follower System")

The visual center of the grid must approach the target state using an easing function rather than snapping instantly.

## $REQ_DRIFTBG_013: Standard Follow Rate
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "5. The Follower System")

The standard follow rate of 10% per second (0.1) must be used for z, v, w, u at all times, and for x, y in Spiral Mode.

## $REQ_DRIFTBG_014: Active Follow Rate
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "5. The Follower System")

The active follow rate of 50% per second (0.5) must be used for x, y only during Mouse Mode.

## $REQ_DRIFTBG_015: Mouse Position Mapping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "6. Interaction Behavior")

When the mouse moves, the component must map the mouse pointer's screen coordinates back to World Coordinates (z=0) to determine a new target x, y position.

## $REQ_DRIFTBG_016: Mouse Mode Activation
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "6. Interaction Behavior")

The component must switch to Mouse Mode when the mouse has moved within the last 2000ms, using the mouse position as target x, y while continuing to calculate z, v, w, u from time.

## $REQ_DRIFTBG_017: Spiral Mode Activation
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "6. Interaction Behavior")

The component must switch to Spiral Mode when the mouse has been inactive for more than 2 seconds, calculating target x, y from the spiral function.

## $REQ_DRIFTBG_018: Tile Grid Configuration
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "7. Rendering & Tiling")

The visual output must be a 15x15 grid of images (indices -7 to +7 on both axes) centered on the follower position.

## $REQ_DRIFTBG_019: Tile Size
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "7. Rendering & Tiling")

Each tile must have a width of 30 World Units, with height based on the image aspect ratio.

## $REQ_DRIFTBG_020: 3D Rotation Order
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "7. Rendering & Tiling")

For each tile, 3D rotation must be applied in the order: Roll (u) around Z, then Yaw (w) around Y, then Pitch (v) around X.

## $REQ_DRIFTBG_021: Tile Perspective Projection
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "7. Rendering & Tiling")

Each tile's transformed 3D point must be projected to 2D screen coordinates with image dimensions scaled based on the perspective scale factor.

## $REQ_DRIFTBG_022: Context Roll Rotation
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "7. Rendering & Tiling")

The 2D drawing context must be rotated by the follower roll (u) to align images visually with the grid rotation.

## $REQ_DRIFTBG_023: Image Placeholder
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "7. Rendering & Tiling")

If the image is not loaded, white dots must be drawn as placeholders.

## $REQ_DRIFTBG_024: Console State Logging
**Source:** ./specs/TESTING.md (Section: "Console Logging Requirement")

The component must log its internal state to the console once per second in the format: `drift-bg: x=12.34 y=-5.67 z=23.45 u=0.12 v=-0.08 w=0.15`

## $REQ_DRIFTBG_025: Console Mode Logging
**Source:** ./specs/TESTING.md (Section: "3. Mouse Interaction Test")

The component must log its current mode in console output, showing `[SPIRAL` when in Spiral Mode and `[MOUSE` when in Mouse Mode.

## $REQ_DRIFTBG_026: Visual Animation Over Time
**Source:** ./specs/TESTING.md (Section: "1. Visual Movement Test")

The background must visibly animate over a 5-second period such that screenshots taken 5 seconds apart show noticeable visual change.

## $REQ_DRIFTBG_027: All State Variables Change
**Source:** ./specs/TESTING.md (Section: "2. State Change Test")

All six state variables (x, y, z, u, v, w) must change over time, with different values between consecutive console log lines.

## $REQ_DRIFTBG_028: Block-Level Container
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "2. Component Interface")

The component must act as a block-level container.
