# Testing Methodology

Documents the mandated approach for visual verification using Playwright screenshots and AI-based image analysis, including the prohibition on byte-level comparisons.

## $REQ_TESTMETH_001: Screenshots via Playwright
**Source:** ./specs/TESTING.md (Section: "Visual Verification Approach")

Tests must take screenshots using Playwright.

## $REQ_TESTMETH_002: Screenshots Saved to tmp Directory
**Source:** ./specs/TESTING.md (Section: "Visual Verification Approach")

Tests must save screenshots to `./tmp/` with descriptive names.

## $REQ_TESTMETH_003: AI-Based Visual Verification
**Source:** ./specs/TESTING.md (Section: "Visual Verification Approach")

Tests must use `visual-test.py` to have AI verify assertions about screenshots.

## $REQ_TESTMETH_004: No Byte-Level Screenshot Comparison
**Source:** ./specs/TESTING.md (Section: "Visual Verification Approach")

Tests must never use byte-level or pixel-level screenshot comparison (e.g., `screenshot1 != screenshot2`) for visual verification.

## $REQ_TESTMETH_005: Console Log Format
**Source:** ./specs/TESTING.md (Section: "Console Logging Requirement")

The `<drift-bg>` component must log its internal state to the console once per second in the format: `drift-bg: x=<value> y=<value> z=<value> u=<value> v=<value> w=<value>` where x,y are follower position (-50 to +50 World Units), z is follower depth, and u,v,w are roll, pitch, yaw in radians.

## $REQ_TESTMETH_006: Visual Movement Test Process
**Source:** ./specs/TESTING.md (Section: "Test Cases - 1. Visual Movement Test")

The visual movement test must: load page with `<drift-bg>` element, wait for initialization, take screenshot A, wait 5 seconds, take screenshot B, then use `visual-test.py` to verify the background has visibly moved or changed position between the two screenshots.

## $REQ_TESTMETH_007: State Change Test Process
**Source:** ./specs/TESTING.md (Section: "Test Cases - 2. State Change Test")

The state change test must: load page with `<drift-bg>` element, capture console output, wait for at least 2 console log lines from `drift-bg:`, parse both log lines to extract x, y, z, u, v, w values, then verify every variable has a different value between the two log lines.

## $REQ_TESTMETH_008: Mouse Interaction Test Process
**Source:** ./specs/TESTING.md (Section: "Test Cases - 3. Mouse Interaction Test")

The mouse interaction test must: load page with `<drift-bg>` element, wait for at least one console log line containing `[SPIRAL` (idle mode), move the mouse anywhere within the canvas, wait for the next console log line, then verify the log contains `[MOUSE` (indicating mouse-tracking mode is active).
