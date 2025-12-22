# Visual Testing

Documents the Playwright screenshot-based visual verification approach for validating form visibility, background coverage, and animation behavior.

## $REQ_VT_001: Form Visibility Verification
**Source:** ./specs/TESTING.md (Section: "Test 1: Form Visibility")

Visual test MUST verify the login form is visible with glassmorphic styling: "Login" title, email field, "Stay logged in" checkbox, and "Continue" button. Form MUST appear semi-transparent with blurred background visible through it.

## $REQ_VT_002: Background Coverage Verification
**Source:** ./specs/TESTING.md (Section: "Test 2: Background Coverage")

Visual test MUST verify the tiled background image completely covers the viewport with no gaps, seams, or uncovered areas visible.

## $REQ_VT_003: Background Animation Verification
**Source:** ./specs/TESTING.md (Section: "Test 3: Background Animation")

Visual test MUST take two screenshots 5 seconds apart and verify that the background image has visibly shifted position between screenshots while the login form remains stationary in both screenshots.
