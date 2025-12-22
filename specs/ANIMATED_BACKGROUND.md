# Animated Background

A continuously scrolling background that creates visual interest behind the login form.

## Background Image

Uses `extart/bg.jpg` as the source image, tiled to fill the viewport.

## Scrolling

The background scrolls in a direction specified by angle θ (in degrees), using compass-style orientation:

### Direction Formula

Given scroll angle θ and speed s (pixels per second):

- **dx = s × sin(θ)** — horizontal displacement per second
- **dy = −s × cos(θ)** — vertical displacement per second

### Examples

| Angle | Direction      | dx      | dy      |
|-------|----------------|---------|---------|
| 0°    | Up             | 0       | −s      |
| 90°   | Right          | +s      | 0       |
| 180°  | Down           | 0       | +s      |
| 270°  | Left           | −s      | 0       |
| 45°   | Up-right       | +0.707s | −0.707s |
| 225°  | Down-left      | −0.707s | +0.707s |

### Wrapping

The background tiles seamlessly. Portions scrolling off one edge reappear on the opposite edge.

### Parameters

- **Scroll angle**: 45 degrees
- **Scroll speed**: 50 pixels per second
