#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "playwright>=1.40.0",
#     "Pillow>=10.0.0",
#     "numpy>=1.24.0",
# ]
# ///
"""
Visual testing for login form with animated background.
Tests $REQ_VT_001, $REQ_VT_002, and $REQ_VT_003.
"""

import sys
import subprocess
import time
import atexit
from pathlib import Path

# Assume CWD is project root
PROJECT_ROOT = Path.cwd()
RELEASED_DIR = PROJECT_ROOT / "released"
BUILD_SCRIPT = PROJECT_ROOT / "code" / "build.py"
UV_BIN = PROJECT_ROOT / "the-system" / "bin" / "uv.linux"
VISUAL_TEST_SCRIPT = PROJECT_ROOT / "the-system" / "scripts" / "visual-test.py"
TMP_DIR = PROJECT_ROOT / "tmp"

# Import websrvr functions
sys.path.insert(0, str(PROJECT_ROOT / "the-system" / "scripts"))
from websrvr import start_server, get_server_url, stop_server

# Ensure tmp directory exists
TMP_DIR.mkdir(exist_ok=True)

# Track subprocesses for cleanup
_procs = []

def cleanup():
    """Clean up any running processes."""
    for p in _procs:
        try:
            p.terminate()
            p.wait(timeout=2)
        except:
            pass
    stop_server()

atexit.register(cleanup)


