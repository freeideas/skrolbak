# Demo Form

Documents the glassmorphic login form overlay used to verify background animation and z-index behavior.

## $REQ_DEMO-FORM_001: Centered Position
**Source:** ./specs/DEMO.md (Section: "Visual Design")

The demo form is centered horizontally and vertically in the viewport.

## $REQ_DEMO-FORM_002: Glassmorphic Styling
**Source:** ./specs/DEMO.md (Section: "Demo Form")

The demo form is hot-pink, 50% opaque, with a frosted glass blur effect (glassmorphism).

## $REQ_DEMO-FORM_003: Form Elements
**Source:** ./specs/DEMO.md (Section: "Visual Design")

The demo form contains: a heading, an input field, a checkbox, and a button.

## $REQ_DEMO-FORM_004: Background Visible Through Form
**Source:** ./specs/DEMO.md (Section: "Purpose")

The animated background is visible and animates behind the semi-transparent form.

## $REQ_DEMO-FORM_005: Z-Index Layering
**Source:** ./specs/DEMO.md (Section: "Purpose")

The background remains behind the foreground form content (correct z-index ordering).

## $REQ_DEMO-FORM_006: Blur Effect With Moving Background
**Source:** ./specs/DEMO.md (Section: "Purpose")

The blur effect interacts properly with the moving background.

## $REQ_DEMO-FORM_007: Form Remains Stationary
**Source:** ./specs/TESTING.md (Section: "Test 3: Animation")

The demo form remains stationary while the background animates.

## $REQ_DEMO-FORM_008: Display Only
**Source:** ./specs/DEMO.md (Section: "Purpose")

The form does not submit anywhere; it is display-only.
