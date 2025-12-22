# Testing

Visual verification testing using Playwright screenshots examined by AI.

## Test Cases

### Test 1: Form Visibility

Verify the login form is visible with glassmorphic styling: "Login" title, email field, "Stay logged in" checkbox, and "Continue" button. Form appears semi-transparent with blurred background visible through it.

### Test 2: Background Coverage

Verify the tiled background image completely covers the viewport with no gaps, seams, or uncovered areas visible.

### Test 3: Background Animation

Take two screenshots 5 seconds apart. Verify:
- The background image has visibly shifted position between screenshots
- The login form remains stationary in both screenshots

## Success Criteria

All tests pass when:
1. Login form is visible, centered, and has glassmorphic styling
2. Background image tiles completely cover the viewport (no gaps)
3. Background visibly scrolls between screenshots while form stays fixed
