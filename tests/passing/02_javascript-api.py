#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["playwright"]
# ///

"""
Test for JavaScript API requirement (reqs/02_javascript-api.md)
Tests attribute accessors, position accessors, and velocity accessors.
"""

import sys
import os
import time
import subprocess
import atexit
from pathlib import Path

# Get repository root (2 levels up from tests/failing/)
REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Add the-system/scripts to path for imports
sys.path.insert(0, str(REPO_ROOT / 'the-system' / 'scripts'))

from websrvr import start_server, stop_server, get_server_url

# Ensure build is run before tests
build_script = REPO_ROOT / 'code' / 'build.py'
result = subprocess.run(
    [str(REPO_ROOT / 'the-system' / 'bin' / 'uv.linux'), 'run', '--script', str(build_script)],
    cwd=str(REPO_ROOT),
    capture_output=True,
    text=True,
    encoding='utf-8'
)
if result.returncode != 0:
    print(f"Build failed:\n{result.stdout}\n{result.stderr}", file=sys.stderr)
    sys.exit(97)

# Start web server
port = start_server(str(REPO_ROOT / 'released'))
base_url = get_server_url(port)

# Ensure cleanup on exit
atexit.register(stop_server)

# Import playwright after dependencies are available
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed. Run: uv run playwright install", file=sys.stderr)
    sys.exit(99)

