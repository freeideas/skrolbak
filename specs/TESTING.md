# Testing

Visual verification using Playwright screenshots and AI-based image analysis, plus console log verification for numerical state.

## Visual Verification Approach

**Important:** Byte-level or pixel-level screenshot comparison is unreliable for visual verification. Browser rendering is non-deterministic -- sub-pixel font rendering, anti-aliasing, compositing timing, and other factors cause consecutive screenshots to differ at the byte level even when nothing visually changed. This leads to false positives (tests pass when they shouldn't).

For all visual verification steps, tests must:
1. Take screenshots using Playwright
2. Save screenshots to `./tmp/` with descriptive names
3. Use `visual-test.py` to have AI verify assertions about the screenshots

Example:
```python
# Save screenshots
page.screenshot(path='./tmp/before.png')
time.sleep(5)
page.screenshot(path='./tmp/after.png')

# Use AI to verify visual change
from visual_test import check_visual
passed, explanation = check_visual(
    image_files=['./tmp/before.png', './tmp/after.png'],
    assertion="The background has moved or changed between the two screenshots",
    test_script=__file__
)
assert passed, explanation
```

**Never use** `screenshot1 != screenshot2` or similar byte/pixel comparisons for visual verification.

## Console Logging Requirement

The `<drift-bg>` component must log its internal state to the console once per second in the following format:

```
drift-bg: x=12.34 y=-5.67 z=23.45 u=0.12 v=-0.08 w=0.15
```

Where:
- `x`, `y`: Current follower position (World Units, -50 to +50)
- `z`: Current follower depth (World Units)
- `u`: Current follower roll (radians)
- `v`: Current follower pitch (radians)
- `w`: Current follower yaw (radians)

Tests can capture these console messages to verify numerical behavior.

## Test Cases

### 1. Visual Movement Test

Verify that the background animates over time.

**Process:**
1. Load page with `<drift-bg>` element
2. Wait for component to initialize
3. Take screenshot A (save to `./tmp/screenshot_a.png`)
4. Wait 5 seconds
5. Take screenshot B (save to `./tmp/screenshot_b.png`)
6. Use `visual-test.py` to verify: "The background has visibly moved or changed position between the two screenshots"

**Why 5 seconds:** The spiral motion, depth oscillation, and tilt oscillations all have periods measured in seconds (13s, 17s, 20s, 23s, 25s). After 5 seconds, there should be noticeable visual change.

### 2. State Change Test

Verify that all six state variables (x, y, z, u, v, w) change over time.

**Process:**
1. Load page with `<drift-bg>` element
2. Capture console output
3. Wait for at least 2 console log lines from `drift-bg:`
4. Parse the two log lines to extract x, y, z, u, v, w values
5. Verify: every variable has a different value between the two log lines

**Why this works:** The follower system continuously approaches the target state. Since targets are driven by time-based oscillations with different periods, all six values should be changing at any given moment.

### 3. Mouse Interaction Test

Verify that mouse movement triggers Mouse Mode.

**Process:**
1. Load page with `<drift-bg>` element
2. Wait for at least one console log line containing `[SPIRAL` (idle mode)
3. Move the mouse anywhere within the canvas
4. Wait for the next console log line
5. Verify: the log contains `[MOUSE` (indicating mouse-tracking mode is active)

**Why this works:** The component logs its current mode in the console output. When idle, it shows `[SPIRAL ...`. When responding to mouse input, it switches to `[MOUSE ...`. This confirms the component detected and responded to mouse movement without depending on easing timing.

## Success Criteria

All tests pass when:
- Visual movement test confirms the background animates over 5 seconds
- State change test confirms all six variables (x, y, z, u, v, w) are changing
- Mouse interaction test confirms the component switches to Mouse Mode when the mouse moves
