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

## $REQ_VISTEST_009: Test Process Position Recording
**Source:** ./specs/TESTING.md (Section: "Test Process")

Each degree of freedom test must record initial position, take a screenshot, wait 1.5 seconds, record final position, and take another screenshot.

## $REQ_VISTEST_010: Test Process Numerical Verification
**Source:** ./specs/TESTING.md (Section: "Test Process")

Each degree of freedom test must verify numerically that final position ≈ initial position + (velocity × 1.5 seconds).

## $REQ_VISTEST_011: Test Process Visual Verification
**Source:** ./specs/TESTING.md (Section: "Test Process")

Each degree of freedom test must verify visually that the background moved as expected for that axis between the two screenshots.

## $REQ_VISTEST_012: Success Criteria
**Source:** ./specs/TESTING.md (Section: "Success Criteria")

All tests pass when each isolated test shows only the expected motion between the two screenshots, and the deterministic replay test confirms matching positions.
