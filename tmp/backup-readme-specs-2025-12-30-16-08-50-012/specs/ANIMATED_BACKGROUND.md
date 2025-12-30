The `<animated-background>` element is a custom HTML element that renders a tiled background image on a virtual wall and animates it over time in six degrees of freedom, with each degree of freedom constrained by percentage-based attributes.

## Element overview

- Tag name: `<animated-background>` (autonomous custom element extending `HTMLElement`).
- Rendering model:  
  - Internally creates a 3D-transformed “wall” surface that is 10× viewport width and 10× viewport height.  
  - The specified image is tiled across this wall; the wall’s center aligns with the center of the image.  
  - The visible viewport corresponds to the browser window; animation is produced by transforming the wall, not the viewport.

## Attributes

All attributes are optional unless stated otherwise and use lowercase names consistent with custom element conventions.

### Image source

- `src` (required)
  - Type: string (URL).
  - Semantics: URL of the image used as the background texture of the virtual wall.
  - Behavior:
    - The image is tiled infinitely over the wall using a repeating pattern in both X and Y directions.
    - The center of one tile is at the geometric center of the wall; additional tiles repeat in all directions.

### Debug/replay attribute

- `t` (optional)
  - Type: non-negative integer, default 0.
  - Semantics: Starting tick for the animation's deterministic state.
  - Behavior: When set to N > 0, the element instantly simulates N seconds of state evolution before beginning visible animation. See "Deterministic Randomness" in Animation model.

### Range attributes (degrees of freedom)

Each degree of freedom has a *range* attribute expressed as a percentage between 0 and 100 (inclusive), where 0% means no movement is allowed and 100% means the full potential range is allowed.  

Six attributes:

- Translation (pan) ranges:  
  - `pan-x`  
  - `pan-y`  
  - `pan-z`  

- Rotation ranges:  
  - `rot-x`  
  - `rot-y`  
  - `rot-z`  

All range attributes:

- Type: number (float or integer), clamped to [0, 100].
- Default: 0 (no motion) if omitted.  
- Zero is allowed for range, but actual *velocity* for that axis must never be zero (see below).

#### Rotation ranges

For `rot-x`, `rot-y`, `rot-z`:

- Potential rotation interval: $$[-45^\circ, +45^\circ]$$ for each axis.  
- Mapping from percentage to allowed interval:  
  - Let $$p$$ be the attribute value in percent.  
  - Allowed rotation angle magnitude is $$(p / 100) \times 45^\circ$$.  
  - Effective allowed interval is $$[-a, +a]$$ where $$a = (p / 100) \times 45^\circ$$.  
- Examples:
  - `rot-x="100"` ⇒ rotation X allowed from $$-45^\circ$$ to $$+45^\circ$$.
  - `rot-y="50"` ⇒ rotation Y allowed from $$-22.5^\circ$$ to $$+22.5^\circ$$.  

#### Pan ranges for X and Y

For `pan-x` and `pan-y`:

- The wall dimensions are 10× viewport width and 10× viewport height.  
- For an axis with 100% range:  
  - 100% pan along X allows the wall to move so that:  
    - At one extreme, the *left* edge of the wall is flush with the *left* edge of the viewport.  
    - At the opposite extreme, the *right* edge of the wall is flush with the *right* edge of the viewport.  
  - 100% pan along Y allows similar extremes for top/bottom.  
- For a pan range $$p$$ in percent:  
  - The actual allowed translation interval is linearly scaled so that the full 100% range corresponds to the extreme positions described above, and a smaller percentage proportionally reduces the max displacement from the center.  

#### Pan range for Z (zoom)

For `pan-z`:

- Z pan is defined as zoom of the wall relative to the viewport.  
- Potential zoom interval: from 50% to 150% of the nominal scale (1.0).  
- Mapping from percentage to allowed zoom interval:  
  - Let $$p$$ be the attribute value in percent.  
  - At 100%, zoom can animate over the full interval [0.5, 1.5].  
  - At smaller $$p$$, the zoom interval is linearly shrunk around the nominal zoom (1.0), so that 0% implies no zoom change and 100% implies full [0.5, 1.5] range.  

## Animation model

### State variables per axis

For each axis and degree of freedom, the element maintains:

- Current value (position or rotation, or zoom for Z pan).  
- Velocity, expressed as a signed percentage per second of the allowed range for that axis.  

Axes:

- `pan-x`, `pan-y`, `pan-z` (zoom).  
- `rot-x`, `rot-y`, `rot-z`.  

### Velocity semantics

- Velocity units: “percent of allowed range per second”.  
  - A velocity magnitude of 1% means that 1% of that axis’s allowed range is traversed in one second.  
  - Velocities may be positive or negative, determining direction.  
