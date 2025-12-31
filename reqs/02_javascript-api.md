# JavaScript API

Documents the programmatic interface: attribute accessors, position accessors, and velocity accessors for each degree of freedom.

## $REQ_JSAPI_001: Attribute Accessors for Range Attributes
**Source:** ./specs/TESTING.md (Section: "Attribute Accessors")

The `<animated-background>` element must expose get/set properties for each range attribute (`pan-x`, `pan-y`, `pan-z`, `rot-x`, `rot-y`, `rot-z`) using camelCase names: `panX`, `panY`, `panZ`, `rotX`, `rotY`, `rotZ`. Getting returns the current range value (0-100), setting updates the range.

## $REQ_JSAPI_002: Attribute Accessor for src
**Source:** ./specs/TESTING.md (Section: "Attribute Accessors")

The `<animated-background>` element must expose a `src` property for getting and setting the image source URL.

## $REQ_JSAPI_003: Position Accessors
**Source:** ./specs/TESTING.md (Section: "Position Accessors")

The `<animated-background>` element must expose get/set properties for the current position of each degree of freedom: `panXPosition`, `panYPosition`, `panZPosition`, `rotXPosition`, `rotYPosition`, `rotZPosition`.

## $REQ_JSAPI_004: Position Value Semantics
**Source:** ./specs/TESTING.md (Section: "Position Accessors")

Position values range from -50% to +50%, where 0% is the absolute center (starting position, center of background tile), -50% is the minimum position, and +50% is the maximum position.

## $REQ_JSAPI_005: Position Setter Allows Full Range
**Source:** ./specs/TESTING.md (Section: "Position Accessors")

The position setter allows any value in -50% to +50%, regardless of the attribute range constraint. For example, if `pan-x="30"`, the position normally stays within -15% to +15% during animation, but the setter allows any value in -50% to +50%.

## $REQ_JSAPI_006: Velocity Accessors
**Source:** ./specs/TESTING.md (Section: "Velocity Accessors")

The `<animated-background>` element must expose get/set properties for the current velocity of each degree of freedom: `panXVelocity`, `panYVelocity`, `panZVelocity`, `rotXVelocity`, `rotYVelocity`, `rotZVelocity`. Velocity is expressed as percent of range per second.

## $REQ_JSAPI_007: Boost Accessors
**Source:** ./specs/BOOST.md (Section: "Boost Accessors")

The `<animated-background>` element must expose get/set properties for the boost velocity of each degree of freedom: `panXBoost`, `panYBoost`, `panZBoost`, `rotXBoost`, `rotYBoost`, `rotZBoost`.

## $REQ_JSAPI_008: Boost Value Semantics
**Source:** ./specs/BOOST.md (Section: "Value Semantics")

Boost values are numbers (positive or negative) in units of percent of allowed range per second (same as base velocity), defaulting to 0, with no minimum or maximum bounds.
