# Boost Velocity

An additional velocity component for each degree of freedom that decays toward zero over time.

## Overview

Each of the six degrees of freedom (`pan-x`, `pan-y`, `pan-z`, `rot-x`, `rot-y`, `rot-z`) has an associated **boost velocity**. This boost:

- Adds to the base velocity (which evolves as a function of `t`)
- Decays toward zero by 1 per tick (see Timing Model in ANIMATED_BACKGROUND.md)
- Can be set programmatically for testing or interaction effects

## Properties

### Boost Accessors

For each degree of freedom, expose a boost velocity:

```javascript
element.panXBoost        // get current pan-x boost (% per second)
element.panXBoost = 10   // set pan-x boost to +10% per second
```

Property names: `panXBoost`, `panYBoost`, `panZBoost`, `rotXBoost`, `rotYBoost`, `rotZBoost`.

### Value Semantics

- Type: number (positive or negative)
- Units: percent of allowed range per second (same as base velocity)
- Default: 0 (no boost)
- No minimum or maximum bounds

## Behavior

### Effective Velocity

The effective velocity for each axis is the sum of the base velocity and the boost:

```
effectiveVelocity = baseVelocity + boost
```

Position updates use this effective velocity:

```
position += effectiveVelocity * deltaTime
```

### Decay

At each tick (when `t` increments):

1. If boost > 0: boost = boost - 1 (but not below 0)
2. If boost < 0: boost = boost + 1 (but not above 0)
3. If boost is between -1 and +1: boost = 0

The decay is applied after velocity updates but before position updates.

### Boundary Behavior

When position reaches or exceeds a boundary:

1. Base velocity is reversed (as per existing spec)
2. Boost velocity is also reversed (sign flipped)

This ensures both velocity components move the position away from the boundary.

### Initialization

All boost values start at 0 when the element connects to the document.

When using the `t` attribute for fast-forward:
- Boost values are not simulated (they remain at 0)
- Boost is a runtime-only feature for testing and interaction

## Mouse Interaction

Mouse movement over the element creates pan boosts, allowing users to "swipe" the background.

### Sampling

- Mouse position is sampled once per tick (see Timing Model in ANIMATED_BACKGROUND.md)
- Each sample records the mouse X and Y coordinates relative to the element
- Coordinates are expressed as percentages of element width/height (0% = left/top edge, 100% = right/bottom edge)

### Boost Calculation

On each sample (after the first):

1. Calculate delta: `deltaX = currentX - previousX` (in % of element width)
2. Calculate delta: `deltaY = currentY - previousY` (in % of element height)

**If no mouse button is pressed (pan mode):**

3. If `deltaX != 0`: set `panXBoost = deltaX * 2`
4. If `deltaY != 0`: set `panYBoost = deltaY * 2`

**If any mouse button is pressed (rotation mode):**

3. If `deltaX != 0`: set `rotYBoost = deltaX * 2` (horizontal drag rotates around Y axis)
4. If `deltaY != 0`: set `rotXBoost = deltaY * 2` (vertical drag rotates around X axis)

The `* 2` multiplier converts the per-tick delta to a per-second rate (since velocity units are % per second and tick interval is 500ms).

### Console Logging

On each mouse sample that produces a boost, log the effect to console:

**Pan mode (no button):**
```
mouse pan: deltaX=20 deltaY=0 → panXBoost=40 panYBoost=0
```

**Rotation mode (button held):**
```
mouse rotate: deltaX=0 deltaY=20 → rotXBoost=40 rotYBoost=0
```

This allows tests to:
1. Verify the boost values were calculated correctly
2. Use the logged values to calculate expected position changes

### Behavior Notes

- Mouse interaction is always enabled (no opt-in attribute)
- Sampling only occurs when mouse is over the element
- When mouse leaves the element, sampling pauses (last boost values decay normally)
- **Non-cumulative:** Each mouse sample replaces the previous boost value entirely (does not add to it)
- Touch events should be handled equivalently where supported

### Non-Cumulative Behavior

Mouse boost values are replaced on each sample (when movement occurs), not accumulated:

```
t=0: mouse at X=10%
t=1: mouse at X=30% → panXBoost = 40  (deltaX=20, ×2)
t=2: mouse at X=35% → panXBoost = 10  (deltaX=5, ×2) ← replaces 40, not 40+10
t=3: mouse at X=35% → (no change, deltaX=0, boost untouched)
t=4: mouse at X=35% → (no change, deltaX=0, boost untouched)
```

When the mouse is stationary (same coordinates across samples), boost is not modified. The existing boost simply decays via the normal tick-based decay (1 per tick toward zero).

### Example

If the mouse moves from X=30% to X=50% of element width in one tick:
- `deltaX = 50 - 30 = 20`
- `panXBoost = 20 * 2 = 40` (40% per second)

The background will drift in the direction of mouse movement, then gradually slow as the boost decays.

