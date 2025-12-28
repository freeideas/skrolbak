# Rendering

Documents dynamic tiling for complete viewport coverage, 3D perspective for realistic foreshortening, and z-index layering.

## $REQ_RENDERING_001: Complete Viewport Coverage
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Rendering")

The viewport must always be fully covered by tiles, regardless of transform state. No gaps may appear at any combination of pan, rotation, and zoom.

## $REQ_RENDERING_002: 3D Perspective Foreshortening
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Rendering")

CSS `perspective` must be applied for realistic foreshortening on X/Y rotations.

## $REQ_RENDERING_003: Z-Index Layering
**Source:** ./specs/ANIMATED_BACKGROUND.md (Section: "Rendering")

The background renders behind all other content (lowest z-index).
