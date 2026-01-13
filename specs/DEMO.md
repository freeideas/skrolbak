# Demo

Assets used solely to demonstrate and test the animated background component.

## Demo Image

`./extart/bg.jpg` is provided for demo/testing purposes. Copy it to an appropriate directory under `./code/`.

## Demo Form

A hot-pink 50% opaque glassmorphic login form that floats above the animated background.

### Visual Design

- Centered horizontally and vertically in viewport
- Semi-transparent with frosted glass blur effect (glassmorphism)
- Contains: heading, email input field, checkbox, submit button

### Behavior

When the submit button is clicked:
1. Validate that the email field contains an `@` character (basic email format check)
2. If invalid: show an error message below the input field
3. If valid: hide the form and show a success panel

### Success Panel

The success panel has the same glassmorphic styling as the form:
- Same size, position, and hot-pink glassmorphic appearance
- Contains centered text: "(Your App Here)"
- No other elements

### Purpose

The demo form verifies:
1. Background animates visibly behind semi-transparent content
2. Background remains behind foreground content (correct z-index)
3. Blur effect interacts properly with moving background
