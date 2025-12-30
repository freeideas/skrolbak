# JavaScript API

Documents the programmatic interface for testing: attribute accessors, position accessors, and velocity accessors.

## $REQ_JSAPI_001: Attribute Accessors for Range Attributes
**Source:** ./specs/TESTING.md (Section: "Attribute Accessors")

The `<animated-background>` element must expose camelCase properties for getting and setting each range attribute: `panX`, `panY`, `panZ`, `rotX`, `rotY`, `rotZ`. Each property gets/sets the corresponding range value (0-100).

## $REQ_JSAPI_002: Attribute Accessor for src
**Source:** ./specs/TESTING.md (Section: "Attribute Accessors")

The `<animated-background>` element must expose a `src` property for getting and setting the image source URL.

## $REQ_JSAPI_003: Position Accessors
**Source:** ./specs/TESTING.md (Section: "Position Accessors")

The `<animated-background>` element must expose position properties: `panXPosition`, `panYPosition`, `panZPosition`, `rotXPosition`, `rotYPosition`, `rotZPosition`. Each property gets/sets the current position for that degree of freedom, with values ranging from -50% (minimum) to +50% (maximum), where 0% is the absolute center.

## $REQ_JSAPI_004: Position Setter Allows Full Range
**Source:** ./specs/TESTING.md (Section: "Position Accessors")

Position setters must accept any value in the -50% to +50% range, regardless of the attribute constraint. For example, if `pan-x="30"` constrains normal operation to -15% to +15%, the `panXPosition` setter still allows setting any value from -50% to +50%.

## $REQ_JSAPI_005: Velocity Accessors
**Source:** ./specs/TESTING.md (Section: "Velocity Accessors")

The `<animated-background>` element must expose velocity properties: `panXVelocity`, `panYVelocity`, `panZVelocity`, `rotXVelocity`, `rotYVelocity`, `rotZVelocity`. Each property gets/sets the current velocity for that degree of freedom, expressed as percent of range per second.
