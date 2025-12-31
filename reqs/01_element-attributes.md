# Element Attributes

Documents the element's attributes: `src` for image URL, `t` for replay tick, and six range attributes (`pan-x`, `pan-y`, `pan-z`, `rot-x`, `rot-y`, `rot-z`) that constrain degrees of freedom.

## $REQ_ATTR_001: src Attribute Specifies Background Image
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Image source")

The `src` attribute is required and specifies the URL of the image used as the background texture. The image is tiled infinitely over the wall using a repeating pattern in both X and Y directions, with the center of one tile at the geometric center of the wall.

## $REQ_ATTR_002: t Attribute Default Value
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Debug/replay attribute")

The `t` attribute is optional, with type non-negative integer and default value 0.

## $REQ_ATTR_003: t Attribute Fast-Forward Behavior
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Deterministic Randomness")

When the `t` attribute is set to a value N > 0, the element fast-forwards to that state on initialization by simulating state from t=0 to t=N-1 without rendering, then beginning normal animation and console logging at t=N.

## $REQ_ATTR_004: Range Attributes Are Optional With Default Zero
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Range attributes (degrees of freedom)")

All six range attributes (`pan-x`, `pan-y`, `pan-z`, `rot-x`, `rot-y`, `rot-z`) are optional and default to 0 (no motion) if omitted.

## $REQ_ATTR_006: rot-x Rotation Range Mapping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Rotation ranges")

The `rot-x` attribute maps a percentage value to a rotation interval around the X axis. The allowed rotation magnitude is `(p / 100) × 45°`, giving an effective interval of `[-a, +a]` where `a = (p / 100) × 45°`. For example, `rot-x="100"` allows rotation from -45° to +45°.

## $REQ_ATTR_007: rot-y Rotation Range Mapping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Rotation ranges")

The `rot-y` attribute maps a percentage value to a rotation interval around the Y axis. The allowed rotation magnitude is `(p / 100) × 45°`, giving an effective interval of `[-a, +a]` where `a = (p / 100) × 45°`. For example, `rot-y="50"` allows rotation from -22.5° to +22.5°.

## $REQ_ATTR_008: rot-z Rotation Range Mapping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Rotation ranges")

The `rot-z` attribute maps a percentage value to a rotation interval around the Z axis. The allowed rotation magnitude is `(p / 100) × 45°`, giving an effective interval of `[-a, +a]` where `a = (p / 100) × 45°`.

## $REQ_ATTR_009: pan-x Translation Range Mapping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Pan ranges for X and Y")

The `pan-x` attribute maps a percentage value to a horizontal translation range. At 100%, the wall can move so that the left edge is flush with the viewport left edge at one extreme, and the right edge is flush with the viewport right edge at the other extreme. Smaller percentages proportionally reduce the max displacement from center.

## $REQ_ATTR_010: pan-y Translation Range Mapping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Pan ranges for X and Y")

The `pan-y` attribute maps a percentage value to a vertical translation range. At 100%, the wall can move so that the top edge is flush with the viewport top edge at one extreme, and the bottom edge is flush with the viewport bottom edge at the other extreme. Smaller percentages proportionally reduce the max displacement from center.

## $REQ_ATTR_011: pan-z Zoom Range Mapping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Pan range for Z (zoom)")

The `pan-z` attribute maps a percentage value to a zoom interval. The potential zoom interval is from 50% to 150% of nominal scale (1.0). At 100%, zoom animates over the full [0.5, 1.5] interval. At smaller percentages, the zoom interval is linearly shrunk around nominal zoom (1.0), with 0% meaning no zoom change.

## $REQ_ATTR_012: Zero Range Means No Motion
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Initialization")

Axes with range = 0 have no velocity and remain stationary.

## $REQ_ATTR_013: Attribute Parsing and Clamping
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Processing model")

On construction or attribute changes, range attributes are parsed as floating-point percentages and clamped to [0, 100].
