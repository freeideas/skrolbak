# Testing

Visual verification using Playwright screenshots.

## JavaScript API Requirements

The `<animated-background>` element must expose get/set methods for programmatic control during testing.

### Attribute Accessors

For each attribute (`src`, `pan-x`, `pan-y`, `pan-z`, `rot-x`, `rot-y`, `rot-z`):

```javascript
element.panX        // get current pan-x range (0-100)
element.panX = 50   // set pan-x range to 50%
```

Property names use camelCase: `panX`, `panY`, `panZ`, `rotX`, `rotY`, `rotZ`, `src`.

### Position Accessors

For each degree of freedom, expose the current position:

```javascript
element.panXPosition        // get current pan-x position (-50 to +50)
element.panXPosition = 0    // set pan-x position to center
```

Position values:
- `0%` = absolute center (starting position, center of background tile)
- `-50%` = minimum position
- `+50%` = maximum position

The attribute value constrains the normal operating range. For example, if `pan-x="30"`, the position normally stays within -15% to +15%, but the setter allows any value in -50% to +50%.

Property names: `panXPosition`, `panYPosition`, `panZPosition`, `rotXPosition`, `rotYPosition`, `rotZPosition`.

### Velocity Accessors

For each degree of freedom, expose the current velocity:

```javascript
element.panXVelocity        // get current pan-x velocity (% of range per second)
element.panXVelocity = 10   // set pan-x velocity to 10% per second
```

Property names: `panXVelocity`, `panYVelocity`, `panZVelocity`, `rotXVelocity`, `rotYVelocity`, `rotZVelocity`.

## Test Process

Each degree of freedom is tested independently using this process:

1. Zero every range except the one being tested
2. Set that range to 100%
3. Set that axis position to 0 (center)
4. Set that axis velocity to a significant value (e.g., 20% per second)
5. Record initial position, take a screenshot
6. Wait 1.5 seconds
7. Record final position, take another screenshot
8. Verify numerically: final position ≈ initial position + (velocity × 1.5)
9. Verify visually: the background moved as expected for that axis

## Test Cases

### Demo Form Test
- Verify form is visible and centered
- Verify glassmorphic styling (semi-transparent with blur)
- Verify form remains stationary while background animates

### Pan-X Test
- Set `panX = 100`, all others to 0
- Set `panXVelocity = 20`
- Verify: horizontal movement only

### Pan-Y Test
- Set `panY = 100`, all others to 0
- Set `panYVelocity = 20`
- Verify: vertical movement only

### Pan-Z Test (Zoom)
- Set `panZ = 100`, all others to 0
- Set `panZVelocity = 20`
- Verify: uniform scaling from center

### Rot-X Test
- Set `rotX = 100`, all others to 0
- Set `rotXVelocity = 20`
- Verify: forward/backward tilt with perspective distortion

### Rot-Y Test
- Set `rotY = 100`, all others to 0
- Set `rotYVelocity = 20`
- Verify: left/right tilt with perspective distortion

### Rot-Z Test
- Set `rotZ = 100`, all others to 0
- Set `rotZVelocity = 20`
- Verify: in-plane rotation only

### Deterministic Replay Test

Verify that the `t` attribute fast-forward produces identical state to real-time animation.

**Test process:**
1. Create element with all ranges at 100%, `t="0"`
2. Wait 30 seconds (until console shows `t=30`)
3. Record all position values: `panXPosition`, `panYPosition`, `panZPosition`, `rotXPosition`, `rotYPosition`, `rotZPosition`
4. Remove element, create new element with same ranges but `t="29"`
5. Wait 1 second (until console shows `t=30`)
6. Record all position values again
7. Verify: all six position values match between step 3 and step 6 (within floating-point tolerance)

**Why this works:**
- Both paths reach t=30 with identical PRNG sequences
- If fast-forward simulation is correct, positions must be identical
- Tests all six axes simultaneously

## Success Criteria

All tests pass when each isolated test shows only the expected motion between the two screenshots, and the deterministic replay test confirms matching positions.