- Zero velocity for any degree of freedom is not permitted as a stable state.  
  - When velocity changes over time (see below), transitions that would result in exactly 0% must skip over 0 and choose a non-zero sign, preserving continuous motion.  

### Velocity evolution

- Time discretization: velocity is updated once per second (when `t` increments).
- For each axis independently:
  - At each one-second tick, the *magnitude* of the velocity is either increased by 1 percentage point per second or decreased by 1 percentage point per second.
  - The choice is determined by `prng(t, "{axis}-vel")` (see Deterministic Randomness), but the result must never be 0.
  - Direction (sign) is preserved except when reversed at range boundaries (see next section).  

### Range boundary behavior

- For each axis, motion is constrained to the computed allowed interval (rotation or pan/zoom).  
- Whenever the current value reaches or attempts to exceed an endpoint of that interval:  
  - The corresponding velocity for that axis is immediately reversed in sign.  
  - Example:  
    - For `rot-x="100"`, the allowed range is $$[-45^\circ, +45^\circ]$$.  
    - If rotation X reaches $$+45^\circ$$, the rotation X velocity is multiplied by $$-1$$, so subsequent motion proceeds back toward $$-45^\circ$$.  

### Initialization

- On element connection to the document:
  - All position values start at 0 (centered for pan, no rotation for rot, nominal scale for zoom).
  - Each axis with a non-zero range is assigned an initial velocity of either -1% or +1% (deterministically chosen based on the axis, see Deterministic Randomness below), ensuring continuous motion.
  - Axes with range = 0 have no velocity and remain stationary.

### Deterministic Randomness

All "random" choices must be deterministic and reproducible for debugging purposes.

**Time counter:**
- A global tick counter `t` starts at the value of the `t` attribute (default 0) when the element connects.
- `t` increments by 1 each second (at the same time as velocity updates).
- On each tick, log to console: `t=0`, `t=1`, `t=2`, etc.

**The `t` attribute:**
- Type: non-negative integer, default 0.
- When `t` is set to a value N > 0, the element fast-forwards to that state on initialization:
  1. Simulate state from t=0 to t=N-1 without rendering (instant computation)
  2. For each simulated tick: apply velocity to position, check boundaries, update velocity magnitude
  3. Begin normal animation and console logging at t=N
- This allows reproducing bug reports: setting `t="23"` starts the animation in the exact state it would have reached after 23 seconds.

**Seeded pseudo-random function:**
- All random choices use a deterministic function `prng(t, salt) → boolean` where:
  - `t` is the current tick counter
  - `salt` is a unique string for each decision point (e.g., `"panX-init"`, `"rotY-vel"`)
- The function must be deterministic: same `t` and `salt` always produce the same result.
- Implementation may use any hash-based approach (e.g., hash `t + salt` and check if result is even/odd).

**Usage:**
- Initial velocity direction: `prng(0, "{axis}-init")` → true = +1, false = -1
- Velocity magnitude change: `prng(t, "{axis}-vel")` → true = +1, false = -1

This allows bug reports like "looked weird at t=23" to be reproduced exactly.  

## Processing model

This section describes a possible normative processing model consistent with the above semantics.

1. **Parsing attributes**  
   - On construction or attribute changes, range attributes are parsed as floating-point percentages and clamped to [0, 100].
   - `src` is resolved to an absolute URL as for regular image resources.  

2. **Layout and rendering**  
   - The element establishes a containing block matching the viewport or its own box, and creates an internal child element representing the wall.  
   - The wall element is given dimensions equal to 10× the width and 10× the height of the viewport or containing block.  
   - The wall’s background is set to the `src` image and configured to repeat in both directions, with its center aligned to the wall’s center.  

3. **Transform application**  
   - On each animation frame, transforms for pan and rotation are computed from the current state variables:  
     - `pan-x` and `pan-y` map to translations along the X and Y axes.  
     - `pan-z` maps to scaling (zoom) of the wall.  
     - `rot-x`, `rot-y`, `rot-z` map to 3D rotations around the respective axes.  
   - The combined transform is applied to the wall element, using CSS transforms or equivalent.

4. **Animation loop**  
   - A time-based animation loop (for example, driven by `requestAnimationFrame`) integrates velocities over time to update current values along each axis.
   - Once per second, a separate tick updates velocities (increase/decrease magnitude by 1% per second, skipping 0, and handling sign reversals at boundaries).  

## Example usage

```html
<animated-background
  src="stars.jpg"
  pan-x="100"
  pan-y="75"
  pan-z="50"
  rot-x="50"
  rot-y="100"
  rot-z="25">
</animated-background>
```

This example declares an `<animated-background>` that:  
- Allows full horizontal panning, 75% of the vertical panning range, and 50% of the zoom range (somewhere between 50% and 150%).  
- Allows 50% tilt around X, full tilt around Y, and 25% rotation around Z, with continuous velocity-based motion within those ranges.
