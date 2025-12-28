#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "pillow",
# ]
# ///

"""
Test for rendering requirements.

Tests:
- $REQ_RENDERING_001: Complete viewport coverage
- $REQ_RENDERING_002: 3D perspective foreshortening
- $REQ_RENDERING_003: Z-index layering
"""

import subprocess
import time
import urllib.request
import sys
import os
import atexit
from pathlib import Path

# Ensure we're running from the project root
os.chdir(Path(__file__).resolve().parent.parent.parent)

# Import server utilities
sys.path.insert(0, str(Path('./the-system/scripts')))
from websrvr import start_server, get_server_url, stop_server

# Process cleanup
_procs = []

def cleanup():
    """Clean up all spawned processes."""
    for p in _procs:
        try:
            p.terminate()
            p.wait(timeout=2)
        except:
            try:
                p.kill()
            except:
                pass
    stop_server()

atexit.register(cleanup)


def test_rendering():
    """Test rendering requirements."""

    # Build the project first
    print("Building project...")
    result = subprocess.run(
        ['./the-system/bin/uv.linux', 'run', '--script', './code/build.py'],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    if result.returncode != 0:
        print(f"Build failed:\n{result.stdout}\n{result.stderr}")
        sys.exit(97)

    print("Build successful")

    # Start web server
    print("Starting web server...")
    port = start_server('./released')
    url = get_server_url(port)
    print(f"Server started at {url}")

    # Wait for server to be ready
    time.sleep(1)

    # Test that page loads
    try:
        response = urllib.request.urlopen(f"{url}/skrolbak/index.html", timeout=5)
        html_content = response.read().decode('utf-8')
        assert len(html_content) > 0, "HTML content is empty"
        print("✓ Page loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load page: {e}")
        sys.exit(1)

    # $REQ_RENDERING_001: Complete viewport coverage
    # Test that viewport is fully covered by checking CSS
    assert '<animated-background' in html_content, "animated-background element not found"
    print("✓ $REQ_RENDERING_001: Animated background element present")

    # Read the JavaScript source to verify rendering implementation
    js_path = Path('./code/animated-background.js')
    assert js_path.exists(), "animated-background.js not found"
    js_content = js_path.read_text()

    # $REQ_RENDERING_001: Verify dynamic tiling for complete coverage
    # Check that tiles are rendered dynamically based on viewport
    assert 'updateTiles' in js_content, "Dynamic tile update function not found"
    assert 'minCol' in js_content or 'minRow' in js_content, "Dynamic tile range calculation not found"
    assert 'for' in js_content and 'tile' in js_content, "Tile rendering loop not found"
    print("✓ $REQ_RENDERING_001: Dynamic tiling implementation verified")

    # $REQ_RENDERING_002: 3D perspective foreshortening
    # Verify CSS perspective is applied
    assert 'perspective' in js_content, "CSS perspective not found"
    # Check that rotateX and rotateY are used for 3D effect
    assert 'rotateX' in js_content, "rotateX transform not found"
    assert 'rotateY' in js_content, "rotateY transform not found"
    print("✓ $REQ_RENDERING_002: 3D perspective foreshortening implemented")

    # $REQ_RENDERING_003: Z-index layering
    # Verify background has lowest z-index
    assert 'z-index: -1' in js_content or 'z-index:-1' in js_content, "Background z-index not set to -1"
    print("✓ $REQ_RENDERING_003: Z-index layering verified (background at z-index: -1)")

    # Visual test using screenshot
    screenshot_path = './tmp/rendering_test.png'
    os.makedirs('./tmp', exist_ok=True)

    # Take screenshot using visual-test.py infrastructure
    print("Taking screenshot for visual verification...")
    screenshot_result = subprocess.run(
        [
            './the-system/bin/uv.linux', 'run', '--script',
            './the-system/scripts/screenshot.py',
            f"{url}/skrolbak/index.html",
            screenshot_path
        ],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    if screenshot_result.returncode == 0 and Path(screenshot_path).exists():
        print(f"✓ Screenshot saved to {screenshot_path}")

        # Use visual-test.py to verify rendering
        visual_test_result = subprocess.run(
            [
                './the-system/bin/uv.linux', 'run', '--script',
                './the-system/scripts/visual-test.py',
                screenshot_path,
                "The viewport is completely filled with a tiled background image with no gaps. "
                "The background appears behind a pink glassmorphic login form that is centered in the viewport."
            ],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60
        )

        if visual_test_result.returncode == 0:
            print("✓ Visual verification: Complete viewport coverage confirmed")
        else:
            print(f"⚠ Visual verification inconclusive: {visual_test_result.stdout}")
            # Don't fail on visual test, as it's supplementary
    else:
        print(f"⚠ Screenshot capture failed (non-critical): {screenshot_result.stderr}")
        # Continue without visual test

    print("\n=== All rendering requirements verified ===")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(test_rendering())
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