def run_build():
    """Build the app if needed."""
    if not RELEASED_DIR.exists() or not list(RELEASED_DIR.iterdir()):
        print("\n• Running build process...")
        result = subprocess.run(
            [str(UV_BIN), "run", "--script", str(BUILD_SCRIPT)],
            cwd=PROJECT_ROOT,
            text=True,
            encoding='utf-8',
            capture_output=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode != 0:
            print(f"✗ Build failed with exit code {result.returncode}", file=sys.stderr)
            sys.exit(97)  # Build failed


def install_playwright():
    """Install Playwright browsers if needed."""
    print("\n• Installing Playwright browsers...")
    result = subprocess.run(
        ["playwright", "install", "chromium"],
        text=True,
        encoding='utf-8',
        capture_output=True
    )
    if result.returncode != 0:
        print(f"Warning: Playwright install returned {result.returncode}")
        print(result.stdout)
        print(result.stderr, file=sys.stderr)


def take_screenshot(page, filename):
    """Take a screenshot and save to tmp directory."""
    screenshot_path = TMP_DIR / filename
    page.screenshot(path=str(screenshot_path))
    print(f"  • Screenshot saved: {screenshot_path}")
    return screenshot_path


def verify_visual(screenshot_path, description, req_id):
    """Use visual-test.py to verify screenshot matches description."""
    print(f"\n• Verifying {req_id}: {description[:60]}...")
    result = subprocess.run(
        [str(UV_BIN), "run", "--script", str(VISUAL_TEST_SCRIPT), str(screenshot_path), description],
        text=True,
        encoding='utf-8',
        capture_output=True
    )

    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    if result.returncode == 0:
        print(f"  ✓ Visual verification passed")
        return True
    elif result.returncode == 1:
        print(f"  ✗ Visual verification failed: image does not match description")
        return False
    else:
        print(f"  ✗ Visual verification error (exit code {result.returncode})")
        return False


def main():
    print("Testing visual requirements...")

    # Build if needed
    run_build()

    # Install Playwright browsers
    install_playwright()

    # Start web server
    print("\n• Starting web server...")
    port = start_server(str(RELEASED_DIR))
    url = get_server_url(port)
    print(f"  • Server running at {url}")

    # Import Playwright after installation
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("✗ Playwright not available", file=sys.stderr)
        sys.exit(99)

    # Run Playwright tests
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        # Navigate to the app
        print(f"\n• Loading app at {url}...")
        page.goto(url, wait_until='networkidle')

        # Wait for Flutter to initialize and render
        print("  • Waiting for Flutter to initialize...")
        time.sleep(5)  # Give Flutter more time to fully render

        # $REQ_VT_001: Form Visibility Verification
        print("\n• Testing $REQ_VT_001: Form Visibility...")
        screenshot1 = take_screenshot(page, "form_visibility.png")

        description1 = (
            "The image shows a login form with glassmorphic styling that is visible and centered. "
            "The form includes a 'Login' title at the top, an email input field, "
            "a 'Stay logged in' checkbox, and a 'Continue' button. "
            "The form appears semi-transparent with a blurred background visible through it."
        )

        assert verify_visual(screenshot1, description1, "$REQ_VT_001"), \
            "Form visibility verification failed"  # $REQ_VT_001

        # $REQ_VT_002: Background Coverage Verification
        print("\n• Testing $REQ_VT_002: Background Coverage...")
        screenshot2 = take_screenshot(page, "background_coverage.png")

        description2 = (
            "The image shows a tiled background image that completely covers the entire viewport. "
            "There are no gaps, seams, white spaces, or uncovered areas visible anywhere in the background. "
            "The background is fully covered from edge to edge with a seamlessly tiled pattern."
        )

        assert verify_visual(screenshot2, description2, "$REQ_VT_002"), \
            "Background coverage verification failed"  # $REQ_VT_002

        # $REQ_VT_003: Background Animation Verification
        print("\n• Testing $REQ_VT_003: Background Animation...")
        print("  • Taking first screenshot...")
        screenshot3a = take_screenshot(page, "animation_before.png")

        print("  • Waiting 5 seconds...")
        time.sleep(5)

        print("  • Taking second screenshot...")
        screenshot3b = take_screenshot(page, "animation_after.png")

        # Compare both screenshots using pixel analysis
        print("\n  • Comparing screenshots for background movement...")

        # Simple pixel comparison to verify background has changed
        from PIL import Image
        import numpy as np

        img1 = Image.open(screenshot3a)
        img2 = Image.open(screenshot3b)

        arr1 = np.array(img1)
        arr2 = np.array(img2)

        # Check that images have differences (background moved)
        diff = np.abs(arr1.astype(int) - arr2.astype(int))
        total_diff = np.sum(diff)

        # Images should be different due to background animation
        assert total_diff > 0, \
            "Background animation verification failed - screenshots are identical"  # $REQ_VT_003

        # Calculate percentage of pixels that changed significantly (threshold of 30 per channel)
        significant_changes = np.sum(np.any(diff > 30, axis=2))
        total_pixels = arr1.shape[0] * arr1.shape[1]
        change_percentage = (significant_changes / total_pixels) * 100

        print(f"  • {change_percentage:.1f}% of pixels changed significantly")

        # Should have noticeable changes (at least some background movement)
        assert change_percentage > 1, \
            f"Background animation verification failed - only {change_percentage:.1f}% of pixels changed (expected > 1%)"  # $REQ_VT_003

        # Verify the login form remained stationary
        print("\n  • Verifying form remained stationary...")
        description3 = (
            "This composite image shows two screenshots side by side taken 5 seconds apart. "
            "In both the left and right screenshots, there is a centered login form with a 'Login' title "
            "and a pink 'Continue' button that appears in exactly the same position. "
            "The login form itself has not moved, shifted, or changed position between the two screenshots, "
            "even though the background pattern behind it may have shifted."
        )

        # Use visual-test.py to verify form stayed in same position by checking both screenshots
        # We'll create a simple composite image showing both screenshots side-by-side
        composite_path = TMP_DIR / "animation_composite.png"
        composite = Image.new('RGB', (img1.width * 2, img1.height))
        composite.paste(img1, (0, 0))
        composite.paste(img2, (img1.width, 0))
        composite.save(composite_path)

        assert verify_visual(composite_path, description3, "$REQ_VT_003"), \
            "Form position verification failed - form did not remain stationary"  # $REQ_VT_003

        print("  ✓ Background animation verified (background shifted while form remained stationary)")

        # Close browser
        browser.close()

    print("\n✓ All visual testing requirements verified!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
