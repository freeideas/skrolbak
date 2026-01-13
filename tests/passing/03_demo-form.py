#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["playwright"]
# ///

"""
Test for demo form requirements.
Tests the glassmorphic login form overlay, email validation, and success panel transition.
"""

import sys
import subprocess
from pathlib import Path

# Import server utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'ai-coder' / 'scripts'))
from websrvr import start_server, get_server_url, stop_server

def main():
    # Start web server
    port = start_server('./released')
    url = get_server_url(port)

    print(f"Testing demo form at {url}")

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)

            # Wait for page to load
            page.wait_for_load_state('networkidle')

            # $REQ_DEMO_FORM_001: Form Visual Design
            # Verify form container exists and is visible
            form_container = page.locator('#loginForm')
            assert form_container.is_visible(), "Form should be visible"

            # Verify form is centered
            # Since styles are in a stylesheet, we need to check the computed styles
            # The requirement is that form is centered horizontally and vertically
            form_style = form_container.evaluate('el => window.getComputedStyle(el)')

            # Verify positioning properties that achieve centering
            assert form_style.get('position') == 'fixed', "Form should have fixed position"

            # Check that the form is visually centered by verifying its bounding box
            form_box = form_container.bounding_box()
            viewport_size = page.viewport_size
            # Form should be roughly centered (within 50px tolerance due to transform)
            form_center_x = form_box['x'] + form_box['width'] / 2
            form_center_y = form_box['y'] + form_box['height'] / 2
            viewport_center_x = viewport_size['width'] / 2
            viewport_center_y = viewport_size['height'] / 2
            assert abs(form_center_x - viewport_center_x) < 5, f"Form should be centered horizontally (form center: {form_center_x}, viewport center: {viewport_center_x})"
            assert abs(form_center_y - viewport_center_y) < 5, f"Form should be centered vertically (form center: {form_center_y}, viewport center: {viewport_center_y})"

            # Verify glassmorphic styling (hot pink with opacity, backdrop blur)
            background = form_style.get('backgroundColor', '')
            assert 'rgba(255, 20, 147, 0.5)' in background or 'rgba(255, 20, 147, 0.498)' in background, f"Form should have hot-pink 50% opacity background, got {background}"

            backdrop_filter = form_style.get('backdropFilter', '') or form_style.get('-webkit-backdrop-filter', '')
            assert 'blur' in backdrop_filter.lower(), f"Form should have backdrop blur effect, got {backdrop_filter}"

            # $REQ_DEMO_FORM_002: Form Contents
            # Verify form contains required elements
            heading = form_container.locator('h1')
            assert heading.is_visible(), "Form should have a heading"

            email_input = form_container.locator('input[type="email"]')
            assert email_input.is_visible(), "Form should have an email input field"

            checkbox = form_container.locator('input[type="checkbox"]')
            assert checkbox.is_visible(), "Form should have a checkbox"

            submit_button = form_container.locator('button')
            assert submit_button.is_visible(), "Form should have a submit button"

            # $REQ_DEMO_FORM_003: Email Validation on Submit
            # $REQ_DEMO_FORM_004: Invalid Email Error Display
            # Test invalid email (no @ character)
            email_input.fill('invalidemail')
            submit_button.click()
            page.wait_for_timeout(100)  # Brief wait for validation

            error_message = page.locator('#errorMessage')
            error_text = error_message.text_content()
            assert error_text and error_text.strip() != '', "Error message should be shown for invalid email"
            assert form_container.is_visible(), "Form should still be visible after invalid email"

            # Verify error message is positioned below the input field
            email_box = email_input.bounding_box()
            error_box = error_message.bounding_box()
            assert error_box['y'] > email_box['y'] + email_box['height'], f"Error message should be below the input field (error y: {error_box['y']}, input bottom: {email_box['y'] + email_box['height']})"

            # $REQ_DEMO_FORM_005: Valid Email Transition to Success Panel
            # Test valid email (contains @ character)
            email_input.fill('test@example.com')
            submit_button.click()
            page.wait_for_timeout(200)  # Wait for transition

            # Form should be hidden
            assert not form_container.is_visible(), "Form should be hidden after valid email submission"

            # Success panel should be shown
            success_panel = page.locator('#successPanel')
            assert success_panel.is_visible(), "Success panel should be visible after valid email submission"

            # $REQ_DEMO_FORM_006: Success Panel Visual Design
            # Verify success panel has same styling as form
            success_style = success_panel.evaluate('el => window.getComputedStyle(el)')

            # Same size
            form_width = form_style.get('width', '')
            success_width = success_style.get('width', '')
            assert form_width == success_width, f"Success panel width ({success_width}) should match form width ({form_width})"

            # Same position (centered) - verify by bounding box
            success_box = success_panel.bounding_box()
            success_center_x = success_box['x'] + success_box['width'] / 2
            success_center_y = success_box['y'] + success_box['height'] / 2
            assert abs(success_center_x - viewport_center_x) < 5, f"Success panel should be centered horizontally"
            assert abs(success_center_y - viewport_center_y) < 5, f"Success panel should be centered vertically"

            # Same hot-pink glassmorphic appearance
            success_background = success_style.get('backgroundColor', '')
            assert 'rgba(255, 20, 147, 0.5)' in success_background or 'rgba(255, 20, 147, 0.498)' in success_background, f"Success panel should have same hot-pink background, got {success_background}"

            success_backdrop = success_style.get('backdropFilter', '') or success_style.get('-webkit-backdrop-filter', '')
            assert 'blur' in success_backdrop.lower(), f"Success panel should have backdrop blur effect, got {success_backdrop}"

            # $REQ_DEMO_FORM_007: Success Panel Content
            # Verify success panel contains only centered text "(Your App Here)"
            success_text = success_panel.locator('p')
            assert success_text.is_visible(), "Success panel should have text content"
            assert success_text.text_content() == '(Your App Here)', "Success panel text should be '(Your App Here)'"

            # Verify it's centered
            text_align = success_text.evaluate('el => window.getComputedStyle(el).textAlign')
            assert text_align == 'center', "Success panel text should be centered"

            # Verify no other elements besides the paragraph
            success_children = success_panel.evaluate('el => el.children.length')
            assert success_children == 1, "Success panel should contain only one element (the paragraph)"

            browser.close()

    except ImportError:
        print("Playwright not installed. Installing browsers...")
        subprocess.run([
            sys.executable, '-m', 'playwright', 'install', 'chromium'
        ], check=True, encoding='utf-8')
        print("Browsers installed. Please run the test again.")
        sys.exit(1)

    print("✓ All demo form tests passed!")
    sys.exit(0)

if __name__ == '__main__':
    main()
