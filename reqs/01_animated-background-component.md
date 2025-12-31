# Animated Background Component

Documents the `<animated-background>` custom HTML element structure, its rendering model with a 10x virtual wall, and tiled background image display.

## $REQ_ABC_001: Custom Element Tag Name
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Element overview")

The component must use the tag name `<animated-background>` as an autonomous custom element extending `HTMLElement`.

## $REQ_ABC_002: Required src Attribute
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Image source")

The element must have a required `src` attribute that specifies the URL of the image used as the background texture.

## $REQ_ABC_003: Virtual Wall Dimensions
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Element overview")

The element must internally create a 3D-transformed "wall" surface that is 10× viewport width and 10× viewport height.

## $REQ_ABC_004: Tiled Background Image
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Image source")

The `src` image must be tiled infinitely over the wall using a repeating pattern in both X and Y directions, with the center of one tile at the geometric center of the wall.

## $REQ_ABC_005: Viewport Rendering
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Element overview")

The visible viewport must correspond to the browser window, with animation produced by transforming the wall, not the viewport.

## $REQ_ABC_006: Script Include Usage
**Source:** ./README.md (Section: "Usage")

The component must be usable by including `animated-background.js` via a script tag and using the `<animated-background src="...">` element.

## $REQ_ABC_007: Attribute Accessors via JavaScript
**Source:** ./specs/TESTING.md (Section: "Attribute Accessors")

The element must expose get/set properties for each attribute using camelCase names: `panX`, `panY`, `panZ`, `rotX`, `rotY`, `rotZ`, `src`.

## $REQ_ABC_008: Position Accessors via JavaScript
**Source:** ./specs/TESTING.md (Section: "Position Accessors")

The element must expose get/set properties for current position of each degree of freedom: `panXPosition`, `panYPosition`, `panZPosition`, `rotXPosition`, `rotYPosition`, `rotZPosition`. Values range from -50% to +50%, with 0% being absolute center.

## $REQ_ABC_009: Velocity Accessors via JavaScript
**Source:** ./specs/TESTING.md (Section: "Velocity Accessors")

The element must expose get/set properties for current velocity of each degree of freedom: `panXVelocity`, `panYVelocity`, `panZVelocity`, `rotXVelocity`, `rotYVelocity`, `rotZVelocity`. Units are percent of allowed range per second.

## $REQ_ABC_010: Range Attribute Parsing
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Processing model")

Range attributes (`pan-x`, `pan-y`, `pan-z`, `rot-x`, `rot-y`, `rot-z`) must be parsed as floating-point percentages and clamped to [0, 100].

## $REQ_ABC_011: Range Attributes Default to Zero
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Range attributes")

All range attributes must default to 0 (no motion) if omitted.

## $REQ_ABC_012: Wall Transform Application
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Transform application")

On each animation frame, the element must compute and apply transforms to the wall: `pan-x`/`pan-y` as translations, `pan-z` as scaling (zoom), and `rot-x`/`rot-y`/`rot-z` as 3D rotations around respective axes.

## $REQ_ABC_013: Background Z-Index
**Source:** ./specs/DEMO.md (Section: "Purpose")

The animated background must remain behind foreground content (correct z-index).

## $REQ_ABC_014: Animation Behind Transparent Content
**Source:** ./specs/DEMO.md (Section: "Purpose")

The background must animate visibly behind semi-transparent content.