def test_javascript_api():
    """Test all JavaScript API requirements"""

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Create a test page with the animated-background element
        test_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>JavaScript API Test</title>
        </head>
        <body>
            <animated-background id="bg"
                src="{base_url}/skrolbak/demo-background.png"
                pan-x="50"
                pan-y="30"
                pan-z="20"
                rot-x="40"
                rot-y="60"
                rot-z="10">
            </animated-background>
            <script src="{base_url}/skrolbak/animated-background.js"></script>
        </body>
        </html>
        """

        page.set_content(test_html)

        # Wait for element to be ready
        page.wait_for_selector('animated-background')
        time.sleep(0.1)  # Allow initialization

        # Get the element
        bg = page.query_selector('#bg')

        # $REQ_JSAPI_001: Attribute Accessors for Range Attributes
        # Test getter for range attributes
        assert page.evaluate('document.getElementById("bg").panX') == 50  # $REQ_JSAPI_001
        assert page.evaluate('document.getElementById("bg").panY') == 30  # $REQ_JSAPI_001
        assert page.evaluate('document.getElementById("bg").panZ') == 20  # $REQ_JSAPI_001
        assert page.evaluate('document.getElementById("bg").rotX') == 40  # $REQ_JSAPI_001
        assert page.evaluate('document.getElementById("bg").rotY') == 60  # $REQ_JSAPI_001
        assert page.evaluate('document.getElementById("bg").rotZ') == 10  # $REQ_JSAPI_001

        # Test setter for range attributes
        page.evaluate('document.getElementById("bg").panX = 75')  # $REQ_JSAPI_001
        assert page.evaluate('document.getElementById("bg").panX') == 75  # $REQ_JSAPI_001
        assert page.evaluate('document.getElementById("bg").getAttribute("pan-x")') == '75'  # $REQ_JSAPI_001

        page.evaluate('document.getElementById("bg").rotY = 85')  # $REQ_JSAPI_001
        assert page.evaluate('document.getElementById("bg").rotY') == 85  # $REQ_JSAPI_001

        # Test clamping (0-100)
        page.evaluate('document.getElementById("bg").panZ = 150')  # $REQ_JSAPI_001
        assert page.evaluate('document.getElementById("bg").panZ') == 100  # $REQ_JSAPI_001

        page.evaluate('document.getElementById("bg").rotX = -10')  # $REQ_JSAPI_001
        assert page.evaluate('document.getElementById("bg").rotX') == 0  # $REQ_JSAPI_001

        # $REQ_JSAPI_002: Attribute Accessor for src
        # Test getter
        src_value = page.evaluate('document.getElementById("bg").src')
        assert 'demo-background.png' in src_value  # $REQ_JSAPI_002

        # Test setter
        new_src = f"{base_url}/skrolbak/demo-background.png"
        page.evaluate(f'document.getElementById("bg").src = "{new_src}"')  # $REQ_JSAPI_002
        assert page.evaluate('document.getElementById("bg").src') == new_src  # $REQ_JSAPI_002
        assert page.evaluate('document.getElementById("bg").getAttribute("src")') == new_src  # $REQ_JSAPI_002

        # $REQ_JSAPI_003: Position Accessors
        # Test getters exist and return numbers
        pan_x_pos = page.evaluate('document.getElementById("bg").panXPosition')  # $REQ_JSAPI_003
        assert isinstance(pan_x_pos, (int, float))  # $REQ_JSAPI_003

        pan_y_pos = page.evaluate('document.getElementById("bg").panYPosition')  # $REQ_JSAPI_003
        assert isinstance(pan_y_pos, (int, float))  # $REQ_JSAPI_003

        pan_z_pos = page.evaluate('document.getElementById("bg").panZPosition')  # $REQ_JSAPI_003
        assert isinstance(pan_z_pos, (int, float))  # $REQ_JSAPI_003

        rot_x_pos = page.evaluate('document.getElementById("bg").rotXPosition')  # $REQ_JSAPI_003
        assert isinstance(rot_x_pos, (int, float))  # $REQ_JSAPI_003

        rot_y_pos = page.evaluate('document.getElementById("bg").rotYPosition')  # $REQ_JSAPI_003
        assert isinstance(rot_y_pos, (int, float))  # $REQ_JSAPI_003

        rot_z_pos = page.evaluate('document.getElementById("bg").rotZPosition')  # $REQ_JSAPI_003
        assert isinstance(rot_z_pos, (int, float))  # $REQ_JSAPI_003

        # $REQ_JSAPI_004: Position Value Semantics
        # Test setters work and values are within expected range
        # Stop animation by setting all velocities to 0
        page.evaluate('''
            const bg = document.getElementById("bg");
            bg.panXVelocity = 0;
            bg.panYVelocity = 0;
            bg.panZVelocity = 0;
            bg.rotXVelocity = 0;
            bg.rotYVelocity = 0;
            bg.rotZVelocity = 0;
        ''')

        page.evaluate('document.getElementById("bg").panXPosition = 0')  # $REQ_JSAPI_004
        pos = page.evaluate('document.getElementById("bg").panXPosition')
        assert abs(pos - 0) < 0.01  # $REQ_JSAPI_004

        page.evaluate('document.getElementById("bg").panYPosition = 25')  # $REQ_JSAPI_004
        pos = page.evaluate('document.getElementById("bg").panYPosition')
        assert abs(pos - 25) < 0.01  # $REQ_JSAPI_004

        page.evaluate('document.getElementById("bg").panZPosition = -25')  # $REQ_JSAPI_004
        pos = page.evaluate('document.getElementById("bg").panZPosition')
        assert abs(pos - (-25)) < 0.01  # $REQ_JSAPI_004

        # Test boundary values (-50% to +50%)
        page.evaluate('document.getElementById("bg").rotXPosition = -50')  # $REQ_JSAPI_004
        pos = page.evaluate('document.getElementById("bg").rotXPosition')
        assert abs(pos - (-50)) < 0.01  # $REQ_JSAPI_004

        page.evaluate('document.getElementById("bg").rotYPosition = 50')  # $REQ_JSAPI_004
        pos = page.evaluate('document.getElementById("bg").rotYPosition')
        assert abs(pos - 50) < 0.01  # $REQ_JSAPI_004

        # $REQ_JSAPI_005: Position Setter Allows Full Range
        # Create element with limited range, but position setter should allow full -50 to +50
        page.set_content(f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"></head>
        <body>
            <animated-background id="bg2"
                src="{base_url}/skrolbak/demo-background.png"
                pan-x="30">
            </animated-background>
            <script src="{base_url}/skrolbak/animated-background.js"></script>
        </body>
        </html>
        """)
        page.wait_for_selector('animated-background')
        time.sleep(0.1)

        # Stop animation by setting all velocities to 0
        page.evaluate('''
            const bg = document.getElementById("bg2");
            bg.panXVelocity = 0;
            bg.panYVelocity = 0;
            bg.panZVelocity = 0;
            bg.rotXVelocity = 0;
            bg.rotYVelocity = 0;
            bg.rotZVelocity = 0;
        ''')

        # With pan-x="30", normal range is -15% to +15% (30% of full range)
        # But position setter should allow full -50% to +50%
        page.evaluate('document.getElementById("bg2").panXPosition = 40')  # $REQ_JSAPI_005
        pos = page.evaluate('document.getElementById("bg2").panXPosition')
        assert abs(pos - 40) < 0.01  # $REQ_JSAPI_005

        page.evaluate('document.getElementById("bg2").panXPosition = -45')  # $REQ_JSAPI_005
        pos = page.evaluate('document.getElementById("bg2").panXPosition')
        assert abs(pos - (-45)) < 0.01  # $REQ_JSAPI_005

        # Test clamping at absolute boundaries
        page.evaluate('document.getElementById("bg2").panXPosition = 60')  # $REQ_JSAPI_005
        pos = page.evaluate('document.getElementById("bg2").panXPosition')
        assert abs(pos - 50) < 0.01  # $REQ_JSAPI_005

        page.evaluate('document.getElementById("bg2").panXPosition = -60')  # $REQ_JSAPI_005
        pos = page.evaluate('document.getElementById("bg2").panXPosition')
        assert abs(pos - (-50)) < 0.01  # $REQ_JSAPI_005

        # $REQ_JSAPI_006: Velocity Accessors
        # Test getters exist and return numbers
        pan_x_vel = page.evaluate('document.getElementById("bg2").panXVelocity')  # $REQ_JSAPI_006
        assert isinstance(pan_x_vel, (int, float))  # $REQ_JSAPI_006

        pan_y_vel = page.evaluate('document.getElementById("bg2").panYVelocity')  # $REQ_JSAPI_006
        assert isinstance(pan_y_vel, (int, float))  # $REQ_JSAPI_006

        pan_z_vel = page.evaluate('document.getElementById("bg2").panZVelocity')  # $REQ_JSAPI_006
        assert isinstance(pan_z_vel, (int, float))  # $REQ_JSAPI_006

        rot_x_vel = page.evaluate('document.getElementById("bg2").rotXVelocity')  # $REQ_JSAPI_006
        assert isinstance(rot_x_vel, (int, float))  # $REQ_JSAPI_006

        rot_y_vel = page.evaluate('document.getElementById("bg2").rotYVelocity')  # $REQ_JSAPI_006
        assert isinstance(rot_y_vel, (int, float))  # $REQ_JSAPI_006

        rot_z_vel = page.evaluate('document.getElementById("bg2").rotZVelocity')  # $REQ_JSAPI_006
        assert isinstance(rot_z_vel, (int, float))  # $REQ_JSAPI_006

        # Test setters work
        page.evaluate('document.getElementById("bg2").panXVelocity = 5.5')  # $REQ_JSAPI_006
        vel = page.evaluate('document.getElementById("bg2").panXVelocity')
        assert abs(vel - 5.5) < 0.01  # $REQ_JSAPI_006

        page.evaluate('document.getElementById("bg2").rotYVelocity = -3.2')  # $REQ_JSAPI_006
        vel = page.evaluate('document.getElementById("bg2").rotYVelocity')
        assert abs(vel - (-3.2)) < 0.01  # $REQ_JSAPI_006

        # $REQ_JSAPI_007: Boost Accessors
        # Test getters exist and return numbers
        pan_x_boost = page.evaluate('document.getElementById("bg2").panXBoost')  # $REQ_JSAPI_007
        assert isinstance(pan_x_boost, (int, float))  # $REQ_JSAPI_007

        pan_y_boost = page.evaluate('document.getElementById("bg2").panYBoost')  # $REQ_JSAPI_007
        assert isinstance(pan_y_boost, (int, float))  # $REQ_JSAPI_007

        pan_z_boost = page.evaluate('document.getElementById("bg2").panZBoost')  # $REQ_JSAPI_007
        assert isinstance(pan_z_boost, (int, float))  # $REQ_JSAPI_007

        rot_x_boost = page.evaluate('document.getElementById("bg2").rotXBoost')  # $REQ_JSAPI_007
        assert isinstance(rot_x_boost, (int, float))  # $REQ_JSAPI_007

        rot_y_boost = page.evaluate('document.getElementById("bg2").rotYBoost')  # $REQ_JSAPI_007
        assert isinstance(rot_y_boost, (int, float))  # $REQ_JSAPI_007

        rot_z_boost = page.evaluate('document.getElementById("bg2").rotZBoost')  # $REQ_JSAPI_007
        assert isinstance(rot_z_boost, (int, float))  # $REQ_JSAPI_007

        # $REQ_JSAPI_008: Boost Value Semantics
        # Default to 0
        boost = page.evaluate('document.getElementById("bg2").panXBoost')
        assert abs(boost - 0) < 0.01  # $REQ_JSAPI_008
        boost = page.evaluate('document.getElementById("bg2").rotZBoost')
        assert abs(boost - 0) < 0.01  # $REQ_JSAPI_008

        # Test setters work with positive and negative values
        page.evaluate('document.getElementById("bg2").panXBoost = 10.5')  # $REQ_JSAPI_008
        boost = page.evaluate('document.getElementById("bg2").panXBoost')
        assert abs(boost - 10.5) < 0.01  # $REQ_JSAPI_008

        page.evaluate('document.getElementById("bg2").panYBoost = -7.3')  # $REQ_JSAPI_008
        boost = page.evaluate('document.getElementById("bg2").panYBoost')
        assert abs(boost - (-7.3)) < 0.01  # $REQ_JSAPI_008

        page.evaluate('document.getElementById("bg2").rotXBoost = 100')  # $REQ_JSAPI_008
        boost = page.evaluate('document.getElementById("bg2").rotXBoost')
        assert abs(boost - 100) < 0.01  # $REQ_JSAPI_008

        page.evaluate('document.getElementById("bg2").rotYBoost = -200')  # $REQ_JSAPI_008
        boost = page.evaluate('document.getElementById("bg2").rotYBoost')
        assert abs(boost - (-200)) < 0.01  # $REQ_JSAPI_008

        browser.close()

    print("✓ All JavaScript API tests passed")

if __name__ == '__main__':
    try:
        test_javascript_api()
        sys.exit(0)
    except AssertionError as e:
        print(f"✗ Test failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
