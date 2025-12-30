# Element Attributes

Documents the element's attributes: image source (`src`), debug/replay tick (`t`), and the six range attributes for degrees of freedom.

## $REQ_ELEM_ATTR_001: Image Source Attribute Required
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Image source")

The `src` attribute is required and specifies the URL of the image used as the background texture of the virtual wall.

## $REQ_ELEM_ATTR_002: Image Tiling Behavior
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Image source")

The image specified by `src` is tiled infinitely over the wall using a repeating pattern in both X and Y directions, with the center of one tile at the geometric center of the wall.

## $REQ_ELEM_ATTR_003: Debug Tick Attribute Type and Default
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Debug/replay attribute")

The `t` attribute is optional, has type non-negative integer, and defaults to 0.

## $REQ_ELEM_ATTR_004: Debug Tick Fast-Forward Behavior
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

When `t` is set to a value N > 0, the element simulates state from t=0 to t=N-1 without rendering (instant computation), then begins normal animation and console logging at t=N.

## $REQ_ELEM_ATTR_005: Range Attributes Defined
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Range attributes (degrees of freedom)")

Six range attributes exist: `pan-x`, `pan-y`, `pan-z` for translation ranges, and `rot-x`, `rot-y`, `rot-z` for rotation ranges.

## $REQ_ELEM_ATTR_006: Range Attribute Type and Clamping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Range attributes (degrees of freedom)")

All range attributes have type number (float or integer) and are clamped to the interval [0, 100].

## $REQ_ELEM_ATTR_007: Range Attribute Default Value
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Range attributes (degrees of freedom)")

All range attributes default to 0 (no motion) if omitted.

## $REQ_ELEM_ATTR_008: Rotation Range Mapping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Rotation ranges")

For `rot-x`, `rot-y`, `rot-z`: the potential rotation interval is [-45°, +45°]. The attribute percentage p maps to an allowed interval of [-(p/100)×45°, +(p/100)×45°].

## $REQ_ELEM_ATTR_009: Pan-X and Pan-Y Range Mapping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Pan ranges for X and Y")

For `pan-x` and `pan-y`: at 100% range, the wall can move from one edge flush with viewport to the opposite edge flush with viewport. Smaller percentages proportionally reduce the max displacement from center.

## $REQ_ELEM_ATTR_010: Pan-Z Range Mapping (Zoom)
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Pan range for Z (zoom)")

For `pan-z`: the potential zoom interval is [0.5, 1.5] (50% to 150% of nominal scale). At 100% range, zoom animates over the full interval. At smaller percentages, the interval is linearly shrunk around nominal zoom (1.0), with 0% meaning no zoom change.
