#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["playwright"]
# ///

"""
Test for Element Attributes requirement (reqs/01_element-attributes.md)
Tests the `src`, `t`, and six range attributes of the <animated-background> element.
"""

import sys
import time
import re
from pathlib import Path

# Add the-system/scripts to path for websrvr
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'the-system' / 'scripts'))

from playwright.sync_api import sync_playwright
from websrvr import start_server, get_server_url, stop_server


def test_element_attributes():
    """Test all element attributes requirements"""

    port = start_server('./released')
    url = get_server_url(port)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            # Test $REQ_ATTR_001: src Attribute Specifies Background Image
            print("Testing $REQ_ATTR_001: src attribute specifies background image...")
            page.set_content(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="{url}/skrolbak/animated-background.js"></script>
                </head>
                <body>
                    <animated-background id="test1" src="test-image.jpg"></animated-background>
                </body>
                </html>
            ''')
            time.sleep(0.1)  # Wait for element to initialize

            # Check that src attribute is used for background image
            bg_image = page.evaluate('''
                document.querySelector('#test1 > div').style.backgroundImage
            ''')
            assert 'test-image.jpg' in bg_image, f"Expected src to be used in background-image, got: {bg_image}"  # $REQ_ATTR_001

            # Check that background is tiled
            bg_repeat = page.evaluate('''
                document.querySelector('#test1 > div').style.backgroundRepeat
            ''')
            assert bg_repeat == 'repeat', f"Expected background to repeat, got: {bg_repeat}"  # $REQ_ATTR_001

            # Check that background is centered
            bg_position = page.evaluate('''
                document.querySelector('#test1 > div').style.backgroundPosition
            ''')
            assert 'center' in bg_position, f"Expected background to be centered, got: {bg_position}"  # $REQ_ATTR_001

            # Test $REQ_ATTR_002: t Attribute Default Value
            print("Testing $REQ_ATTR_002: t attribute default value is 0...")
            page.set_content(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="{url}/skrolbak/animated-background.js"></script>
                </head>
                <body>
                    <animated-background id="test2" src="test.jpg"></animated-background>
                </body>
                </html>
            ''')
            time.sleep(0.1)

            # Check that t defaults to 0
            t_value = page.evaluate('document.querySelector("#test2")._t')
            assert t_value == 0, f"Expected t to default to 0, got: {t_value}"  # $REQ_ATTR_002

            # Test $REQ_ATTR_003: t Attribute Fast-Forward Behavior
            print("Testing $REQ_ATTR_003: t attribute fast-forward behavior...")
            console_messages = []
            page.on('console', lambda msg: console_messages.append(msg.text))

            page.set_content(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="{url}/skrolbak/animated-background.js"></script>
                </head>
                <body>
                    <animated-background id="test3" src="test.jpg" t="5" pan-x="100"></animated-background>
                </body>
                </html>
            ''')
            time.sleep(0.2)

            # Check that element starts at t=5 without logging 0-4
            assert any('t=5' in msg for msg in console_messages), f"Expected console log 't=5', got: {console_messages}"  # $REQ_ATTR_003
            assert not any('t=0' in msg for msg in console_messages), f"Should not log t=0 during fast-forward"  # $REQ_ATTR_003
            assert not any('t=1' in msg for msg in console_messages), f"Should not log t=1 during fast-forward"  # $REQ_ATTR_003

            # Check that state was simulated
            t_value = page.evaluate('document.querySelector("#test3")._t')
            assert t_value == 5, f"Expected t to be 5 after fast-forward, got: {t_value}"  # $REQ_ATTR_003

            # Test $REQ_ATTR_004: Range Attributes Are Optional With Default Zero
            print("Testing $REQ_ATTR_004: range attributes default to 0...")
            page.set_content(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="{url}/skrolbak/animated-background.js"></script>
                </head>
                <body>
                    <animated-background id="test4" src="test.jpg"></animated-background>
                </body>
                </html>
            ''')
            time.sleep(0.1)

            # Check all six range attributes default to 0
            ranges = page.evaluate('''
                ({
                    panX: document.querySelector("#test4")._state.panX.range,
                    panY: document.querySelector("#test4")._state.panY.range,
                    panZ: document.querySelector("#test4")._state.panZ.range,
                    rotX: document.querySelector("#test4")._state.rotX.range,
                    rotY: document.querySelector("#test4")._state.rotY.range,
                    rotZ: document.querySelector("#test4")._state.rotZ.range
                })
            ''')
            assert ranges['panX'] == 0, f"Expected pan-x to default to 0, got: {ranges['panX']}"  # $REQ_ATTR_004
            assert ranges['panY'] == 0, f"Expected pan-y to default to 0, got: {ranges['panY']}"  # $REQ_ATTR_004
            assert ranges['panZ'] == 0, f"Expected pan-z to default to 0, got: {ranges['panZ']}"  # $REQ_ATTR_004
            assert ranges['rotX'] == 0, f"Expected rot-x to default to 0, got: {ranges['rotX']}"  # $REQ_ATTR_004
            assert ranges['rotY'] == 0, f"Expected rot-y to default to 0, got: {ranges['rotY']}"  # $REQ_ATTR_004
            assert ranges['rotZ'] == 0, f"Expected rot-z to default to 0, got: {ranges['rotZ']}"  # $REQ_ATTR_004

            # Test $REQ_ATTR_006: rot-x Rotation Range Mapping
            print("Testing $REQ_ATTR_006: rot-x rotation range mapping...")
            page.set_content(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="{url}/skrolbak/animated-background.js"></script>
                </head>
                <body>
                    <animated-background id="test6" src="test.jpg" rot-x="100"></animated-background>
                </body>
                </html>
            ''')
            time.sleep(0.1)

            # Check that rot-x range is set correctly
            rot_x_range = page.evaluate('document.querySelector("#test6")._state.rotX.range')
            assert rot_x_range == 100, f"Expected rot-x range to be 100, got: {rot_x_range}"  # $REQ_ATTR_006

            # Set position to maximum and check rotation calculation
            # Position at +50 should give +45° rotation
            page.evaluate('document.querySelector("#test6")._state.rotX.position = 50')
            page.evaluate('document.querySelector("#test6")._applyTransform()')
            transform = page.evaluate('document.querySelector("#test6 > div").style.transform')
            match = re.search(r'rotateX\(([-\d.]+)deg\)', transform)
            assert match, f"Expected rotateX in transform, got: {transform}"  # $REQ_ATTR_006
            rot_x_value = float(match.group(1))
            assert abs(rot_x_value - 45) < 0.1, f"Expected rotateX close to 45deg at position +50, got: {rot_x_value}deg"  # $REQ_ATTR_006

            # Test $REQ_ATTR_007: rot-y Rotation Range Mapping
            print("Testing $REQ_ATTR_007: rot-y rotation range mapping...")
            page.set_content(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="{url}/skrolbak/animated-background.js"></script>
                </head>
                <body>
                    <animated-background id="test7" src="test.jpg" rot-y="50"></animated-background>
                </body>
                </html>
            ''')
            time.sleep(0.1)

            rot_y_range = page.evaluate('document.querySelector("#test7")._state.rotY.range')
            assert rot_y_range == 50, f"Expected rot-y range to be 50, got: {rot_y_range}"  # $REQ_ATTR_007

            # At 50% range, position +25 (half of +50) should give +22.5° rotation
            page.evaluate('document.querySelector("#test7")._state.rotY.position = 25')
            page.evaluate('document.querySelector("#test7")._applyTransform()')
            transform = page.evaluate('document.querySelector("#test7 > div").style.transform')
            match = re.search(r'rotateY\(([-\d.]+)deg\)', transform)
            assert match, f"Expected rotateY in transform, got: {transform}"  # $REQ_ATTR_007
            rot_y_value = float(match.group(1))
            assert abs(rot_y_value - 22.5) < 0.1, f"Expected rotateY close to 22.5deg at position +25, got: {rot_y_value}deg"  # $REQ_ATTR_007

            # Test $REQ_ATTR_008: rot-z Rotation Range Mapping
            print("Testing $REQ_ATTR_008: rot-z rotation range mapping...")
            page.set_content(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="{url}/skrolbak/animated-background.js"></script>
                </head>
                <body>
                    <animated-background id="test8" src="test.jpg" rot-z="100"></animated-background>
                </body>
                </html>
            ''')
            time.sleep(0.1)

            rot_z_range = page.evaluate('document.querySelector("#test8")._state.rotZ.range')
            assert rot_z_range == 100, f"Expected rot-z range to be 100, got: {rot_z_range}"  # $REQ_ATTR_008

            # Position at -50 should give -45° rotation (with tolerance for floating point)
            page.evaluate('document.querySelector("#test8")._state.rotZ.position = -50')
            page.evaluate('document.querySelector("#test8")._applyTransform()')
            transform = page.evaluate('document.querySelector("#test8 > div").style.transform')
            # Extract rotation value and check it's close to -45
            match = re.search(r'rotateZ\(([-\d.]+)deg\)', transform)
            assert match, f"Expected rotateZ in transform, got: {transform}"  # $REQ_ATTR_008
            rot_z_value = float(match.group(1))
            assert abs(rot_z_value - (-45)) < 0.1, f"Expected rotateZ close to -45deg at position -50, got: {rot_z_value}deg"  # $REQ_ATTR_008

            # Test $REQ_ATTR_009: pan-x Translation Range Mapping
            print("Testing $REQ_ATTR_009: pan-x translation range mapping...")
            page.set_content(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="{url}/skrolbak/animated-background.js"></script>
                </head>
                <body>
                    <animated-background id="test9" src="test.jpg" pan-x="100"></animated-background>
                </body>
                </html>
            ''')
            time.sleep(0.1)

            pan_x_range = page.evaluate('document.querySelector("#test9")._state.panX.range')
            assert pan_x_range == 100, f"Expected pan-x range to be 100, got: {pan_x_range}"  # $REQ_ATTR_009

            # At 100% range, the wall should be able to pan across the full viewport
            # Position at +50 should move the wall significantly
            page.evaluate('document.querySelector("#test9")._state.panX.position = 50')
            page.evaluate('document.querySelector("#test9")._applyTransform()')
            transform = page.evaluate('document.querySelector("#test9 > div").style.transform')
            # Should contain a positive X translation
            assert 'translate(' in transform, f"Expected translation in transform, got: {transform}"  # $REQ_ATTR_009

            # Test $REQ_ATTR_010: pan-y Translation Range Mapping
            print("Testing $REQ_ATTR_010: pan-y translation range mapping...")
            page.set_content(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="{url}/skrolbak/animated-background.js"></script>
                </head>
                <body>
                    <animated-background id="test10" src="test.jpg" pan-y="100"></animated-background>
                </body>
                </html>
            ''')
            time.sleep(0.1)

            pan_y_range = page.evaluate('document.querySelector("#test10")._state.panY.range')
            assert pan_y_range == 100, f"Expected pan-y range to be 100, got: {pan_y_range}"  # $REQ_ATTR_010

            # Test $REQ_ATTR_011: pan-z Zoom Range Mapping
            print("Testing $REQ_ATTR_011: pan-z zoom range mapping...")
            page.set_content(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="{url}/skrolbak/animated-background.js"></script>
                </head>
                <body>
                    <animated-background id="test11" src="test.jpg" pan-z="100"></animated-background>
                </body>
                </html>
            ''')
            time.sleep(0.1)

            pan_z_range = page.evaluate('document.querySelector("#test11")._state.panZ.range')
            assert pan_z_range == 100, f"Expected pan-z range to be 100, got: {pan_z_range}"  # $REQ_ATTR_011

            # At position 0, scale should be 1.0 (nominal)
            page.evaluate('document.querySelector("#test11")._state.panZ.position = 0')
            page.evaluate('document.querySelector("#test11")._applyTransform()')
            transform = page.evaluate('document.querySelector("#test11 > div").style.transform')
            # Extract scale value and check it's close to 1.0
            match = re.search(r'scale\(([\d.]+)\)', transform)
            assert match, f"Expected scale in transform, got: {transform}"  # $REQ_ATTR_011
            scale_value = float(match.group(1))
            assert abs(scale_value - 1.0) < 0.01, f"Expected scale close to 1.0 at position 0, got: {scale_value}"  # $REQ_ATTR_011

            # At position +50, scale should be 1.5 (150%)
            page.evaluate('document.querySelector("#test11")._state.panZ.position = 50')
            page.evaluate('document.querySelector("#test11")._applyTransform()')
            transform = page.evaluate('document.querySelector("#test11 > div").style.transform')
            match = re.search(r'scale\(([\d.]+)\)', transform)
            assert match, f"Expected scale in transform, got: {transform}"  # $REQ_ATTR_011
            scale_value = float(match.group(1))
            assert abs(scale_value - 1.5) < 0.01, f"Expected scale close to 1.5 at position +50, got: {scale_value}"  # $REQ_ATTR_011

            # At position -50, scale should be 0.5 (50%)
            page.evaluate('document.querySelector("#test11")._state.panZ.position = -50')
            page.evaluate('document.querySelector("#test11")._applyTransform()')
            transform = page.evaluate('document.querySelector("#test11 > div").style.transform')
            match = re.search(r'scale\(([\d.]+)\)', transform)
            assert match, f"Expected scale in transform, got: {transform}"  # $REQ_ATTR_011
            scale_value = float(match.group(1))
            assert abs(scale_value - 0.5) < 0.01, f"Expected scale close to 0.5 at position -50, got: {scale_value}"  # $REQ_ATTR_011

            # Test $REQ_ATTR_012: Zero Range Means No Motion
            print("Testing $REQ_ATTR_012: zero range means no motion...")
            page.set_content(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="{url}/skrolbak/animated-background.js"></script>
                </head>
                <body>
                    <animated-background id="test12" src="test.jpg" pan-x="0" pan-y="0"></animated-background>
                </body>
                </html>
            ''')
            time.sleep(0.1)

            # Check that velocity is 0 for axes with range = 0
            velocities = page.evaluate('''
                ({
                    panX: document.querySelector("#test12")._state.panX.velocity,
                    panY: document.querySelector("#test12")._state.panY.velocity
                })
            ''')
            assert velocities['panX'] == 0, f"Expected pan-x velocity to be 0, got: {velocities['panX']}"  # $REQ_ATTR_012
            assert velocities['panY'] == 0, f"Expected pan-y velocity to be 0, got: {velocities['panY']}"  # $REQ_ATTR_012

            # Test $REQ_ATTR_013: Attribute Parsing and Clamping
            print("Testing $REQ_ATTR_013: attribute parsing and clamping...")
            page.set_content(f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <script src="{url}/skrolbak/animated-background.js"></script>
                </head>
                <body>
                    <animated-background id="test13" src="test.jpg"
                        pan-x="150" pan-y="-10" pan-z="50.5" rot-x="invalid"></animated-background>
                </body>
                </html>
            ''')
            time.sleep(0.1)

            # Check clamping to [0, 100]
            ranges = page.evaluate('''
                ({
                    panX: document.querySelector("#test13")._state.panX.range,
                    panY: document.querySelector("#test13")._state.panY.range,
                    panZ: document.querySelector("#test13")._state.panZ.range,
                    rotX: document.querySelector("#test13")._state.rotX.range
                })
            ''')
            assert ranges['panX'] == 100, f"Expected pan-x to be clamped to 100, got: {ranges['panX']}"  # $REQ_ATTR_013
            assert ranges['panY'] == 0, f"Expected pan-y to be clamped to 0, got: {ranges['panY']}"  # $REQ_ATTR_013
            assert ranges['panZ'] == 50.5, f"Expected pan-z to parse as 50.5, got: {ranges['panZ']}"  # $REQ_ATTR_013
            assert ranges['rotX'] == 0, f"Expected rot-x to default to 0 on invalid parse, got: {ranges['rotX']}"  # $REQ_ATTR_013

            browser.close()

    finally:
        stop_server()

    print("\n✓ All element attribute tests passed!")


if __name__ == '__main__':
    try:
        test_element_attributes()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Test error: {e}", file=sys.stderr)
        sys.exit(1)
