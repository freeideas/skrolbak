# Boost Velocity

Documents the boost velocity component for each axis: boost accessors, decay toward zero, boundary reversal, and combination with base velocity.

## $REQ_BOOST-VEL_001: Boost Accessors
**Source:** ./specs/BOOST.md (Section: "Boost Accessors")

The element exposes get/set properties for boost velocity on each degree of freedom: `panXBoost`, `panYBoost`, `panZBoost`, `rotXBoost`, `rotYBoost`, `rotZBoost`. Values are numbers representing percent of allowed range per second.

## $REQ_BOOST-VEL_002: Boost Default Value
**Source:** ./specs/BOOST.md (Section: "Value Semantics")

All boost values default to 0 (no boost) and start at 0 when the element connects to the document.

## $REQ_BOOST-VEL_003: Effective Velocity Calculation
**Source:** ./specs/BOOST.md (Section: "Effective Velocity")

The effective velocity for each axis is the sum of the base velocity and the boost: `effectiveVelocity = baseVelocity + boost`. Position updates use this effective velocity.

## $REQ_BOOST-VEL_004: Boost Decay Toward Zero
**Source:** ./specs/BOOST.md (Section: "Decay")

At each tick (when `t` increments): if boost > 0, boost decreases by 1 (but not below 0); if boost < 0, boost increases by 1 (but not above 0); if boost is between -1 and +1, boost becomes 0. Decay is applied after velocity updates but before position updates.

## $REQ_BOOST-VEL_005: Boost Reversal at Boundaries
**Source:** ./specs/BOOST.md (Section: "Boundary Behavior")

When position reaches or exceeds a boundary, the boost velocity is reversed (sign flipped) along with the base velocity reversal.

## $REQ_BOOST-VEL_006: Boost Not Simulated During Fast-Forward
**Source:** ./specs/BOOST.md (Section: "Initialization")

When using the `t` attribute for fast-forward, boost values are not simulated and remain at 0. Boost is a runtime-only feature.
