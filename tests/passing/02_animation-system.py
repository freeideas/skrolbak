#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["playwright"]
# ///

"""
Test suite for animation system requirements.
Verifies state variables, velocity semantics, boundary behavior, and initialization.
"""

import sys
import time
from pathlib import Path

# Add the-system/scripts to path for websrvr
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'the-system' / 'scripts'))

from playwright.sync_api import sync_playwright
from websrvr import start_server, stop_server, get_server_url


def test_animation_system():
    """Test all animation system requirements."""

    port = start_server('./released')
    url = get_server_url(port)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Set up console logging capture
        console_logs = []
        page.on('console', lambda msg: console_logs.append(msg.text))

        # Navigate to demo page
        page.goto(f"{url}/skrolbak/demo.html")

        # Wait for element to be ready
        page.wait_for_selector('animated-background')

        # $REQ_ANIM_001: State Variables Per Axis
        # Test that each axis maintains position and velocity
        pan_x_position = page.evaluate("document.querySelector('animated-background').panXPosition")
        pan_x_velocity = page.evaluate("document.querySelector('animated-background').panXVelocity")
        pan_y_position = page.evaluate("document.querySelector('animated-background').panYPosition")
        pan_y_velocity = page.evaluate("document.querySelector('animated-background').panYVelocity")
        pan_z_position = page.evaluate("document.querySelector('animated-background').panZPosition")
        pan_z_velocity = page.evaluate("document.querySelector('animated-background').panZVelocity")
        rot_x_position = page.evaluate("document.querySelector('animated-background').rotXPosition")
        rot_x_velocity = page.evaluate("document.querySelector('animated-background').rotXVelocity")
        rot_y_position = page.evaluate("document.querySelector('animated-background').rotYPosition")
        rot_y_velocity = page.evaluate("document.querySelector('animated-background').rotYVelocity")
        rot_z_position = page.evaluate("document.querySelector('animated-background').rotZPosition")
        rot_z_velocity = page.evaluate("document.querySelector('animated-background').rotZVelocity")

        assert pan_x_position is not None, "panXPosition should exist"  # $REQ_ANIM_001
        assert pan_x_velocity is not None, "panXVelocity should exist"  # $REQ_ANIM_001
        assert pan_y_position is not None, "panYPosition should exist"  # $REQ_ANIM_001
        assert pan_y_velocity is not None, "panYVelocity should exist"  # $REQ_ANIM_001
        assert pan_z_position is not None, "panZPosition should exist"  # $REQ_ANIM_001
        assert pan_z_velocity is not None, "panZVelocity should exist"  # $REQ_ANIM_001
        assert rot_x_position is not None, "rotXPosition should exist"  # $REQ_ANIM_001
        assert rot_x_velocity is not None, "rotXVelocity should exist"  # $REQ_ANIM_001
        assert rot_y_position is not None, "rotYPosition should exist"  # $REQ_ANIM_001
        assert rot_y_velocity is not None, "rotYVelocity should exist"  # $REQ_ANIM_001
        assert rot_z_position is not None, "rotZPosition should exist"  # $REQ_ANIM_001
        assert rot_z_velocity is not None, "rotZVelocity should exist"  # $REQ_ANIM_001

        # $REQ_ANIM_002: Velocity Units
        # Test that velocity is in percent of range per second
        page.evaluate("""
            const el = document.createElement('animated-background');
            el.setAttribute('src', 'test.jpg');
            el.setAttribute('pan-x', '100');  // Full range
            el.id = 'velocity-test';
            document.body.appendChild(el);
        """)
        time.sleep(0.1)

        # Set known velocity and position
        page.evaluate("""
            const el = document.getElementById('velocity-test');
            el.panXVelocity = 10;  // 10% per second
            el.panXPosition = 0;
        """)

        initial_position = page.evaluate("document.getElementById('velocity-test').panXPosition")
        time.sleep(1.1)  # Wait ~1 second
        final_position = page.evaluate("document.getElementById('velocity-test').panXPosition")

        movement = abs(final_position - initial_position)
        # Movement should be approximately 10% (allowing for timing variance and velocity changes)
        assert movement >= 8, f"Movement should be at least 8% with 10%/s velocity, got {movement}"  # $REQ_ANIM_002
        assert movement <= 15, f"Movement should be at most 15% with 10%/s velocity, got {movement}"  # $REQ_ANIM_002

        # $REQ_ANIM_003: No Zero Velocity
        # Test that velocity never becomes zero for axes with non-zero range
        page.evaluate("""
            const el = document.createElement('animated-background');
            el.setAttribute('src', 'test.jpg');
            el.setAttribute('pan-x', '50');
            el.id = 'no-zero-velocity-test';
            document.body.appendChild(el);
        """)
        time.sleep(0.1)

        # Check velocity after several ticks
        for i in range(5):
            time.sleep(1.1)
            velocity = page.evaluate("document.getElementById('no-zero-velocity-test').panXVelocity")
            assert velocity != 0, f"Velocity should never be zero for axis with non-zero range, got {velocity} at tick {i}"  # $REQ_ANIM_003

        # $REQ_ANIM_004: Velocity Update Frequency
        # $REQ_ANIM_005: Velocity Magnitude Change
        # Test that velocity magnitude changes by ±1 per second
        page.evaluate("""
            const el = document.createElement('animated-background');
            el.setAttribute('src', 'test.jpg');
            el.setAttribute('pan-x', '50');
            el.id = 'velocity-update-test';
            document.body.appendChild(el);
        """)
        time.sleep(0.1)

        # Set velocity to a value > 1 so we can observe both increase and decrease
        page.evaluate("document.getElementById('velocity-update-test').panXVelocity = 5")
        time.sleep(0.5)  # Let it settle

        initial_velocity = page.evaluate("document.getElementById('velocity-update-test').panXVelocity")
        initial_magnitude = abs(initial_velocity)

        time.sleep(1.1)  # Wait for one tick

        new_velocity = page.evaluate("document.getElementById('velocity-update-test').panXVelocity")
        new_magnitude = abs(new_velocity)

        # Magnitude should change by exactly 1 (either +1 or -1)
        magnitude_change = abs(new_magnitude - initial_magnitude)
        assert magnitude_change == 1, f"Velocity magnitude should change by 1 per tick, changed by {magnitude_change} (from {initial_magnitude} to {new_magnitude})"  # $REQ_ANIM_004, $REQ_ANIM_005

        # $REQ_ANIM_006: Range Boundary Reversal
        # Test that velocity reverses at boundaries
        page.evaluate("""
            const el = document.createElement('animated-background');
            el.setAttribute('src', 'test.jpg');
            el.setAttribute('pan-x', '50');
            el.id = 'boundary-test';
            document.body.appendChild(el);
        """)
        time.sleep(0.1)

        # Position near max boundary, set positive velocity
        page.evaluate("""
            const el = document.getElementById('boundary-test');
            el.panXPosition = 24;  // Near max (25 for 50% range)
            el.panXVelocity = 50;  // Large positive velocity
        """)

        initial_velocity = page.evaluate("document.getElementById('boundary-test').panXVelocity")
        assert initial_velocity > 0, "Initial velocity should be positive"

        time.sleep(0.2)  # Wait for boundary hit

        final_velocity = page.evaluate("document.getElementById('boundary-test').panXVelocity")
        final_position = page.evaluate("document.getElementById('boundary-test').panXPosition")

        assert final_velocity < 0, f"Velocity should reverse to negative after hitting boundary, got {final_velocity}"  # $REQ_ANIM_006
        assert final_position <= 25, f"Position should be at or below boundary, got {final_position}"

        # $REQ_ANIM_007: Initial Position Values
        # Test that all positions start at 0
        # Check immediately in the same evaluate call to avoid animation delays
        init_positions = page.evaluate("""() => {
            const el = document.createElement('animated-background');
            el.setAttribute('src', 'test.jpg');
            el.setAttribute('pan-x', '50');
            el.setAttribute('pan-y', '50');
            el.setAttribute('pan-z', '50');
            el.setAttribute('rot-x', '50');
            el.setAttribute('rot-y', '50');
            el.setAttribute('rot-z', '50');
            el.id = 'init-position-test';
            document.body.appendChild(el);

            // Check positions immediately after connection
            return {
                panX: el.panXPosition,
                panY: el.panYPosition,
                panZ: el.panZPosition,
                rotX: el.rotXPosition,
                rotY: el.rotYPosition,
                rotZ: el.rotZPosition
            };
        }""")

        assert init_positions['panX'] == 0, f"panXPosition should start at 0, got {init_positions['panX']}"  # $REQ_ANIM_007
        assert init_positions['panY'] == 0, f"panYPosition should start at 0, got {init_positions['panY']}"  # $REQ_ANIM_007
        assert init_positions['panZ'] == 0, f"panZPosition should start at 0, got {init_positions['panZ']}"  # $REQ_ANIM_007
        assert init_positions['rotX'] == 0, f"rotXPosition should start at 0, got {init_positions['rotX']}"  # $REQ_ANIM_007
        assert init_positions['rotY'] == 0, f"rotYPosition should start at 0, got {init_positions['rotY']}"  # $REQ_ANIM_007
        assert init_positions['rotZ'] == 0, f"rotZPosition should start at 0, got {init_positions['rotZ']}"  # $REQ_ANIM_007

        # $REQ_ANIM_008: Initial Velocity Assignment
        # Test that axes with non-zero range get ±1 initial velocity
        init_pan_x_vel = page.evaluate("document.getElementById('init-position-test').panXVelocity")
        init_pan_y_vel = page.evaluate("document.getElementById('init-position-test').panYVelocity")
        init_pan_z_vel = page.evaluate("document.getElementById('init-position-test').panZVelocity")
        init_rot_x_vel = page.evaluate("document.getElementById('init-position-test').rotXVelocity")
        init_rot_y_vel = page.evaluate("document.getElementById('init-position-test').rotYVelocity")
        init_rot_z_vel = page.evaluate("document.getElementById('init-position-test').rotZVelocity")

        assert abs(init_pan_x_vel) == 1, f"panXVelocity should be ±1, got {init_pan_x_vel}"  # $REQ_ANIM_008
        assert abs(init_pan_y_vel) == 1, f"panYVelocity should be ±1, got {init_pan_y_vel}"  # $REQ_ANIM_008
        assert abs(init_pan_z_vel) == 1, f"panZVelocity should be ±1, got {init_pan_z_vel}"  # $REQ_ANIM_008
        assert abs(init_rot_x_vel) == 1, f"rotXVelocity should be ±1, got {init_rot_x_vel}"  # $REQ_ANIM_008
        assert abs(init_rot_y_vel) == 1, f"rotYVelocity should be ±1, got {init_rot_y_vel}"  # $REQ_ANIM_008
        assert abs(init_rot_z_vel) == 1, f"rotZVelocity should be ±1, got {init_rot_z_vel}"  # $REQ_ANIM_008

        # $REQ_ANIM_009: Zero Range Axis Behavior
        # Test that axes with range=0 have no velocity
        page.evaluate("""
            const el = document.createElement('animated-background');
            el.setAttribute('src', 'test.jpg');
            el.setAttribute('pan-x', '0');  // Zero range
            el.id = 'zero-range-test';
            document.body.appendChild(el);
        """)
        time.sleep(0.1)

        zero_range_velocity = page.evaluate("document.getElementById('zero-range-test').panXVelocity")
        assert zero_range_velocity == 0, f"Velocity should be 0 for zero-range axis, got {zero_range_velocity}"  # $REQ_ANIM_009

        time.sleep(1.1)
        zero_range_velocity_after = page.evaluate("document.getElementById('zero-range-test').panXVelocity")
        assert zero_range_velocity_after == 0, f"Velocity should remain 0 for zero-range axis, got {zero_range_velocity_after}"  # $REQ_ANIM_009

        # $REQ_ANIM_010: Animation Loop Integration
        # Test that positions update continuously with time
        page.evaluate("""
            const el = document.createElement('animated-background');
            el.setAttribute('src', 'test.jpg');
            el.setAttribute('pan-x', '100');
            el.id = 'animation-loop-test';
            document.body.appendChild(el);
        """)
        time.sleep(0.1)

        page.evaluate("""
            const el = document.getElementById('animation-loop-test');
            el.panXVelocity = 5;
            el.panXPosition = 0;
        """)

        positions = []
        for i in range(5):
            pos = page.evaluate("document.getElementById('animation-loop-test').panXPosition")
            positions.append(pos)
            time.sleep(0.2)

        # Position should change continuously
        unique_positions = len(set(positions))
        assert unique_positions >= 3, f"Position should change continuously, got {unique_positions} unique values"  # $REQ_ANIM_010

        # $REQ_ANIM_011: Tick Console Logging
        # Test that ticks are logged to console
        console_logs.clear()

        page.evaluate("""
            const el = document.createElement('animated-background');
            el.setAttribute('src', 'test.jpg');
            el.setAttribute('pan-x', '50');
            el.setAttribute('t', '0');
            el.id = 'tick-log-test';
            document.body.appendChild(el);
        """)

        time.sleep(2.2)  # Wait for at least 2 ticks

        tick_logs = [log for log in console_logs if log.startswith('t=')]
        assert len(tick_logs) >= 2, f"Should have at least 2 tick logs, got {len(tick_logs)}: {tick_logs}"  # $REQ_ANIM_011

        # Verify format
        assert any('t=0' in log for log in tick_logs), "Should have t=0 log"  # $REQ_ANIM_011
        assert any('t=1' in log or 't=2' in log for log in tick_logs), "Should have t=1 or t=2 log"  # $REQ_ANIM_011

        # $REQ_ANIM_012: Boost Effective Velocity
        # Test that effective velocity includes boost
        page.evaluate("""
            const el = document.createElement('animated-background');
            el.setAttribute('src', 'test.jpg');
            el.setAttribute('pan-x', '100');
            el.id = 'effective-velocity-test';
            document.body.appendChild(el);
        """)
        time.sleep(0.1)

        page.evaluate("""
            const el = document.getElementById('effective-velocity-test');
            el.panXVelocity = 5;
            el.panXBoost = 10;
            el.panXPosition = 0;
        """)

        initial_pos = page.evaluate("document.getElementById('effective-velocity-test').panXPosition")
        time.sleep(0.5)
        final_pos = page.evaluate("document.getElementById('effective-velocity-test').panXPosition")

        movement = abs(final_pos - initial_pos)
        # With effective velocity of 15 (5 + 10), in 0.5 seconds should move ~7.5
        assert movement >= 5, f"Movement with boost should be significant, got {movement}"  # $REQ_ANIM_012

        # $REQ_ANIM_013: Boost Decay Per Tick
        # Test that boost decays by 1 per tick
        page.evaluate("""
            const el = document.createElement('animated-background');
            el.setAttribute('src', 'test.jpg');
            el.setAttribute('pan-x', '50');
            el.setAttribute('t', '0');
            el.id = 'boost-decay-test';
            document.body.appendChild(el);
        """)
        time.sleep(0.1)

        page.evaluate("""
            const el = document.getElementById('boost-decay-test');
            el.panXBoost = 5;
        """)

        initial_boost = page.evaluate("document.getElementById('boost-decay-test').panXBoost")
        assert initial_boost == 5, f"Initial boost should be 5, got {initial_boost}"

        time.sleep(1.1)  # Wait for one tick

        decayed_boost = page.evaluate("document.getElementById('boost-decay-test').panXBoost")
        assert decayed_boost == 4, f"Boost should decay from 5 to 4, got {decayed_boost}"  # $REQ_ANIM_013

        # $REQ_ANIM_014: Boost Boundary Reversal
        # Test that boost reverses at boundaries
        page.evaluate("""
            const el = document.createElement('animated-background');
            el.setAttribute('src', 'test.jpg');
            el.setAttribute('pan-x', '50');
            el.id = 'boost-boundary-test';
            document.body.appendChild(el);
        """)
        time.sleep(0.1)

        page.evaluate("""
            const el = document.getElementById('boost-boundary-test');
            el.panXPosition = 24;
            el.panXVelocity = 20;
            el.panXBoost = 10;
        """)

        time.sleep(0.2)  # Wait for boundary hit

        final_boost = page.evaluate("document.getElementById('boost-boundary-test').panXBoost")
        assert final_boost < 0, f"Boost should reverse to negative after boundary hit, got {final_boost}"  # $REQ_ANIM_014

        # $REQ_ANIM_015: Boost Initial Value
        # Test that boost starts at 0
        page.evaluate("""
            const el = document.createElement('animated-background');
            el.setAttribute('src', 'test.jpg');
            el.setAttribute('pan-x', '50');
            el.id = 'boost-init-test';
            document.body.appendChild(el);
        """)
        time.sleep(0.1)

        init_boost_x = page.evaluate("document.getElementById('boost-init-test').panXBoost")
        init_boost_y = page.evaluate("document.getElementById('boost-init-test').panYBoost")
        init_boost_z = page.evaluate("document.getElementById('boost-init-test').panZBoost")

        assert init_boost_x == 0, f"panXBoost should start at 0, got {init_boost_x}"  # $REQ_ANIM_015
        assert init_boost_y == 0, f"panYBoost should start at 0, got {init_boost_y}"  # $REQ_ANIM_015
        assert init_boost_z == 0, f"panZBoost should start at 0, got {init_boost_z}"  # $REQ_ANIM_015

        # $REQ_ANIM_016: Boost Not Simulated on Fast-Forward
        # Test that boost remains 0 after fast-forward
        page.evaluate("""
            const el = document.createElement('animated-background');
            el.setAttribute('src', 'test.jpg');
            el.setAttribute('pan-x', '50');
            el.setAttribute('t', '10');
            el.id = 'boost-ff-test';
            document.body.appendChild(el);
        """)
        time.sleep(0.2)

        ff_boost_x = page.evaluate("document.getElementById('boost-ff-test').panXBoost")
        ff_boost_y = page.evaluate("document.getElementById('boost-ff-test').panYBoost")
        ff_boost_z = page.evaluate("document.getElementById('boost-ff-test').panZBoost")

        assert ff_boost_x == 0, f"panXBoost should remain 0 after fast-forward, got {ff_boost_x}"  # $REQ_ANIM_016
        assert ff_boost_y == 0, f"panYBoost should remain 0 after fast-forward, got {ff_boost_y}"  # $REQ_ANIM_016
        assert ff_boost_z == 0, f"panZBoost should remain 0 after fast-forward, got {ff_boost_z}"  # $REQ_ANIM_016

        browser.close()

    stop_server()
    print("✓ All animation system tests passed")


if __name__ == '__main__':
    try:
        test_animation_system()
    except AssertionError as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
