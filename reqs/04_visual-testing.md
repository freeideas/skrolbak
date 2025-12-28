# Visual Testing

Documents the Playwright screenshot-based verification for demo form appearance, background coverage, and isolated motion tests.

## $REQ_VISUAL_001: Demo Form Visibility and Centering
**Source:** ./specs/TESTING.md (Section: "Test 1: Demo Form")

The demo form must be visible and centered in the viewport.

## $REQ_VISUAL_002: Demo Form Glassmorphic Styling
**Source:** ./specs/TESTING.md (Section: "Test 1: Demo Form")

The demo form must display glassmorphic styling (semi-transparent with blur).

## $REQ_VISUAL_003: Background Coverage at T=0
**Source:** ./specs/TESTING.md (Section: "Test 2: Background Coverage")

The tiled background must completely cover the viewport with no gaps at time offset T=0.

## $REQ_VISUAL_004: Background Coverage at T=9
**Source:** ./specs/TESTING.md (Section: "Test 2: Background Coverage")

The tiled background must completely cover the viewport with no gaps at time offset T=9, confirming dynamic tiling works correctly.

## $REQ_VISUAL_005: Background Animates Over Time
**Source:** ./specs/TESTING.md (Section: "Test 3: Animation")

Taking two screenshots 5 seconds apart must show the background visibly changes (pan, rotation, zoom).

## $REQ_VISUAL_006: Demo Form Remains Stationary During Animation
**Source:** ./specs/TESTING.md (Section: "Test 3: Animation")

Taking two screenshots 5 seconds apart must show the demo form remains stationary while the background animates.

## $REQ_VISUAL_007: Isolated X-Pan Motion
**Source:** ./specs/TESTING.md (Section: "X-Pan Only")

When configured with x-pan enabled and all other motion disabled, screenshots 5 seconds apart must show horizontal scroll only.

## $REQ_VISUAL_008: Isolated Y-Pan Motion
**Source:** ./specs/TESTING.md (Section: "Y-Pan Only")

When configured with y-pan enabled and all other motion disabled, screenshots 5 seconds apart must show vertical scroll only.

## $REQ_VISUAL_009: Isolated X-Rotation Motion
**Source:** ./specs/TESTING.md (Section: "X-Rotation Only")

When configured with x-rotation enabled and all other motion disabled, screenshots 5 seconds apart must show forward/backward tilt with perspective distortion.

## $REQ_VISUAL_010: Isolated Y-Rotation Motion
**Source:** ./specs/TESTING.md (Section: "Y-Rotation Only")

When configured with y-rotation enabled and all other motion disabled, screenshots 5 seconds apart must show left/right tilt with perspective distortion.

## $REQ_VISUAL_011: Isolated Z-Rotation Motion
**Source:** ./specs/TESTING.md (Section: "Z-Rotation Only")

When configured with z-rotation enabled and all other motion disabled, screenshots 5 seconds apart must show in-plane rotation only.

## $REQ_VISUAL_012: Isolated Zoom Motion
**Source:** ./specs/TESTING.md (Section: "Zoom Only")

When configured with zoom enabled and all other motion disabled, screenshots 5 seconds apart must show uniform scaling from center.
