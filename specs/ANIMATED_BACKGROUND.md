# Animated Background

A full-viewport animated background with a tiled image viewed through a virtual camera that drifts organically through six degrees of freedom.

## Web Component

Custom HTML element: `<animated-background>`

### Attributes

| Attribute       | Description                              | Default |
| --------------- | ---------------------------------------- | ------- |
| `src`           | Path to the background image (required)  | —       |
| `start-offset`  | Time offset in seconds (for debugging)   | 0       |
| `x-pan-pps-min` | X-axis pan velocity minimum (pixels/sec) | -5      |
| `x-pan-pps-max` | X-axis pan velocity maximum (pixels/sec) | 5       |
| `y-pan-pps-min` | Y-axis pan velocity minimum (pixels/sec) | -5      |
| `y-pan-pps-max` | Y-axis pan velocity maximum (pixels/sec) | 5       |
| `x-rot-min`     | X-axis rotation minimum (degrees)        | -10     |
| `x-rot-max`     | X-axis rotation maximum (degrees)        | 10      |
| `y-rot-min`     | Y-axis rotation minimum (degrees)        | -10     |
| `y-rot-max`     | Y-axis rotation maximum (degrees)        | 10      |
| `z-rot-min`     | Z-axis rotation minimum (degrees)        | -20     |
| `z-rot-max`     | Z-axis rotation maximum (degrees)        | 20      |
| `z-pan-min`     | Zoom minimum (percent)                   | 50      |
| `z-pan-max`     | Zoom maximum (percent)                   | 200     |

### Usage

```html
<animated-background src="bg.jpg"></animated-background>
```

The element fills its parent container. For full-viewport backgrounds, use CSS `position: fixed` with full width/height.

## Camera Model

The background is an infinite tiled plane viewed through a virtual camera with six degrees of freedom:

| DoF   | Unit       | Bounds   | Description                |
| ----- | ---------- | -------- | -------------------------- |
| X-pan | pixels/sec | infinite | Horizontal scroll velocity |
| Y-pan | pixels/sec | infinite | Vertical scroll velocity   |
| X-rot | degrees    | bounded  | Tilt forward/backward      |
| Y-rot | degrees    | bounded  | Tilt left/right            |
| Z-rot | degrees    | bounded  | In-plane spin              |
| Zoom  | percent    | bounded  | Scale (50-200%)            |

Initial state: all velocities 0, all rotations 0°, zoom 100%.

## Animation System

### Deterministic Random Walk

Each parameter has a velocity that changes every second via a deterministic noise function:

```
noise(seconds, channel) = frac(sin(seconds × 12.9898 + channel × 78.233) × 43758.5453)
direction = noise < 0.5 ? -1 : +1
```

- Velocity changes by ±1% of parameter range per second
- Maximum velocity is ±10% of parameter range per second
- Channel indices: 0=X-pan, 1=Y-pan, 2=X-rot, 3=Y-rot, 4=Z-rot, 5=Zoom

### Boundary Behavior

**Bounded parameters (rotations, zoom):** Value clamps at limit, velocity reverses.

**Unbounded parameters (pan):** Velocity clamps at limit, acceleration reverses.

### Frame-Rate Independence

Animation state is computed analytically from elapsed time, not accumulated per-frame. Given time `T`, compute position as the integral of velocity from 0 to T. This guarantees identical output regardless of frame rate.

### Debug Logging

Log the current time offset to the console once per second:

```
t=0
t=1
t=2
...
```

This enables bug reports to reference a specific time (e.g., "glitch at t=47") that can be reproduced using the `start-offset` attribute.

## Rendering

### Dynamic Tiling

The viewport must always be fully covered by tiles, regardless of transform state. Tiles are rendered dynamically:

1. Compute the inverse transform to find viewport corners in tile-space
2. Determine which tile grid cells intersect the visible area
3. Render exactly those tiles with the current transform applied

This guarantees complete coverage at any combination of pan, rotation, and zoom—no fixed-size tile region can achieve this.

### 3D Perspective

Apply CSS `perspective` for realistic foreshortening on X/Y rotations.

### Z-Index

The background renders behind all other content (lowest z-index).
