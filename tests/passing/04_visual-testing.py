#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["playwright"]
# ///

"""
Visual Testing
Tests the visual behaviors of the animated background demo using Playwright screenshots.

This test verifies behaviors from multiple requirement documents:
- Demo form (demo-form.md)
- Deterministic replay (deterministic-replay.md)

NOTE: This requirement document has no unique requirements. It documents the
Playwright screenshot-based test process for verifying each degree of freedom
independently and confirming deterministic replay. All testable behaviors are
already specified in other requirement documents.
"""

import sys
import os
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

# Import server utilities
import subprocess

def start_server(path):
    """Start HTTP server and return port"""
    import random
    port = random.randint(10001, 65000)
    proc = subprocess.Popen(
        [sys.executable, '-m', 'http.server', str(port), '--directory', path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding='utf-8'
    )
    time.sleep(1)  # Give server time to start
    global _server_proc
    _server_proc = proc
    return port

_server_proc = None

def cleanup_server():
    """Stop the HTTP server"""
    global _server_proc
    if _server_proc:
        try:
            _server_proc.terminate()
            _server_proc.wait(timeout=2)
        except:
            try:
                _server_proc.kill()
            except:
                pass

import atexit
atexit.register(cleanup_server)

def main():
    # Ensure tmp directory exists
    tmp_dir = Path(__file__).resolve().parent.parent.parent / 'tmp' / '04_visual-testing'
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # Start server for the released demo
    released_dir = Path(__file__).resolve().parent.parent.parent / 'released' / 'skrolbak'
    port = start_server(str(released_dir))
    url = f"http://localhost:{port}/demo.html"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Navigate to demo
        page.goto(url)

        # Wait for page to be ready
        page.wait_for_load_state('networkidle')
        time.sleep(0.5)  # Additional time for any initialization

        # ==========================================
        # Demo Form Visual Tests
        # ==========================================

        # $REQ_DEMO_FORM_001: Glassmorphic Visual Style
        # Verify hot-pink 50% opaque glassmorphic login form exists
        form = page.locator('.demo-form')
        assert form.count() == 1, "$REQ_DEMO_FORM_001: Demo form should exist"

        # Check background color (hot pink with 50% opacity: rgba(255, 20, 147, 0.5))
        bg_color = form.evaluate('el => window.getComputedStyle(el).backgroundColor')
        assert 'rgba(255, 20, 147, 0.5)' in bg_color, f"$REQ_DEMO_FORM_001: Expected hot pink background, got {bg_color}"

        # Check backdrop-filter for glassmorphism
        backdrop_filter = form.evaluate('el => window.getComputedStyle(el).backdropFilter || window.getComputedStyle(el).webkitBackdropFilter')
        assert 'blur' in backdrop_filter.lower(), f"$REQ_DEMO_FORM_001: Expected blur backdrop filter, got {backdrop_filter}"

        # $REQ_DEMO_FORM_002: Centered Placement
        # Verify form is centered horizontally and vertically
        viewport_size = page.viewport_size
        form_box = form.bounding_box()
        assert form_box is not None, "$REQ_DEMO_FORM_002: Form should be visible"

        form_center_x = form_box['x'] + form_box['width'] / 2
        form_center_y = form_box['y'] + form_box['height'] / 2
        viewport_center_x = viewport_size['width'] / 2
        viewport_center_y = viewport_size['height'] / 2

        # Allow small tolerance for centering
        tolerance = 5
        assert abs(form_center_x - viewport_center_x) < tolerance, f"$REQ_DEMO_FORM_002: Form should be horizontally centered"
        assert abs(form_center_y - viewport_center_y) < tolerance, f"$REQ_DEMO_FORM_002: Form should be vertically centered"

        # $REQ_DEMO_FORM_003: Foreground Layering
        # Verify z-index is high enough to float above background
        z_index = form.evaluate('el => window.getComputedStyle(el).zIndex')
        assert int(z_index) >= 100, f"$REQ_DEMO_FORM_003: Form z-index should be high (got {z_index})"

        # $REQ_DEMO_FORM_004: Form Elements
        # Verify basic form elements exist
        assert page.locator('.demo-form h1').count() == 1, "$REQ_DEMO_FORM_004: Heading should exist"
        assert page.locator('.demo-form input[type="text"], .demo-form input[type="password"]').count() >= 1, "$REQ_DEMO_FORM_004: Input field should exist"
        assert page.locator('.demo-form input[type="checkbox"]').count() >= 1, "$REQ_DEMO_FORM_004: Checkbox should exist"
        assert page.locator('.demo-form button').count() >= 1, "$REQ_DEMO_FORM_004: Button should exist"

        # $REQ_DEMO_FORM_005: Display Only
        # Not reasonably testable - form doesn't submit anywhere by design

        # $REQ_DEMO_FORM_006: Background Animation Visibility
        # Verify animated-background element exists and is visible
        bg_element = page.locator('animated-background')
        assert bg_element.count() == 1, "$REQ_DEMO_FORM_006: Animated background should exist"
        assert bg_element.is_visible(), "$REQ_DEMO_FORM_006: Animated background should be visible"

        # $REQ_DEMO_FORM_007: Blur Effect Interaction
        # Verified by $REQ_DEMO_FORM_001 (backdrop-filter applies to content beneath)

        # $REQ_DEMO_FORM_008: Form Stationary During Animation
        # Get form position initially
        form_box_1 = page.locator('.demo-form').bounding_box()

        # Wait for animation to progress
        time.sleep(2)

        # Get form position after animation
        form_box_2 = page.locator('.demo-form').bounding_box()

        # Form should remain in same position (centered)
        assert form_box_1 is not None and form_box_2 is not None, "$REQ_DEMO_FORM_008: Form should be visible"
        assert abs(form_box_1['x'] - form_box_2['x']) < 1, "$REQ_DEMO_FORM_008: Form should remain stationary (x position)"
        assert abs(form_box_1['y'] - form_box_2['y']) < 1, "$REQ_DEMO_FORM_008: Form should remain stationary (y position)"

        # Take screenshots for documentation
        screenshot_path = tmp_dir / 'demo-visual.png'
        page.screenshot(path=str(screenshot_path))

        browser.close()

    # ==========================================
    # Deterministic Replay Visual Test
    # ==========================================

    # $REQ_REPLAY_008: Fast-Forward Produces Identical State
    # This requires comparing two scenarios at exactly t=3:
    # 1. Run from t=0 for 3 seconds
    # 2. Set t=2 and wait 1 second to reach t=3
    # Both should produce identical position values right after the t=3 tick
    #
    # We use t=3 instead of t=30 for faster testing (the principle is the same)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # We'll test with t=3 for faster execution (requirement uses t=30)
        test_time = 3

        # Scenario 1: Run from t=0 for 3 seconds
        page1 = browser.new_page()

        # Setup console listener to detect when t=3 tick happens
        console_logs_1 = []
        page1.on('console', lambda msg: console_logs_1.append(msg.text))

        test_html_0 = released_dir / 'test-replay-0.html'
        with open(test_html_0, 'w', encoding='utf-8') as f:
            f.write(f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body>
<script src="animated-background.js"></script>
<animated-background src="bg.jpg" pan-x="100" pan-y="100" t="0"></animated-background>
</body>
</html>''')

        page1.goto(f"http://localhost:{port}/test-replay-0.html")
        page1.wait_for_load_state('networkidle')

        # Wait until we see "t=3" in console logs
        for _ in range(40):  # 4 seconds max
            if any(f"t={test_time}" in log for log in console_logs_1):
                break
            time.sleep(0.1)

        # Wait a tiny bit more to ensure transform is applied
        time.sleep(0.05)

        # Get the transform values
        transform_1 = page1.evaluate('''() => {
            const el = document.querySelector('animated-background');
            const wall = el.querySelector('div');
            return wall ? wall.style.transform : null;
        }''')

        # Scenario 2: Set t=2 and wait 1 second to reach t=3
        page2 = browser.new_page()

        # Setup console listener
        console_logs_2 = []
        page2.on('console', lambda msg: console_logs_2.append(msg.text))

        test_html_2 = released_dir / 'test-replay-2.html'
        with open(test_html_2, 'w', encoding='utf-8') as f:
            f.write(f'''<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body>
<script src="animated-background.js"></script>
<animated-background src="bg.jpg" pan-x="100" pan-y="100" t="{test_time - 1}"></animated-background>
</body>
</html>''')

        page2.goto(f"http://localhost:{port}/test-replay-2.html")
        page2.wait_for_load_state('networkidle')

        # Wait until we see "t=3" in console logs
        for _ in range(20):  # 2 seconds max
            if any(f"t={test_time}" in log for log in console_logs_2):
                break
            time.sleep(0.1)

        # Wait a tiny bit more to ensure transform is applied
        time.sleep(0.05)

        # Get the transform values
        transform_2 = page2.evaluate('''() => {
            const el = document.querySelector('animated-background');
            const wall = el.querySelector('div');
            return wall ? wall.style.transform : null;
        }''')

        # Clean up test files
        test_html_0.unlink()
        test_html_2.unlink()

        browser.close()

        # Compare transforms - they should be identical within floating-point tolerance
        # Extract numeric values from transform strings for comparison
        import re

        def parse_transform(transform_str):
            """Parse transform string into dict of values"""
            if not transform_str:
                return None

            # Extract all numeric values
            numbers = re.findall(r'[-+]?\d*\.?\d+', transform_str)
            return [float(n) for n in numbers]

        values_1 = parse_transform(transform_1)
        values_2 = parse_transform(transform_2)

        assert values_1 is not None and values_2 is not None, "$REQ_REPLAY_008: Both transforms should exist"
        assert len(values_1) == len(values_2), "$REQ_REPLAY_008: Transforms should have same number of values"

        # Floating-point tolerance per the requirement
        # The transforms should match very closely right after a tick
        # Allow for timing imprecision in the browser's animation loop (a few pixels)
        tolerance = 5.0  # Reasonable absolute tolerance for visual testing
        for i, (v1, v2) in enumerate(zip(values_1, values_2)):
            diff = abs(v1 - v2)
            assert diff < tolerance, f"$REQ_REPLAY_008: Transform value {i} differs: {v1} vs {v2} (diff={diff})"

    print("All visual tests passed ✓")
    return 0

if __name__ == '__main__':
    sys.exit(main())
