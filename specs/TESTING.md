# Testing

Visual verification using Playwright screenshots.

## Test Cases

### Test 1: Demo Form

Verify:
- Form is visible and centered
- Glassmorphic styling (semi-transparent with blur)

### Test 2: Background Coverage

Verify the tiled background completely covers the viewport with no gaps. Test at multiple time offsets (T=0, T=9) to confirm dynamic tiling works correctly.

### Test 3: Animation

Take two screenshots 5 seconds apart. Verify:
- Background visibly changes (pan, rotation, zoom)
- Demo form remains stationary

## Isolated Motion Tests

Each test isolates one degree of freedom. Take screenshots 5 seconds apart.

### X-Pan Only
```html
<animated-background src="bg.jpg"
  x-pan-pps-min="-20" x-pan-pps-max="20"
  y-pan-pps-min="0" y-pan-pps-max="0"
  x-rot-min="0" x-rot-max="0" y-rot-min="0" y-rot-max="0" z-rot-min="0" z-rot-max="0"
  z-pan-min="100" z-pan-max="100"></animated-background>
```
Verify: horizontal scroll only.

### Y-Pan Only
```html
<animated-background src="bg.jpg"
  x-pan-pps-min="0" x-pan-pps-max="0"
  y-pan-pps-min="-20" y-pan-pps-max="20"
  x-rot-min="0" x-rot-max="0" y-rot-min="0" y-rot-max="0" z-rot-min="0" z-rot-max="0"
  z-pan-min="100" z-pan-max="100"></animated-background>
```
Verify: vertical scroll only.

### X-Rotation Only
```html
<animated-background src="bg.jpg"
  x-pan-pps-min="0" x-pan-pps-max="0" y-pan-pps-min="0" y-pan-pps-max="0"
  x-rot-min="-30" x-rot-max="30"
  y-rot-min="0" y-rot-max="0" z-rot-min="0" z-rot-max="0"
  z-pan-min="100" z-pan-max="100"></animated-background>
```
Verify: forward/backward tilt with perspective distortion.

### Y-Rotation Only
```html
<animated-background src="bg.jpg"
  x-pan-pps-min="0" x-pan-pps-max="0" y-pan-pps-min="0" y-pan-pps-max="0"
  x-rot-min="0" x-rot-max="0"
  y-rot-min="-30" y-rot-max="30"
  z-rot-min="0" z-rot-max="0"
  z-pan-min="100" z-pan-max="100"></animated-background>
```
Verify: left/right tilt with perspective distortion.

### Z-Rotation Only
```html
<animated-background src="bg.jpg"
  x-pan-pps-min="0" x-pan-pps-max="0" y-pan-pps-min="0" y-pan-pps-max="0"
  x-rot-min="0" x-rot-max="0" y-rot-min="0" y-rot-max="0"
  z-rot-min="-45" z-rot-max="45"
  z-pan-min="100" z-pan-max="100"></animated-background>
```
Verify: in-plane rotation only.

### Zoom Only
```html
<animated-background src="bg.jpg"
  x-pan-pps-min="0" x-pan-pps-max="0" y-pan-pps-min="0" y-pan-pps-max="0"
  x-rot-min="0" x-rot-max="0" y-rot-min="0" y-rot-max="0" z-rot-min="0" z-rot-max="0"
  z-pan-min="50" z-pan-max="200"></animated-background>
```
Verify: uniform scaling from center.

## Success Criteria

All tests pass when:
1. Demo form visible, centered, glassmorphic
2. Background tiles cover viewport completely
3. Background animates while form stays fixed
4. Each isolated test shows only the expected motion
