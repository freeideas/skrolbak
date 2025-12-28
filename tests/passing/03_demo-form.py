#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "playwright",
#     "pillow",
# ]
# ///

"""Test demo form overlay on animated background."""

import atexit
import os
import subprocess
import sys
import time
from pathlib import Path

# Add the-system/scripts to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'the-system' / 'scripts'))

from websrvr import start_server, get_server_url, stop_server

# Ensure cleanup
atexit.register(stop_server)

def main():
    # Start web server
    port = start_server('./released/skrolbak')
    url = get_server_url(port)

    # Install playwright browsers if needed
    try:
        subprocess.run(
            [sys.executable, '-m', 'playwright', 'install', 'chromium'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=120
        )
    except Exception as e:
        print(f"Warning: Could not install playwright browsers: {e}")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load the page
        page.goto(url, wait_until='networkidle')
        time.sleep(2)  # Allow animation to start

        # $REQ_DEMO-FORM_001: Centered Position
        form_container = page.locator('.form-container')
        assert form_container.count() > 0, "Form container not found"

        # Get form position
        form_box = form_container.bounding_box()
        assert form_box is not None, "Could not get form bounding box"

        # Get viewport size
        viewport = page.viewport_size
        viewport_center_x = viewport['width'] / 2
        viewport_center_y = viewport['height'] / 2

        # Check if form is centered (within 10px tolerance)
        form_center_x = form_box['x'] + form_box['width'] / 2
        form_center_y = form_box['y'] + form_box['height'] / 2

        assert abs(form_center_x - viewport_center_x) < 10, \
            f"Form not centered horizontally: {form_center_x} vs {viewport_center_x}"
        assert abs(form_center_y - viewport_center_y) < 10, \
            f"Form not centered vertically: {form_center_y} vs {viewport_center_y}"

        # $REQ_DEMO-FORM_002: Glassmorphic Styling
        form = page.locator('.glassmorphic-form')
        assert form.count() > 0, "Glassmorphic form not found"

        # Check styling
        bg_color = form.evaluate('el => getComputedStyle(el).backgroundColor')
        backdrop_filter = form.evaluate('el => getComputedStyle(el).backdropFilter || getComputedStyle(el).webkitBackdropFilter')

        # Check hot-pink with 50% opacity (rgba(255, 105, 180, 0.5))
        assert 'rgba(255, 105, 180, 0.5)' in bg_color or 'rgba(255,105,180,0.5)' in bg_color.replace(' ', ''), \
            f"Form background not hot-pink 50% opaque: {bg_color}"

        # Check blur effect
        assert 'blur' in backdrop_filter.lower(), \
            f"Form does not have backdrop blur: {backdrop_filter}"

        # $REQ_DEMO-FORM_003: Form Elements
        # Check for heading
        heading = form.locator('h2')
        assert heading.count() > 0, "Form heading not found"

        # Check for input field
        text_input = form.locator('input[type="text"], input[type="password"]')
        assert text_input.count() > 0, "Form input field not found"

        # Check for checkbox
        checkbox = form.locator('input[type="checkbox"]')
        assert checkbox.count() > 0, "Form checkbox not found"

        # Check for button
        button = form.locator('button, input[type="submit"]')
        assert button.count() > 0, "Form button not found"

        # $REQ_DEMO-FORM_004: Background Visible Through Form
        # Check that animated-background element exists
        bg_element = page.locator('animated-background')
        assert bg_element.count() > 0, "Animated background not found"

        # Verify background is visible (has dimensions)
        bg_box = bg_element.bounding_box()
        assert bg_box is not None, "Background has no bounding box"
        assert bg_box['width'] > 0 and bg_box['height'] > 0, \
            "Background has zero dimensions"

        # $REQ_DEMO-FORM_005: Z-Index Layering
        # Check z-index of form vs background
        form_z = form_container.evaluate('el => getComputedStyle(el).zIndex')
        bg_z = bg_element.evaluate('el => getComputedStyle(el).zIndex')

        form_z_num = int(form_z) if form_z and form_z != 'auto' else 0
        bg_z_num = int(bg_z) if bg_z and bg_z != 'auto' else 0

        assert form_z_num > bg_z_num, \
            f"Form z-index ({form_z_num}) not greater than background z-index ({bg_z_num})"

        # $REQ_DEMO-FORM_006: Blur Effect With Moving Background
        # Verify backdrop-filter is applied (already checked above in styling)
        # The blur effect working with moving background is verified by:
        # 1. backdrop-filter being present (checked above)
        # 2. Background element existing and being visible (checked above)
        # 3. Form being semi-transparent (checked above)
        # Therefore this requirement is satisfied by previous checks

        # $REQ_DEMO-FORM_007: Form Remains Stationary
        # Record initial form position
        initial_pos = form_container.bounding_box()

        # Wait for animation
        time.sleep(2)

        # Check form position hasn't changed
        final_pos = form_container.bounding_box()

        assert abs(initial_pos['x'] - final_pos['x']) < 1, \
            f"Form moved horizontally: {initial_pos['x']} -> {final_pos['x']}"
        assert abs(initial_pos['y'] - final_pos['y']) < 1, \
            f"Form moved vertically: {initial_pos['y']} -> {final_pos['y']}"

        # $REQ_DEMO-FORM_008: Display Only
        # Check that form does not submit anywhere
        # The .glassmorphic-form class IS on the <form> element itself
        form_action = form.evaluate('el => el.hasAttribute("action") ? el.getAttribute("action") : null')
        form_onsubmit = form.evaluate('el => el.hasAttribute("onsubmit")')

        # Check button type
        submit_btn = form.locator('button[type="submit"], input[type="submit"]')

        # Form should either have no submit button, or have no action and no onsubmit handler
        has_submit_btn = submit_btn.count() > 0
        has_action = form_action is not None and form_action not in ['', '#']

        assert not (has_submit_btn and has_action), \
            f"Form has submit button and action: {form_action}"
        assert not form_onsubmit, \
            "Form has onsubmit handler"

        browser.close()

    print("✓ All demo form tests passed")

if __name__ == '__main__':
    main()