## Test Cases

Each test includes numerical verification (reading position/boost values via API) and visual verification where applicable (screenshot comparison to confirm visible change).

### Boost Effect Test

Verify that boost adds to base velocity.

**Setup:**
1. Set `panX = 100`, all others to 0
2. Set `panXPosition = 0`
3. Set `panXVelocity = 0` (zero base velocity for isolated test)
4. Set `panXBoost = 20`
5. Take screenshot A
6. Record initial `panXPosition`

**Wait:** 4 ticks (2 seconds)

**Numerical verification:**
7. Record final `panXPosition`
8. Expected: position changed (boost decays by 1 each tick; exact amount depends on frame timing)
9. Verify: final position has increased from initial

**Visual verification:**
10. Take screenshot B
11. Verify: screenshots A and B differ (background has moved horizontally)

### Boost Decay Test

Verify that boost decays toward zero by 1 per tick.

**Setup:**
1. Set `panXBoost = 5`

**Wait:** 3 ticks (1.5 seconds)

**Numerical verification:**
2. Verify: `panXBoost` is now 2

**Visual verification:** Not applicable (decay is internal state)

### Boost Reversal Test

Verify that boost reverses at boundaries.

**Setup:**
1. Set `panX = 100`, all others to 0
2. Set `panXPosition = 48` (near +50 boundary)
3. Set `panXVelocity = 0` (isolate boost effect)
4. Set `panXBoost = 10` (pushing toward boundary)
5. Take screenshot A

**Wait:** 2 ticks (1 second) - position reaches boundary, reversal occurs

**Numerical verification:**
6. Verify: `panXBoost` is now negative (reversed)
7. Verify: `panXPosition` is at or near 50 (boundary)

**Wait:** 2 more ticks (1 second)

**Visual verification:**
8. Take screenshot B
9. Verify: screenshots A and B differ (background moved toward boundary then back)

### Combined Velocity Test

Verify boost and base velocity combine correctly.

**Setup:**
1. Set `panX = 100`, all others to 0
2. Set `panXPosition = 0`
3. Set `panXVelocity = 5` (known base velocity)
4. Set `panXBoost = 10`
5. Take screenshot A
6. Record initial `panXPosition`

**Wait:** 4 ticks (2 seconds)

**Numerical verification:**
7. Record final `panXPosition`
8. Expected: position has changed significantly (base velocity + decaying boost)
9. Verify: position change is within tolerance of expected

**Visual verification:**
10. Take screenshot B
11. Verify: screenshots A and B differ (background has moved)

### Mouse Pan Boost Test

Verify mouse movement without button creates pan boost.

**Setup:**
1. Set `panX = 100`, `panY = 100`, all others to 0
2. Set `panXPosition = 0`, `panYPosition = 0`
3. Set `panXBoost = 0`, `panYBoost = 0`
4. Set `panXVelocity = 0`, `panYVelocity = 0`
5. Take screenshot A
6. Record initial `panXPosition`
7. Simulate mouse entering element at (25%, 50%)

**Wait:** 1 tick

8. Simulate mouse move to (75%, 50%) - 50% horizontal movement, no vertical

**Console verification:**
9. Verify console log: `mouse pan: deltaX=50 deltaY=0 → panXBoost=100 panYBoost=0`

**Numerical verification:**
10. Verify: `panXBoost` is 100
11. Verify: `panYBoost` is 0

**Wait:** 4 ticks (2 seconds)

12. Record final `panXPosition`
13. Expected: position has increased significantly (boost decays each tick)
14. Verify: `panXPosition` has increased significantly from initial

**Visual verification:**
15. Take screenshot B
16. Verify: screenshots A and B differ (background moved horizontally)

### Mouse Rotation Boost Test

Verify mouse movement with button held creates rotation boost.

**Setup:**
1. Set `rotX = 100`, `rotY = 100`, all others to 0
2. Set `rotXPosition = 0`, `rotYPosition = 0`
3. Set `rotXBoost = 0`, `rotYBoost = 0`
4. Set `rotXVelocity = 0`, `rotYVelocity = 0`
5. Take screenshot A
6. Record initial `rotXPosition`
7. Simulate mouse entering element at (50%, 25%)
8. Simulate mouse button down

**Wait:** 1 tick

9. Simulate mouse move to (50%, 75%) - 50% vertical movement, no horizontal

**Console verification:**
10. Verify console log: `mouse rotate: deltaX=0 deltaY=50 → rotXBoost=100 rotYBoost=0`

**Numerical verification:**
11. Verify: `rotXBoost` is 100
12. Verify: `rotYBoost` is 0

**Wait:** 4 ticks (2 seconds)

13. Record final `rotXPosition`
14. Verify: `rotXPosition` has changed significantly from initial

**Visual verification:**
15. Take screenshot B
16. Verify: screenshots A and B differ (background has visibly changed due to rotation)
