#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["playwright"]
# ///

"""
Test for deterministic replay requirements.
"""

import sys
import time
import subprocess
import atexit
from pathlib import Path

# Add the-system/scripts to path for websrvr
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'the-system' / 'scripts'))
from websrvr import start_server, stop_server, get_server_url

_procs = []

def cleanup():
    for p in _procs:
        try:
            p.terminate()
            p.wait(timeout=2)
        except:
            pass
    stop_server()

atexit.register(cleanup)

def test_deterministic_replay():
    """Test all deterministic replay requirements."""

    # Build the project first
    build_result = subprocess.run(
        ['../../the-system/bin/uv.linux', 'run', '--script', '../../code/build.py'],
        cwd=Path(__file__).resolve().parent,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    if build_result.returncode != 0:
        print(f"Build failed:\n{build_result.stderr}")
        sys.exit(97)

    # Start web server
    port = start_server('./released')
    url = get_server_url(port)

    # Import playwright after server is started
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()

        # Test 1: $REQ_REPLAY_001, $REQ_REPLAY_003, $REQ_REPLAY_004
        # Time counter starts at t attribute value and logs to console
        page1 = browser.new_context().new_page()

        console_logs = []
        page1.on('console', lambda msg: console_logs.append(msg.text))

        page1.goto(f'{url}/skrolbak/demo.html')
        page1.wait_for_load_state('networkidle')

        # Create an element with t="5"
        page1.evaluate("""
            const elem = document.createElement('animated-background');
            elem.setAttribute('src', 'test.png');
            elem.setAttribute('pan-x', '100');
            elem.setAttribute('pan-y', '100');
            elem.setAttribute('t', '5');
            document.body.appendChild(elem);
        """)

        # Wait a bit for initialization
        time.sleep(0.5)

        # $REQ_REPLAY_001: Time counter starts at t attribute value
        # $REQ_REPLAY_004: Animation begins at specified tick
        # Should see t=5 in console immediately after fast-forward
        assert any('t=5' in log for log in console_logs), f"Expected t=5 in console logs, got: {console_logs}"  # $REQ_REPLAY_001, $REQ_REPLAY_004

        # $REQ_REPLAY_003: Console tick logging
        # Console should log t=N format
        initial_log_count = len([log for log in console_logs if log.startswith('t=')])
        assert initial_log_count > 0, "Expected at least one tick log"  # $REQ_REPLAY_003

        page1.close()

        # Test 2: $REQ_REPLAY_002
        # Time counter increments each second
        page2 = browser.new_context().new_page()

        console_logs2 = []
        page2.on('console', lambda msg: console_logs2.append(msg.text))

        page2.goto(f'{url}/skrolbak/demo.html')
        page2.wait_for_load_state('networkidle')

        # Remove existing animated-background elements
        page2.evaluate("""
            document.querySelectorAll('animated-background').forEach(el => el.remove());
        """)

        # Clear console logs captured so far
        console_logs2.clear()

        # Create element and wait for animation to run
        page2.evaluate("""
            window.testElem2 = document.createElement('animated-background');
            testElem2.setAttribute('src', 'test.png');
            testElem2.setAttribute('pan-x', '100');
            testElem2.setAttribute('t', '0');
            document.body.appendChild(testElem2);
        """)

        # Wait for t to reach at least 2 (meaning we've seen t=0, t=1, t=2)
        page2.wait_for_function("window.testElem2._t >= 2", timeout=5000)

        # $REQ_REPLAY_002: Time counter increments each second
        tick_logs = [log for log in console_logs2 if log.startswith('t=')]

        # We should have seen t=0, t=1, and t=2
        assert len(tick_logs) >= 2, f"Expected at least 2 tick logs (t=0 and t=1), got: {tick_logs}"
        assert 't=0' in tick_logs, f"Expected t=0 in logs, got: {tick_logs}"
        assert 't=1' in tick_logs, f"Expected t=1 in logs, got: {tick_logs}"  # $REQ_REPLAY_002

        page2.close()

        # Test 3: $REQ_REPLAY_005, $REQ_REPLAY_006, $REQ_REPLAY_007
        # Deterministic PRNG function
        page3 = browser.new_context().new_page()
        page3.goto(f'{url}/skrolbak/demo.html')
        page3.wait_for_load_state('networkidle')

        # Test PRNG determinism
        result1 = page3.evaluate("""() => {
            const elem = document.createElement('animated-background');
            elem.setAttribute('src', 'test.png');
            elem.setAttribute('pan-x', '100');
            elem.setAttribute('pan-y', '100');
            elem.setAttribute('rot-x', '100');
            document.body.appendChild(elem);

            // Access the PRNG function
            const prng1 = elem._prng(0, 'test');
            const prng2 = elem._prng(0, 'test');
            const prng3 = elem._prng(1, 'test');
            const prng4 = elem._prng(0, 'other');

            // $REQ_REPLAY_005: Same inputs produce same result
            const sameInputsSameResult = prng1 === prng2;

            // Different t or salt should potentially give different results
            // (not guaranteed, but we can at least test consistency)
            const prng1_repeat = elem._prng(0, 'test');
            const consistentResults = prng1 === prng1_repeat;

            // Get initial velocities to verify PRNG usage
            // $REQ_REPLAY_006: Initial velocity direction via PRNG
            const panXVel = elem.panXVelocity;
            const panYVel = elem.panYVelocity;
            const rotXVel = elem.rotXVelocity;

            return {
                sameInputsSameResult,
                consistentResults,
                panXVel,
                panYVel,
                rotXVel,
                prng1,
                prng2,
                prng3,
                prng4
            };
        }""")

        # $REQ_REPLAY_005: Deterministic PRNG function - same inputs always produce same result
        assert result1['sameInputsSameResult'], "PRNG with same inputs should produce same result"  # $REQ_REPLAY_005
        assert result1['consistentResults'], "PRNG should be consistent across calls"  # $REQ_REPLAY_005

        # $REQ_REPLAY_006: Initial velocity direction via PRNG - should be +1 or -1
        assert result1['panXVel'] in [1, -1], f"Expected panXVel to be ±1, got {result1['panXVel']}"  # $REQ_REPLAY_006
        assert result1['panYVel'] in [1, -1], f"Expected panYVel to be ±1, got {result1['panYVel']}"  # $REQ_REPLAY_006
        assert result1['rotXVel'] in [1, -1], f"Expected rotXVel to be ±1, got {result1['rotXVel']}"  # $REQ_REPLAY_006

        page3.close()

        # Test 4: $REQ_REPLAY_007
        # Velocity magnitude change via PRNG
        page4 = browser.new_context().new_page()
        page4.goto(f'{url}/skrolbak/demo.html')
        page4.wait_for_load_state('networkidle')

        result4 = page4.evaluate("""() => {
            const elem = document.createElement('animated-background');
            elem.setAttribute('src', 'test.png');
            elem.setAttribute('pan-x', '100');
            document.body.appendChild(elem);

            // Get initial velocity
            const initialVel = Math.abs(elem.panXVelocity);

            // Manually trigger tick update to test PRNG usage for velocity changes
            // Store multiple velocity changes to see PRNG in action
            const velocityChanges = [];
            for (let t = 0; t < 10; t++) {
                const prngResult = elem._prng(t, 'panX-vel');
                velocityChanges.push(prngResult);
            }

            return {
                initialVel,
                velocityChanges
            };
        }""")

        # $REQ_REPLAY_007: Velocity magnitude change via PRNG
        # PRNG results should be boolean (true/false)
        assert all(isinstance(v, bool) for v in result4['velocityChanges']), "PRNG should return boolean values"  # $REQ_REPLAY_007

        page4.close()

        # Test 5: $REQ_REPLAY_008
        # Fast-forward produces identical state
        page5a = browser.new_context().new_page()
        page5b = browser.new_context().new_page()

        page5a.goto(f'{url}/skrolbak/demo.html')
        page5a.wait_for_load_state('networkidle')
        page5b.goto(f'{url}/skrolbak/demo.html')
        page5b.wait_for_load_state('networkidle')

        # Create element at t=0 and wait 3 seconds
        page5a.evaluate("""
            window.testElem = document.createElement('animated-background');
            testElem.setAttribute('src', 'test.png');
            testElem.setAttribute('pan-x', '100');
            testElem.setAttribute('pan-y', '100');
            testElem.setAttribute('rot-x', '100');
            testElem.setAttribute('t', '0');
            document.body.appendChild(testElem);
        """)

        # Wait for 3 seconds of animation plus a bit more to ensure we're past the t=3 boundary
        time.sleep(3.5)

        positions_slow = page5a.evaluate("""() => ({
            t: testElem._t,
            panX: testElem.panXPosition,
            panY: testElem.panYPosition,
            rotX: testElem.rotXPosition,
            panXVel: testElem.panXVelocity,
            panYVel: testElem.panYVelocity,
            rotXVel: testElem.rotXVelocity
        })""")

        # Create element at t=2 and wait 1 second to reach t=3
        page5b.evaluate("""
            window.testElem = document.createElement('animated-background');
            testElem.setAttribute('src', 'test.png');
            testElem.setAttribute('pan-x', '100');
            testElem.setAttribute('pan-y', '100');
            testElem.setAttribute('rot-x', '100');
            testElem.setAttribute('t', '2');
            document.body.appendChild(testElem);
        """)

        # Wait for 1 second of animation to reach t=3 plus a bit more to ensure we're past the t=3 boundary
        time.sleep(1.5)

        positions_fast = page5b.evaluate("""() => ({
            t: testElem._t,
            panX: testElem.panXPosition,
            panY: testElem.panYPosition,
            rotX: testElem.rotXPosition,
            panXVel: testElem.panXVelocity,
            panYVel: testElem.panYVelocity,
            rotXVel: testElem.rotXVelocity
        })""")

        # $REQ_REPLAY_008: Fast-forward produces identical state
        # Positions should be very close (within floating-point tolerance)
        # We use 0.5 tolerance to account for small timing differences between
        # fast-forward simulation (fixed 60fps) and real-time (variable fps)
        tolerance = 0.5

        assert abs(positions_slow['panX'] - positions_fast['panX']) < tolerance, \
            f"panX positions differ: {positions_slow['panX']} vs {positions_fast['panX']}"  # $REQ_REPLAY_008
        assert abs(positions_slow['panY'] - positions_fast['panY']) < tolerance, \
            f"panY positions differ: {positions_slow['panY']} vs {positions_fast['panY']}"  # $REQ_REPLAY_008
        assert abs(positions_slow['rotX'] - positions_fast['rotX']) < tolerance, \
            f"rotX positions differ: {positions_slow['rotX']} vs {positions_fast['rotX']}"  # $REQ_REPLAY_008

        # Velocities should be identical (they're integers)
        assert positions_slow['panXVel'] == positions_fast['panXVel'], \
            f"panX velocities differ: {positions_slow['panXVel']} vs {positions_fast['panXVel']}"  # $REQ_REPLAY_008
        assert positions_slow['panYVel'] == positions_fast['panYVel'], \
            f"panY velocities differ: {positions_slow['panYVel']} vs {positions_fast['panYVel']}"  # $REQ_REPLAY_008
        assert positions_slow['rotXVel'] == positions_fast['rotXVel'], \
            f"rotX velocities differ: {positions_slow['rotXVel']} vs {positions_fast['rotXVel']}"  # $REQ_REPLAY_008

        page5a.close()
        page5b.close()
        browser.close()

    print("✓ All deterministic replay tests passed")

if __name__ == '__main__':
    test_deterministic_replay()
