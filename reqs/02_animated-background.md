# Animated Background

Documents the continuously scrolling tiled background including its source image, scroll direction formula, wrapping behavior, and animation parameters.

## $REQ_ANIMATED_BG_001: Background Source Image
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Background Image")

The background MUST use `extart/bg.jpg` as the source image.

## $REQ_ANIMATED_BG_002: Tiled Background Coverage
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Background Image")

The background image MUST be tiled to fill the viewport completely with no gaps, seams, or uncovered areas.

## $REQ_ANIMATED_BG_003: Scroll Direction Formula
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Direction Formula")

The background MUST scroll in a direction determined by angle θ (in degrees) using compass-style orientation where:
- dx = s × sin(θ) (horizontal displacement per second)
- dy = −s × cos(θ) (vertical displacement per second)

## $REQ_ANIMATED_BG_004: Scroll Angle
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Parameters")

The scroll angle MUST be 45 degrees.

## $REQ_ANIMATED_BG_005: Scroll Speed
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Parameters")

The scroll speed MUST be 50 pixels per second.

## $REQ_ANIMATED_BG_006: Seamless Wrapping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Wrapping")

The background MUST tile seamlessly, with portions scrolling off one edge reappearing on the opposite edge.

## $REQ_ANIMATED_BG_007: Continuous Animation
**Source:** ./specs/TESTING.md (Section: "Test 3: Background Animation")

The background MUST continuously scroll, visibly shifting position over time.
