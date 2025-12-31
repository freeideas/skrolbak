# Mouse Interaction

Documents mouse-based boost control: position sampling, pan mode vs rotation mode, boost calculation, and console logging.

## $REQ_MOUSE_001: Mouse Position Sampling Rate
**Source:** ./specs/BOOST.md (Section: "Sampling")

Mouse position must be sampled twice per second (every 500ms). Each sample records the mouse X and Y coordinates relative to the element.

## $REQ_MOUSE_002: Mouse Coordinates as Percentages
**Source:** ./specs/BOOST.md (Section: "Sampling")

Mouse coordinates must be expressed as percentages of element width/height, where 0% = left/top edge and 100% = right/bottom edge.

## $REQ_MOUSE_003: Pan Mode Boost Calculation
**Source:** ./specs/BOOST.md (Section: "Boost Calculation")

When no mouse button is pressed (pan mode), on each sample after the first: if deltaX != 0, set panXBoost = deltaX * 2; if deltaY != 0, set panYBoost = deltaY * 2.

## $REQ_MOUSE_004: Rotation Mode Boost Calculation
**Source:** ./specs/BOOST.md (Section: "Boost Calculation")

When any mouse button is pressed (rotation mode), on each sample after the first: if deltaX != 0, set rotYBoost = deltaX * 2 (horizontal drag rotates around Y axis); if deltaY != 0, set rotXBoost = deltaY * 2 (vertical drag rotates around X axis).

## $REQ_MOUSE_005: Pan Mode Console Logging
**Source:** ./specs/BOOST.md (Section: "Console Logging")

On each mouse sample that produces a boost in pan mode, log to console in the format: `mouse pan: deltaX=20 deltaY=0 → panXBoost=40 panYBoost=0`.

## $REQ_MOUSE_006: Rotation Mode Console Logging
**Source:** ./specs/BOOST.md (Section: "Console Logging")

On each mouse sample that produces a boost in rotation mode, log to console in the format: `mouse rotate: deltaX=0 deltaY=20 → rotXBoost=40 rotYBoost=0`.

## $REQ_MOUSE_007: Mouse Interaction Always Enabled
**Source:** ./specs/BOOST.md (Section: "Behavior Notes")

Mouse interaction must always be enabled with no opt-in attribute required.

## $REQ_MOUSE_008: Sampling Pauses When Mouse Leaves Element
**Source:** ./specs/BOOST.md (Section: "Behavior Notes")

When the mouse leaves the element, sampling pauses. Last boost values decay normally via the tick-based decay mechanism.

## $REQ_MOUSE_009: Non-Cumulative Boost Replacement
**Source:** ./specs/BOOST.md (Section: "Non-Cumulative Behavior")

Each mouse sample that has movement replaces the previous boost value entirely (does not add to it). When the mouse is stationary (same coordinates across samples), boost is not modified and simply decays via normal tick-based decay.

## $REQ_MOUSE_010: Touch Events Equivalence
**Source:** ./specs/BOOST.md (Section: "Behavior Notes")

Touch events must be handled equivalently to mouse events where supported.
