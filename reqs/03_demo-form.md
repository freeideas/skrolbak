# Demo Form

Documents the glassmorphic login form overlay: its visual design, email validation behavior, and success panel transition.

## $REQ_DEMO_FORM_001: Form Visual Design
**Source:** ./specs/DEMO.md (Section: "Visual Design")

The demo form must be a hot-pink 50% opaque glassmorphic login form that is centered horizontally and vertically in the viewport, with a semi-transparent frosted glass blur effect.

## $REQ_DEMO_FORM_002: Form Contents
**Source:** ./specs/DEMO.md (Section: "Visual Design")

The demo form must contain: a heading, an email input field, a checkbox, and a submit button.

## $REQ_DEMO_FORM_003: Email Validation on Submit
**Source:** ./specs/DEMO.md (Section: "Behavior")

When the submit button is clicked, the system must validate that the email field contains an `@` character.

## $REQ_DEMO_FORM_004: Invalid Email Error Display
**Source:** ./specs/DEMO.md (Section: "Behavior")

When the email validation fails (no `@` character), an error message must be shown below the input field.

## $REQ_DEMO_FORM_005: Valid Email Transition to Success Panel
**Source:** ./specs/DEMO.md (Section: "Behavior")

When the email validation passes (contains `@` character), the form must be hidden and a success panel must be shown.

## $REQ_DEMO_FORM_006: Success Panel Visual Design
**Source:** ./specs/DEMO.md (Section: "Success Panel")

The success panel must have the same size, position, and hot-pink glassmorphic appearance as the form.

## $REQ_DEMO_FORM_007: Success Panel Content
**Source:** ./specs/DEMO.md (Section: "Success Panel")

The success panel must contain only centered text reading "(Your App Here)" with no other elements.

