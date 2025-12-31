#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["playwright"]
# ///

"""
Test suite for boost velocity requirements.
Verifies boost accessors, decay, boundary reversal, and combination with base velocity.
"""

import sys
import time
from pathlib import Path

# Add the-system/scripts to path for websrvr
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'the-system' / 'scripts'))

from playwright.sync_api import sync_playwright
from websrvr import start_server, stop_server, get_server_url


def test_boost_velocity():
    """Test all boost velocity requirements."""

    port = start_server('./released')
    url = get_server_url(port)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Navigate to demo page
        page.goto(f"{url}/skrolbak/demo.html")

        # Wait for element to be ready
        page.wait_for_selector('animated-background')

        # $REQ_BOOST-VEL_001: Boost Accessors
        # Test that get/set properties exist for boost velocity on each axis
        pan_x_boost = page.evaluate("document.querySelector('animated-background').panXBoost")
        pan_y_boost = page.evaluate("document.querySelector('animated-background').panYBoost")
        pan_z_boost = page.evaluate("document.querySelector('animated-background').panZBoost")
        rot_x_boost = page.evaluate("document.querySelector('animated-background').rotXBoost")
        rot_y_boost = page.evaluate("document.querySelector('animated-background').rotYBoost")
        rot_z_boost = page.evaluate("document.querySelector('animated-background').rotZBoost")

        assert pan_x_boost is not None, "panXBoost accessor should exist"
        assert pan_y_boost is not None, "panYBoost accessor should exist"
        assert pan_z_boost is not None, "panZBoost accessor should exist"
        assert rot_x_boost is not None, "rotXBoost accessor should exist"
        assert rot_y_boost is not None, "rotYBoost accessor should exist"
        assert rot_z_boost is not None, "rotZBoost accessor should exist"

        # Test setter
        page.evaluate("document.querySelector('animated-background').panXBoost = 10")
        new_pan_x_boost = page.evaluate("document.querySelector('animated-background').panXBoost")
        assert new_pan_x_boost == 10, "panXBoost setter should work"  # $REQ_BOOST-VEL_001

        # $REQ_BOOST-VEL_002: Boost Default Value
        # Create a new element to test default values
        page.evaluate("""
            const newEl = document.createElement('animated-background');
            newEl.setAttribute('src', 'test.jpg');
            newEl.setAttribute('pan-x', '50');
            newEl.id = 'test-element';
            document.body.appendChild(newEl);
        """)

        time.sleep(0.1)  # Give it time to connect

        # Check all boost values default to 0
        test_el_pan_x_boost = page.evaluate("document.getElementById('test-element').panXBoost")
        test_el_pan_y_boost = page.evaluate("document.getElementById('test-element').panYBoost")
        test_el_pan_z_boost = page.evaluate("document.getElementById('test-element').panZBoost")
        test_el_rot_x_boost = page.evaluate("document.getElementById('test-element').rotXBoost")
        test_el_rot_y_boost = page.evaluate("document.getElementById('test-element').rotYBoost")
        test_el_rot_z_boost = page.evaluate("document.getElementById('test-element').rotZBoost")

        assert test_el_pan_x_boost == 0, "panXBoost should default to 0"  # $REQ_BOOST-VEL_002
        assert test_el_pan_y_boost == 0, "panYBoost should default to 0"  # $REQ_BOOST-VEL_002
        assert test_el_pan_z_boost == 0, "panZBoost should default to 0"  # $REQ_BOOST-VEL_002
        assert test_el_rot_x_boost == 0, "rotXBoost should default to 0"  # $REQ_BOOST-VEL_002
        assert test_el_rot_y_boost == 0, "rotYBoost should default to 0"  # $REQ_BOOST-VEL_002
        assert test_el_rot_z_boost == 0, "rotZBoost should default to 0"  # $REQ_BOOST-VEL_002

        # $REQ_BOOST-VEL_003: Effective Velocity Calculation
        # Test that position updates use effective velocity = base + boost
        page.evaluate("""
            const el = document.getElementById('test-element');
            el.setAttribute('pan-x', '100');  // Allow full range
            el.panXVelocity = 5;
            el.panXBoost = 3;
            el.panXPosition = 0;
        """)

        initial_position = page.evaluate("document.getElementById('test-element').panXPosition")

        # Wait for exactly 1 second to make calculation clear
        time.sleep(1.1)

        final_position = page.evaluate("document.getElementById('test-element').panXPosition")

        # Position should have moved by effective velocity = 5 + 3 = 8% per second
        # In 1 second, should move about 8 units
        # Allow some tolerance for timing and decay (boost will decay by 1 during this time)
        expected_movement = 8  # 5 (base) + 3 (boost) = 8% per second
        actual_movement = abs(final_position - initial_position)

        # The boost decays by 1 after 1 second, so average boost is ~2.5
        # Expected: 5 + 2.5 = 7.5, but initial tick uses full 8
        assert actual_movement >= 6, f"Movement should be at least 6% with effective velocity, got {actual_movement}"  # $REQ_BOOST-VEL_003
        assert actual_movement <= 10, f"Movement should be at most 10% with effective velocity, got {actual_movement}"  # $REQ_BOOST-VEL_003

        # $REQ_BOOST-VEL_004: Boost Decay Toward Zero
        # Test boost decay at each tick
        page.evaluate("""
            const el = document.getElementById('test-element');
            el.setAttribute('t', '0');
            el.panXBoost = 5;
            el.panYBoost = -5;
            el.panZBoost = 0.5;
        """)

        # Get initial values
        initial_pan_x_boost = page.evaluate("document.getElementById('test-element').panXBoost")
        initial_pan_y_boost = page.evaluate("document.getElementById('test-element').panYBoost")
        initial_pan_z_boost = page.evaluate("document.getElementById('test-element').panZBoost")

        assert initial_pan_x_boost == 5, "Initial panXBoost should be 5"
        assert initial_pan_y_boost == -5, "Initial panYBoost should be -5"
        assert initial_pan_z_boost == 0.5, "Initial panZBoost should be 0.5"

        # Wait for 1 tick (1 second)
        time.sleep(1.1)

        # Check decay: positive boost decreased by 1, negative increased by 1, small boost becomes 0
        pan_x_boost_after = page.evaluate("document.getElementById('test-element').panXBoost")
        pan_y_boost_after = page.evaluate("document.getElementById('test-element').panYBoost")
        pan_z_boost_after = page.evaluate("document.getElementById('test-element').panZBoost")

        assert pan_x_boost_after == 4, f"panXBoost should decay from 5 to 4, got {pan_x_boost_after}"  # $REQ_BOOST-VEL_004
        assert pan_y_boost_after == -4, f"panYBoost should decay from -5 to -4, got {pan_y_boost_after}"  # $REQ_BOOST-VEL_004
        assert pan_z_boost_after == 0, f"panZBoost between -1 and 1 should become 0, got {pan_z_boost_after}"  # $REQ_BOOST-VEL_004

        # $REQ_BOOST-VEL_005: Boost Reversal at Boundaries
        # Test that boost reverses when position hits boundary
        page.evaluate("""
            const el = document.getElementById('test-element');
            el.setAttribute('pan-x', '50');
            el.panXPosition = 49;  // Near max boundary (50)
            el.panXVelocity = 10;
            el.panXBoost = 5;
        """)

        # Wait for boundary hit
        time.sleep(0.2)

        # Check that boost was reversed
        final_boost = page.evaluate("document.getElementById('test-element').panXBoost")
        final_velocity = page.evaluate("document.getElementById('test-element').panXVelocity")

        # Both should be negative after boundary reversal
        assert final_boost < 0, f"Boost should be negative after boundary reversal, got {final_boost}"  # $REQ_BOOST-VEL_005
        assert final_velocity < 0, f"Velocity should be negative after boundary reversal, got {final_velocity}"  # $REQ_BOOST-VEL_005

        # $REQ_BOOST-VEL_006: Boost Not Simulated During Fast-Forward
        # Test that boost remains 0 when using t attribute for fast-forward
        page.evaluate("""
            const ffEl = document.createElement('animated-background');
            ffEl.setAttribute('src', 'test.jpg');
            ffEl.setAttribute('pan-x', '50');
            ffEl.setAttribute('t', '10');  // Fast-forward to t=10
            ffEl.id = 'ff-element';
            document.body.appendChild(ffEl);
        """)

        time.sleep(0.2)

        # Check that all boost values are still 0 after fast-forward
        ff_pan_x_boost = page.evaluate("document.getElementById('ff-element').panXBoost")
        ff_pan_y_boost = page.evaluate("document.getElementById('ff-element').panYBoost")
        ff_pan_z_boost = page.evaluate("document.getElementById('ff-element').panZBoost")
        ff_rot_x_boost = page.evaluate("document.getElementById('ff-element').rotXBoost")
        ff_rot_y_boost = page.evaluate("document.getElementById('ff-element').rotYBoost")
        ff_rot_z_boost = page.evaluate("document.getElementById('ff-element').rotZBoost")

        assert ff_pan_x_boost == 0, "panXBoost should remain 0 after fast-forward"  # $REQ_BOOST-VEL_006
        assert ff_pan_y_boost == 0, "panYBoost should remain 0 after fast-forward"  # $REQ_BOOST-VEL_006
        assert ff_pan_z_boost == 0, "panZBoost should remain 0 after fast-forward"  # $REQ_BOOST-VEL_006
        assert ff_rot_x_boost == 0, "rotXBoost should remain 0 after fast-forward"  # $REQ_BOOST-VEL_006
        assert ff_rot_y_boost == 0, "rotYBoost should remain 0 after fast-forward"  # $REQ_BOOST-VEL_006
        assert ff_rot_z_boost == 0, "rotZBoost should remain 0 after fast-forward"  # $REQ_BOOST-VEL_006

        browser.close()

    stop_server()
    print("✓ All boost velocity tests passed")


if __name__ == '__main__':
    try:
        test_boost_velocity()
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
