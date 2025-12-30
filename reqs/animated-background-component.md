# Animated Background Component

Documents the `<animated-background>` custom HTML element, its rendering model with a 10x viewport wall, and tiled background image display.

## $REQ_ABC_001: Custom Element Tag Name
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Element overview")

The component is an autonomous custom element with tag name `<animated-background>` extending `HTMLElement`.

## $REQ_ABC_002: Wall Dimensions
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Element overview")

The element creates an internal 3D-transformed "wall" surface that is 10× viewport width and 10× viewport height.

## $REQ_ABC_003: Image Tiling
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Image source")

The image specified by `src` is tiled infinitely over the wall using a repeating pattern in both X and Y directions, with the center of one tile at the geometric center of the wall.

## $REQ_ABC_004: Src Attribute Required
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Attributes")

The `src` attribute is required and specifies the URL of the image used as the background texture of the virtual wall.

## $REQ_ABC_005: Range Attributes Clamped
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Range attributes")

The six range attributes (`pan-x`, `pan-y`, `pan-z`, `rot-x`, `rot-y`, `rot-z`) are expressed as percentages between 0 and 100 inclusive, clamped to this range if out of bounds, and default to 0 if omitted.

## $REQ_ABC_006: Rotation Range Mapping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Rotation ranges")

For `rot-x`, `rot-y`, `rot-z`: the allowed rotation angle is (p / 100) × 45°, producing an effective interval of [-a, +a] where a = (p / 100) × 45°.

## $REQ_ABC_007: Pan XY Range Mapping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Pan ranges for X and Y")

For `pan-x` and `pan-y` at 100%: the wall can move so that its edge (left/right for X, top/bottom for Y) is flush with the corresponding viewport edge. Smaller percentages proportionally reduce the max displacement from center.

## $REQ_ABC_008: Pan Z Range Mapping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Pan range for Z (zoom)")

For `pan-z`: zoom ranges from 50% to 150% of nominal scale at 100%, with smaller percentages linearly shrinking the interval around the nominal zoom (1.0).

## $REQ_ABC_009: Velocity Never Zero
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Velocity semantics")

Zero velocity for any degree of freedom is not permitted as a stable state. Transitions that would result in exactly 0% must skip over 0 and choose a non-zero sign.

## $REQ_ABC_010: Velocity Evolution Per Second
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Velocity evolution")

At each one-second tick, the magnitude of each axis's velocity is either increased by 1 percentage point per second or decreased by 1 percentage point per second, determined by `prng(t, "{axis}-vel")`.

## $REQ_ABC_011: Range Boundary Reversal
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Range boundary behavior")

When the current value reaches or attempts to exceed an endpoint of the allowed interval, the velocity for that axis is immediately reversed in sign.

## $REQ_ABC_012: Initialization State
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Initialization")

On element connection: all position values start at 0 (centered for pan, no rotation for rot, nominal scale for zoom), and each axis with non-zero range is assigned initial velocity of either -1% or +1% determined by `prng(0, "{axis}-init")`.

## $REQ_ABC_013: Console Tick Logging
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

On each tick, the element logs to console: `t=0`, `t=1`, `t=2`, etc.

## $REQ_ABC_014: T Attribute Fast-Forward
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

When the `t` attribute is set to N > 0, the element simulates state from t=0 to t=N-1 without rendering, applying velocity to position, checking boundaries, and updating velocity magnitude, then begins normal animation and console logging at t=N.

## $REQ_ABC_015: Deterministic PRNG
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

All random choices use a deterministic function `prng(t, salt) → boolean` where the same `t` and `salt` always produce the same result.

## $REQ_ABC_016: JavaScript Attribute Accessors
**Source:** ./specs/TESTING.md (Section: "Attribute Accessors")

The element exposes camelCase get/set properties for each attribute: `panX`, `panY`, `panZ`, `rotX`, `rotY`, `rotZ`, `src`.

## $REQ_ABC_017: JavaScript Position Accessors
**Source:** ./specs/TESTING.md (Section: "Position Accessors")

The element exposes get/set properties for current position of each degree of freedom: `panXPosition`, `panYPosition`, `panZPosition`, `rotXPosition`, `rotYPosition`, `rotZPosition`. Position values range from -50% to +50% with 0% being absolute center.

## $REQ_ABC_018: JavaScript Velocity Accessors
**Source:** ./specs/TESTING.md (Section: "Velocity Accessors")

The element exposes get/set properties for current velocity of each degree of freedom: `panXVelocity`, `panYVelocity`, `panZVelocity`, `rotXVelocity`, `rotYVelocity`, `rotZVelocity`.
