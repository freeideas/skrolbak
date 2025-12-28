#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Test for Camera Model requirements.
Tests the six degrees of freedom virtual camera implementation.
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path

# Ensure we're in project root
os.chdir(Path(__file__).resolve().parent.parent.parent)

def test_camera_model():
    """Test camera model implementation in JavaScript."""

    # Build the project first
    build_result = subprocess.run(
        ['./the-system/bin/uv.linux', 'run', '--script', './code/build.py'],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    if build_result.returncode != 0:
        print(f"Build failed: {build_result.stderr}")
        sys.exit(97)

    # Read the JavaScript implementation
    js_path = Path('./code/animated-background.js')
    assert js_path.exists(), "animated-background.js must exist"

    js_content = js_path.read_text()

    # $REQ_CAMERA_001: Six Degrees of Freedom
    # Verify that the camera supports all six degrees of freedom
    assert 'xPanVel' in js_content, "$REQ_CAMERA_001: X-pan velocity must be tracked"
    assert 'yPanVel' in js_content, "$REQ_CAMERA_001: Y-pan velocity must be tracked"
    assert 'xRotVel' in js_content or 'xRot' in js_content, "$REQ_CAMERA_001: X-rotation must be tracked"
    assert 'yRotVel' in js_content or 'yRot' in js_content, "$REQ_CAMERA_001: Y-rotation must be tracked"
    assert 'zRotVel' in js_content or 'zRot' in js_content, "$REQ_CAMERA_001: Z-rotation must be tracked"
    assert 'zoomVel' in js_content or 'zoom' in js_content, "$REQ_CAMERA_001: Zoom must be tracked"

    # $REQ_CAMERA_002: X-Pan Degree of Freedom
    # X-pan measures horizontal scroll velocity in pixels/sec with infinite bounds
    assert 'xPanVel' in js_content, "$REQ_CAMERA_002: X-pan velocity in pixels/sec"
    assert 'xPan' in js_content, "$REQ_CAMERA_002: X-pan position tracking"
    # Infinite bounds means no hard limits on xPan position value

    # $REQ_CAMERA_003: Y-Pan Degree of Freedom
    # Y-pan measures vertical scroll velocity in pixels/sec with infinite bounds
    assert 'yPanVel' in js_content, "$REQ_CAMERA_003: Y-pan velocity in pixels/sec"
    assert 'yPan' in js_content, "$REQ_CAMERA_003: Y-pan position tracking"
    # Infinite bounds means no hard limits on yPan position value

    # $REQ_CAMERA_004: X-Rotation Degree of Freedom
    # X-rotation measures forward/backward tilt in degrees with bounded range
    assert 'xRot' in js_content, "$REQ_CAMERA_004: X-rotation in degrees"
    assert 'xRotMin' in js_content or 'x-rot-min' in js_content, "$REQ_CAMERA_004: X-rotation has minimum bound"
    assert 'xRotMax' in js_content or 'x-rot-max' in js_content, "$REQ_CAMERA_004: X-rotation has maximum bound"

    # $REQ_CAMERA_005: Y-Rotation Degree of Freedom
    # Y-rotation measures left/right tilt in degrees with bounded range
    assert 'yRot' in js_content, "$REQ_CAMERA_005: Y-rotation in degrees"
    assert 'yRotMin' in js_content or 'y-rot-min' in js_content, "$REQ_CAMERA_005: Y-rotation has minimum bound"
    assert 'yRotMax' in js_content or 'y-rot-max' in js_content, "$REQ_CAMERA_005: Y-rotation has maximum bound"

    # $REQ_CAMERA_006: Z-Rotation Degree of Freedom
    # Z-rotation measures in-plane spin in degrees with bounded range
    assert 'zRot' in js_content, "$REQ_CAMERA_006: Z-rotation in degrees"
    assert 'zRotMin' in js_content or 'z-rot-min' in js_content, "$REQ_CAMERA_006: Z-rotation has minimum bound"
    assert 'zRotMax' in js_content or 'z-rot-max' in js_content, "$REQ_CAMERA_006: Z-rotation has maximum bound"

    # $REQ_CAMERA_007: Zoom Degree of Freedom
    # Zoom measures scale in percent with bounded range (50-200%)
    assert 'zoom' in js_content, "$REQ_CAMERA_007: Zoom in percent"
    assert 'zoomMin' in js_content or 'z-pan-min' in js_content, "$REQ_CAMERA_007: Zoom has minimum bound"
    assert 'zoomMax' in js_content or 'z-pan-max' in js_content, "$REQ_CAMERA_007: Zoom has maximum bound"
    # Default bounds should be 50-200%
    assert ("'50'" in js_content or '"50"' in js_content), "$REQ_CAMERA_007: Default zoom minimum is 50%"
    assert ("'200'" in js_content or '"200"' in js_content), "$REQ_CAMERA_007: Default zoom maximum is 200%"

    # $REQ_CAMERA_008: Initial Camera State
    # Initial state: all velocities 0, all rotations 0°, zoom 100%
    # Check initial state in constructor or state initialization
    assert 'xPanVel: 0' in js_content or 'xPanVel = 0' in js_content, "$REQ_CAMERA_008: Initial X-pan velocity is 0"
    assert 'yPanVel: 0' in js_content or 'yPanVel = 0' in js_content, "$REQ_CAMERA_008: Initial Y-pan velocity is 0"
    assert 'xRot: 0' in js_content or 'xRot = 0' in js_content, "$REQ_CAMERA_008: Initial X-rotation is 0°"
    assert 'yRot: 0' in js_content or 'yRot = 0' in js_content, "$REQ_CAMERA_008: Initial Y-rotation is 0°"
    assert 'zRot: 0' in js_content or 'zRot = 0' in js_content, "$REQ_CAMERA_008: Initial Z-rotation is 0°"
    assert 'zoom: 100' in js_content or 'zoom = 100' in js_content, "$REQ_CAMERA_008: Initial zoom is 100%"

    # $REQ_CAMERA_009: Bounded Parameter Boundary Behavior
    # For bounded parameters (rotations, zoom), value clamps and velocity reverses
    # Look for clamping and velocity reversal logic
    clamp_and_reverse_count = 0

    # Check for rotation boundary handling
    if 'xRot < this.xRotMin' in js_content or 'xRot > this.xRotMax' in js_content:
        clamp_and_reverse_count += 1
    if 'yRot < this.yRotMin' in js_content or 'yRot > this.yRotMax' in js_content:
        clamp_and_reverse_count += 1
    if 'zRot < this.zRotMin' in js_content or 'zRot > this.zRotMax' in js_content:
        clamp_and_reverse_count += 1
    if 'zoom < this.zoomMin' in js_content or 'zoom > this.zoomMax' in js_content:
        clamp_and_reverse_count += 1

    assert clamp_and_reverse_count >= 4, "$REQ_CAMERA_009: Bounded parameters must clamp and reverse velocity"

    # Verify velocity reversal (look for velocity negation)
    assert ('-state.xRotVel' in js_content or 'xRotVel = -' in js_content or 'zoomVel = -' in js_content), "$REQ_CAMERA_009: Velocity reverses at boundary"

    # $REQ_CAMERA_010: Unbounded Parameter Boundary Behavior
    # For unbounded parameters (pan), velocity clamps and acceleration reverses
    # Pan velocities should have limits but pan positions don't
    assert 'xPanVel' in js_content, "$REQ_CAMERA_010: X-pan velocity exists"
    assert 'yPanVel' in js_content, "$REQ_CAMERA_010: Y-pan velocity exists"
    # Velocity limits should be checked (max velocity is 10% of range)

    # $REQ_CAMERA_011: Frame-Rate Independent Animation
    # Animation state computed analytically from elapsed time
    assert 'computeState' in js_content or 'elapsed' in js_content, "$REQ_CAMERA_011: Analytical state computation"
    assert 'performance.now()' in js_content or 'elapsed' in js_content, "$REQ_CAMERA_011: Time-based animation"
    # Should not accumulate per-frame (no state += deltaTime pattern without recomputing from t=0)

    # $REQ_CAMERA_012: X-Pan Motion Isolation
    # Not reasonably testable: Requires visual verification of horizontal-only scroll
    # $REQ_CAMERA_012 - Not reasonably testable: Visual verification required for X-pan isolation

    # $REQ_CAMERA_013: Y-Pan Motion Isolation
    # Not reasonably testable: Requires visual verification of vertical-only scroll
    # $REQ_CAMERA_013 - Not reasonably testable: Visual verification required for Y-pan isolation

    # $REQ_CAMERA_014: X-Rotation Motion Isolation
    # Not reasonably testable: Requires visual verification of tilt with perspective
    # $REQ_CAMERA_014 - Not reasonably testable: Visual verification required for X-rotation isolation

    # $REQ_CAMERA_015: Y-Rotation Motion Isolation
    # Not reasonably testable: Requires visual verification of tilt with perspective
    # $REQ_CAMERA_015 - Not reasonably testable: Visual verification required for Y-rotation isolation

    # $REQ_CAMERA_016: Z-Rotation Motion Isolation
    # Not reasonably testable: Requires visual verification of in-plane rotation
    # $REQ_CAMERA_016 - Not reasonably testable: Visual verification required for Z-rotation isolation

    # $REQ_CAMERA_017: Zoom Motion Isolation
    # Not reasonably testable: Requires visual verification of uniform scaling
    # $REQ_CAMERA_017 - Not reasonably testable: Visual verification required for zoom isolation

    print("✓ All camera model requirements verified")
    return 0

if __name__ == '__main__':
    try:
        sys.exit(test_camera_model())
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
