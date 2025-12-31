#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["playwright"]
# ///

"""
Test for demo form requirements (reqs/04_demo-form.md)
"""

import sys
import subprocess
import time
import atexit
from pathlib import Path

# Ensure we're running from project root
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / 'the-system' / 'scripts'))

from websrvr import start_server, get_server_url, stop_server

# Install playwright browsers if needed (one-time setup)
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Installing Playwright...")
    subprocess.run([
        str(project_root / 'the-system' / 'bin' / 'uv.linux'),
        'pip', 'install', 'playwright'
    ], check=True, encoding='utf-8')
    from playwright.sync_api import sync_playwright

def ensure_playwright_browsers():
    """Ensure Playwright browsers are installed"""
    try:
        # Check if browsers are installed by trying to launch
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
    except Exception:
        # Install browsers
        print("Installing Playwright browsers (one-time setup)...")
        subprocess.run([
            str(project_root / 'the-system' / 'bin' / 'uv.linux'),
            'run', 'playwright', 'install', 'chromium'
        ], check=True, encoding='utf-8')

def test_demo_form():
    """Test all demo form requirements"""

    # Start web server
    port = start_server(str(project_root / 'released' / 'skrolbak'))
    url = get_server_url(port)
    demo_url = f"{url}/demo.html"

    print(f"Testing demo form at {demo_url}")

    # Ensure Playwright browsers are installed
    ensure_playwright_browsers()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            # Load the demo page
            page.goto(demo_url)
            page.wait_for_load_state('networkidle')

            # Wait for animated-background component to be defined
            page.wait_for_function("customElements.get('animated-background') !== undefined")

            # Wait a bit for initial render
            time.sleep(0.5)

            # Find the demo form
            form = page.locator('.demo-form')
            assert form.count() == 1, "Demo form not found"

            # $REQ_DEMO_FORM_004: Form Elements
            # Check for heading
            heading = form.locator('h1')
            assert heading.count() == 1, "Form heading not found"
            assert heading.text_content().strip() != "", "Form heading is empty"

            # Check for input field
            username_input = form.locator('input[type="text"]')
            assert username_input.count() >= 1, "Text input field not found"

            # Check for checkbox
            checkbox = form.locator('input[type="checkbox"]')
            assert checkbox.count() >= 1, "Checkbox not found"

            # Check for button
            button = form.locator('button')
            assert button.count() >= 1, "Button not found"

            # $REQ_DEMO_FORM_002: Centered Placement
            # Check that form is centered
            form_box = form.bounding_box()
            assert form_box is not None, "Could not get form bounding box"

            viewport_size = page.viewport_size
            form_center_x = form_box['x'] + form_box['width'] / 2
            form_center_y = form_box['y'] + form_box['height'] / 2
            viewport_center_x = viewport_size['width'] / 2
            viewport_center_y = viewport_size['height'] / 2

            # Allow 10px tolerance for centering
            assert abs(form_center_x - viewport_center_x) < 10, \
                f"Form not centered horizontally: {form_center_x} vs {viewport_center_x}"
            assert abs(form_center_y - viewport_center_y) < 10, \
                f"Form not centered vertically: {form_center_y} vs {viewport_center_y}"

            # $REQ_DEMO_FORM_001: Glassmorphic Visual Style
            # Check for glassmorphic styling properties
            styles = page.evaluate("""() => {
                const form = document.querySelector('.demo-form');
                const computed = window.getComputedStyle(form);
                return {
                    backgroundColor: computed.backgroundColor,
                    backdropFilter: computed.backdropFilter || computed.webkitBackdropFilter,
                    borderRadius: computed.borderRadius,
                };
            }""")

            # Check for semi-transparent background (hot pink with opacity)
            bg_color = styles['backgroundColor']
            assert 'rgba' in bg_color, f"Background should be semi-transparent (rgba): {bg_color}"

            # Parse rgba values
            rgba_parts = bg_color.replace('rgba(', '').replace(')', '').split(',')
            assert len(rgba_parts) == 4, "Invalid rgba format"
            alpha = float(rgba_parts[3].strip())
            assert 0.4 <= alpha <= 0.6, f"Opacity should be around 50%: {alpha}"

            # Check for pink/hot-pink color (high red component)
            red = int(rgba_parts[0].strip())
            assert red > 200, f"Should have high red component for hot pink: {red}"

            # Check for backdrop blur effect
            backdrop_filter = styles['backdropFilter']
            assert 'blur' in backdrop_filter, f"Backdrop filter should include blur: {backdrop_filter}"

            # Check for border radius (glassmorphic design)
            border_radius = styles['borderRadius']
            assert border_radius != '0px', "Form should have rounded corners"

            # $REQ_DEMO_FORM_003: Foreground Layering
            # Check z-index to ensure form is above background
            z_index = page.evaluate("""() => {
                const form = document.querySelector('.demo-form');
                const computed = window.getComputedStyle(form);
                return parseInt(computed.zIndex) || 0;
            }""")
            assert z_index > 0, f"Form should have positive z-index to be above background: {z_index}"

            # $REQ_DEMO_FORM_005: Display Only
            # Verify form has onsubmit="return false" or similar to prevent submission
            form_element = page.locator('form')
            if form_element.count() > 0:
                onsubmit = page.evaluate("""() => {
                    const form = document.querySelector('form');
                    return form ? form.getAttribute('onsubmit') : null;
                }""")
                # Form should either prevent default or return false
                assert onsubmit is not None and 'false' in onsubmit.lower(), \
                    "Form should have onsubmit handler that returns false"

            # $REQ_DEMO_FORM_006: Background Animation Visibility
            # Verify background element exists and is visible
            # The semi-transparent form should allow the background to show through
            bg_element = page.locator('animated-background')
            assert bg_element.count() == 1, "Animated background element not found"

            # Check that background has rendered content (the wall element)
            has_wall = page.evaluate("""() => {
                const bg = document.querySelector('animated-background');
                if (!bg) return false;
                // Check if wall div exists as direct child
                const wall = bg.querySelector('div');
                return wall !== null;
            }""")
            assert has_wall, "Background element has no rendered content (wall div)"

            # Verify the form is semi-transparent (allowing background to show)
            # Already verified in $REQ_DEMO_FORM_001 with alpha check

            # $REQ_DEMO_FORM_007: Blur Effect Interaction
            # Verify backdrop-filter is applied (blur interacts with background)
            has_backdrop_filter = page.evaluate("""() => {
                const form = document.querySelector('.demo-form');
                const computed = window.getComputedStyle(form);
                const filter = computed.backdropFilter || computed.webkitBackdropFilter;
                return filter && filter !== 'none' && filter.includes('blur');
            }""")
            assert has_backdrop_filter, "Backdrop filter with blur not applied to form"

            # $REQ_DEMO_FORM_008: Form Stationary During Animation
            # Record initial form position
            initial_position = form.bounding_box()
            assert initial_position is not None, "Could not get initial form position"

            # Wait for animation to occur (2 seconds)
            time.sleep(2)

            # Check form position again
            final_position = form.bounding_box()
            assert final_position is not None, "Could not get final form position"

            # Form should remain in the same position (allow 1px tolerance for rounding)
            assert abs(initial_position['x'] - final_position['x']) < 1, \
                f"Form moved horizontally: {initial_position['x']} -> {final_position['x']}"
            assert abs(initial_position['y'] - final_position['y']) < 1, \
                f"Form moved vertically: {initial_position['y']} -> {final_position['y']}"

            # Verify background is animating by checking that the component exists and has range attributes
            bg_is_configured = page.evaluate("""() => {
                const bg = document.querySelector('animated-background');
                if (!bg) return false;
                // Check if any range attributes are set (indicating animation is configured)
                const panX = bg.getAttribute('pan-x');
                const panY = bg.getAttribute('pan-y');
                const panZ = bg.getAttribute('pan-z');
                const rotX = bg.getAttribute('rot-x');
                const rotY = bg.getAttribute('rot-y');
                const rotZ = bg.getAttribute('rot-z');
                return (panX || panY || panZ || rotX || rotY || rotZ);
            }""")
            assert bg_is_configured, "Background should have animation ranges configured"

            print("✓ All demo form requirements passed")

        finally:
            browser.close()
            stop_server()

if __name__ == '__main__':
    try:
        test_demo_form()
        sys.exit(0)
    except AssertionError as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"✗ Test error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
