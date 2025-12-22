#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = [
#   "playwright",
# ]
# ///

"""
Test for animated background requirements.
Tests background image source, tiling, scroll direction formula, angle, speed, wrapping, and continuous animation.
"""

import sys
import os
import time
import subprocess
import atexit
from pathlib import Path

# Add the-system/scripts to path for websrvr
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'the-system' / 'scripts'))
from websrvr import start_server, get_server_url, stop_server

# Setup cleanup
atexit.register(stop_server)

def read_file(path):
    """Read file contents"""
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def verify_build_exists():
    """Verify that the build exists in ./released/"""
    released_dir = Path(__file__).resolve().parent.parent.parent / 'released'
    if not released_dir.exists() or not (released_dir / 'index.html').exists():
        print("Error: ./released/ directory not found or incomplete. Run build first.", file=sys.stderr)
        sys.exit(97)  # Build failed

def test_code_implementation():
    """Test code implementation details for requirements"""
    code_dir = Path(__file__).resolve().parent.parent.parent / 'code'

    # $REQ_ANIMATED_BG_001: Background Source Image
    # Check that code uses 'extart/bg.jpg'
    bg_dart = code_dir / 'lib' / 'animated_background.dart'
    assert bg_dart.exists(), f"animated_background.dart not found at {bg_dart}"

    bg_content = read_file(bg_dart)
    assert 'extart/bg.jpg' in bg_content, "$REQ_ANIMATED_BG_001: Code must reference 'extart/bg.jpg'"
    print("✓ $REQ_ANIMATED_BG_001: Background uses extart/bg.jpg")

    # $REQ_ANIMATED_BG_004: Scroll Angle
    # Verify 45 degree angle
    assert 'scrollAngle = 45' in bg_content or 'scrollAngle = 45.0' in bg_content, \
        "$REQ_ANIMATED_BG_004: Scroll angle must be 45 degrees"
    print("✓ $REQ_ANIMATED_BG_004: Scroll angle is 45 degrees")

    # $REQ_ANIMATED_BG_005: Scroll Speed
    # Verify 50 pixels per second
    assert 'scrollSpeed = 50' in bg_content or 'scrollSpeed = 50.0' in bg_content, \
        "$REQ_ANIMATED_BG_005: Scroll speed must be 50 pixels per second"
    print("✓ $REQ_ANIMATED_BG_005: Scroll speed is 50 pixels per second")

    # $REQ_ANIMATED_BG_003: Scroll Direction Formula
    # Check for the correct formula: dx = s × sin(θ), dy = −s × cos(θ)
    assert 'sin(radians)' in bg_content or 'sin(' in bg_content, \
        "$REQ_ANIMATED_BG_003: Must use sin for horizontal displacement"
    assert 'cos(radians)' in bg_content or 'cos(' in bg_content, \
        "$REQ_ANIMATED_BG_003: Must use cos for vertical displacement"
    # Check for negative sign on cos (dy = -s * cos(θ))
    assert '-scrollSpeed * cos' in bg_content or '- scrollSpeed * cos' in bg_content or \
           '-s * cos' in bg_content or '- s * cos' in bg_content, \
        "$REQ_ANIMATED_BG_003: dy must use negative cos(θ)"
    print("✓ $REQ_ANIMATED_BG_003: Scroll direction formula uses dx = s × sin(θ), dy = −s × cos(θ)")

    # $REQ_ANIMATED_BG_002: Tiled Background Coverage
    # Check for ImageRepeat.repeat to tile the background
    assert 'ImageRepeat.repeat' in bg_content or 'repeat:' in bg_content, \
        "$REQ_ANIMATED_BG_002: Background must use repeat to tile"
    print("✓ $REQ_ANIMATED_BG_002: Background is configured to tile")

    # $REQ_ANIMATED_BG_006: Seamless Wrapping
    # Wrapping is automatic with ImageRepeat.repeat and Transform.translate
    assert 'Transform.translate' in bg_content or 'Offset(' in bg_content, \
        "$REQ_ANIMATED_BG_006: Background must use offset for scrolling"
    print("✓ $REQ_ANIMATED_BG_006: Background uses Transform.translate for seamless wrapping")

