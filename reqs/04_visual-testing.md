# Visual Testing

Documents the test cases for verifying each degree of freedom through Playwright screenshots and position/velocity checks.

## $REQ_VISTEST_001: Demo Form Visibility and Styling
**Source:** ./specs/TESTING.md (Section: "Test Cases")

The demo form test must verify: the form is visible, the form is centered, and the form has glassmorphic styling (semi-transparent with blur).

## $REQ_VISTEST_002: Demo Form Stationary Behavior
**Source:** ./specs/TESTING.md (Section: "Test Cases")

The demo form must remain stationary while the background animates behind it.

## $REQ_VISTEST_003: Pan-X Isolation Test
**Source:** ./specs/TESTING.md (Section: "Test Cases")

When `panX = 100` and all other ranges are set to 0, with `panXVelocity = 20`, the test must verify horizontal movement only.

## $REQ_VISTEST_004: Pan-Y Isolation Test
**Source:** ./specs/TESTING.md (Section: "Test Cases")

When `panY = 100` and all other ranges are set to 0, with `panYVelocity = 20`, the test must verify vertical movement only.

## $REQ_VISTEST_005: Pan-Z Isolation Test
**Source:** ./specs/TESTING.md (Section: "Test Cases")

When `panZ = 100` and all other ranges are set to 0, with `panZVelocity = 20`, the test must verify uniform scaling from center.

## $REQ_VISTEST_006: Rot-X Isolation Test
**Source:** ./specs/TESTING.md (Section: "Test Cases")

When `rotX = 100` and all other ranges are set to 0, with `rotXVelocity = 20`, the test must verify forward/backward tilt with perspective distortion.

## $REQ_VISTEST_007: Rot-Y Isolation Test
**Source:** ./specs/TESTING.md (Section: "Test Cases")

When `rotY = 100` and all other ranges are set to 0, with `rotYVelocity = 20`, the test must verify left/right tilt with perspective distortion.

## $REQ_VISTEST_008: Rot-Z Isolation Test
**Source:** ./specs/TESTING.md (Section: "Test Cases")

When `rotZ = 100` and all other ranges are set to 0, with `rotZVelocity = 20`, the test must verify in-plane rotation only.

## $REQ_VISTEST_009: Deterministic Replay Test
**Source:** ./specs/TESTING.md (Section: "Deterministic Replay Test")

To verify that the `t` attribute fast-forward produces identical state to real-time animation: create element with all ranges at 100% and `t="0"`, wait 30 seconds, record all six position values, then create a new element with `t="29"`, wait 1 second, and verify all six position values match (within floating-point tolerance).