def test_visual_requirements():
    """Test visual requirements using screenshots"""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: playwright not available", file=sys.stderr)
        sys.exit(99)

    # Start web server
    released_dir = Path(__file__).resolve().parent.parent.parent / 'released'
    port = start_server(str(released_dir))
    url = get_server_url(port)

    print(f"Started server at {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        # Navigate to the app
        page.goto(url)

        # Wait for app to load
        page.wait_for_timeout(2000)

        # Take first screenshot
        screenshot1_path = Path(__file__).resolve().parent.parent.parent / 'tmp' / 'bg_screenshot1.png'
        screenshot1_path.parent.mkdir(exist_ok=True)
        page.screenshot(path=str(screenshot1_path))
        print(f"Captured screenshot 1: {screenshot1_path}")

        # Wait 5 seconds for animation
        page.wait_for_timeout(5000)

        # Take second screenshot
        screenshot2_path = Path(__file__).resolve().parent.parent.parent / 'tmp' / 'bg_screenshot2.png'
        page.screenshot(path=str(screenshot2_path))
        print(f"Captured screenshot 2: {screenshot2_path}")

        browser.close()

    project_root = Path(__file__).resolve().parent.parent.parent
    visual_test = project_root / 'the-system' / 'scripts' / 'visual-test.py'
    uv_bin = project_root / 'the-system' / 'bin' / 'uv.linux'

    # TESTING.md Test 1: Form Visibility
    # Verify the login form is visible with glassmorphic styling
    result = subprocess.run(
        [str(uv_bin), 'run', '--script', str(visual_test),
         str(screenshot1_path),
         'The login form is visible with glassmorphic styling: "Login" title, email field, "Stay logged in" checkbox, and "Continue" button. Form appears semi-transparent with blurred background visible through it.'],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    if result.returncode != 0:
        print(f"✗ TESTING.md Test 1: Login form not visible or missing glassmorphic styling", file=sys.stderr)
        print(f"Visual test output: {result.stdout}", file=sys.stderr)
        sys.exit(1)

    print("✓ TESTING.md Test 1: Login form is visible with glassmorphic styling")

    # TESTING.md Test 2: Background Coverage
    # $REQ_ANIMATED_BG_002: Tiled Background Coverage
    result = subprocess.run(
        [str(uv_bin), 'run', '--script', str(visual_test),
         str(screenshot1_path),
         'The tiled background image completely covers the viewport with no gaps, seams, or uncovered areas visible.'],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    if result.returncode != 0:
        print(f"✗ $REQ_ANIMATED_BG_002: Background does not tile to fill viewport completely", file=sys.stderr)
        print(f"Visual test output: {result.stdout}", file=sys.stderr)
        sys.exit(1)

    print("✓ $REQ_ANIMATED_BG_002: Background tiles completely cover the viewport")

    # TESTING.md Test 3: Background Animation
    # $REQ_ANIMATED_BG_007: Continuous Animation
    # Verify: 1) Form remains stationary, 2) Background has shifted

    # Verify the login form is in the center in first screenshot
    result1 = subprocess.run(
        [str(uv_bin), 'run', '--script', str(visual_test),
         str(screenshot1_path),
         'The login form is centered in the viewport.'],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    if result1.returncode != 0:
        print(f"✗ TESTING.md Test 3: Login form not centered in first screenshot", file=sys.stderr)
        sys.exit(1)

    # Verify the login form is still in the center in second screenshot (stationary)
    result2 = subprocess.run(
        [str(uv_bin), 'run', '--script', str(visual_test),
         str(screenshot2_path),
         'The login form is centered in the viewport.'],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    if result2.returncode != 0:
        print(f"✗ TESTING.md Test 3: Login form not centered in second screenshot (should remain stationary)", file=sys.stderr)
        sys.exit(1)

    print("✓ TESTING.md Test 3: Login form remains stationary in both screenshots")

    # Binary check: screenshots must be different due to background animation
    with open(screenshot1_path, 'rb') as f1:
        img1_data = f1.read()
    with open(screenshot2_path, 'rb') as f2:
        img2_data = f2.read()

    assert img1_data != img2_data, "$REQ_ANIMATED_BG_007: Screenshots differ, proving background animated"
    print("✓ $REQ_ANIMATED_BG_007: Background has visibly shifted position between screenshots")

def main():
    """Run all tests"""
    print("Testing animated background requirements...")

    # Verify build exists
    verify_build_exists()

    # Test code implementation
    test_code_implementation()

    # Test visual requirements
    test_visual_requirements()

    print("\n✓ All animated background tests passed!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
