#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Test for login form requirements.
Tests visual appearance and structure of the glassmorphic login form.
"""

import sys
import os
import subprocess
import time
import atexit
from pathlib import Path

# Add the-system/scripts to path for utilities
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'the-system' / 'scripts'))

try:
    from websrvr import start_server, get_server_url, stop_server
except ImportError:
    print("Error: Cannot import websrvr utilities")
    sys.exit(2)

# Cleanup handler
_procs = []

def cleanup():
    """Kill any spawned processes."""
    for p in _procs:
        try:
            p.terminate()
            p.wait(timeout=2)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    stop_server()

atexit.register(cleanup)


def run_visual_test(image_path: str, description: str) -> bool:
    """Run visual-test.py script and return True if match."""
    script_path = Path(__file__).resolve().parent.parent.parent / 'the-system' / 'scripts' / 'visual-test.py'
    uv_path = Path(__file__).resolve().parent.parent.parent / 'the-system' / 'bin' / 'uv.linux'

    result = subprocess.run(
        [str(uv_path), 'run', '--script', str(script_path), image_path, description],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    return result.returncode == 0


def take_screenshot(url: str, output_path: str, viewport_width: int = 1024, viewport_height: int = 768):
    """Take a screenshot of the given URL using playwright."""
    script_content = f'''#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = ["playwright"]
# ///

from playwright.sync_api import sync_playwright
import sys

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={{"width": {viewport_width}, "height": {viewport_height}}})
    page.goto("{url}")
    page.wait_for_timeout(2000)  # Wait for animations
    page.screenshot(path="{output_path}")
    browser.close()
'''

    # Create temp script
    tmp_dir = Path(__file__).resolve().parent.parent.parent / 'tmp'
    tmp_dir.mkdir(exist_ok=True)
    script_path = tmp_dir / 'screenshot.py'

    with open(script_path, 'w') as f:
        f.write(script_content)

    # Run script
    uv_path = Path(__file__).resolve().parent.parent.parent / 'the-system' / 'bin' / 'uv.linux'
    result = subprocess.run(
        [str(uv_path), 'run', '--script', str(script_path)],
        capture_output=True,
        text=True,
        encoding='utf-8',
        timeout=30
    )

    if result.returncode != 0:
        print(f"Screenshot failed: {result.stderr}")
        return False

    return True


def main():
    """Main test function."""

    # Check if build exists
    build_path = Path(__file__).resolve().parent.parent.parent / 'code' / 'build' / 'web'
    if not build_path.exists():
        print("Error: Build not found at code/build/web")
        sys.exit(97)

    # Start web server
    print("Starting web server...")
    try:
        port = start_server(str(build_path))
        url = get_server_url(port)
        print(f"Server started at {url}")
    except Exception as e:
        print(f"Failed to start server: {e}")
        sys.exit(99)

    # Give server time to start
    time.sleep(1)

    # Create tmp directory for screenshots
    tmp_dir = Path(__file__).resolve().parent.parent.parent / 'tmp'
    tmp_dir.mkdir(exist_ok=True)

    # Test at standard viewport
    screenshot_path = str(tmp_dir / 'login-form-1024x768.png')
    print(f"Taking screenshot at 1024x768...")
    if not take_screenshot(url, screenshot_path, 1024, 768):
        print("Failed to take screenshot")
        sys.exit(1)

    print("Running visual tests...")

    # Combined test for overall form appearance and structure
    # Tests REQ_LOGIN_FORM_001-009 in one comprehensive visual check
    print("Testing comprehensive form appearance...")
    comprehensive_description = """
    A login form that is:
    - Centered both horizontally and vertically in the viewport
    - Approximately 400 pixels wide
    - Has a semi-transparent purple/lavender background with glassmorphic frosted blur effect
    - Has rounded corners and subtle styling
    - Has a soft drop shadow
    - Contains a 'Login' heading at the top
    - Contains an 'Email' field label with 'you@example.com' placeholder text
    - Contains an unchecked 'Stay logged in' checkbox
    - Contains a full-width pink 'Continue' button
    """
    assert run_visual_test(
        screenshot_path,
        comprehensive_description
    ), "Form does not match comprehensive requirements"
    # $REQ_LOGIN_FORM_001, $REQ_LOGIN_FORM_002, $REQ_LOGIN_FORM_003
    # $REQ_LOGIN_FORM_004, $REQ_LOGIN_FORM_005, $REQ_LOGIN_FORM_006
    # $REQ_LOGIN_FORM_007, $REQ_LOGIN_FORM_008, $REQ_LOGIN_FORM_009

    # $REQ_LOGIN_FORM_010: Display Only
    # Since this is a Flutter Canvas app, we verify through code inspection
    # that the button handlers are empty (no navigation, HTTP requests, or form submission)
    print("Testing $REQ_LOGIN_FORM_010: Form does not submit...")
    main_dart_path = Path(__file__).resolve().parent.parent.parent / 'code' / 'lib' / 'main.dart'

    with open(main_dart_path, 'r') as f:
        main_dart_content = f.read()

    # Verify the onPressed handler for the Continue button is empty (display only)
    import re

    # Find the ElevatedButton's onPressed handler
    # It should be empty or only contain a comment
    onPressed_pattern = r'ElevatedButton\s*\(\s*onPressed:\s*\(\)\s*\{[^}]*\}'
    matches = re.findall(onPressed_pattern, main_dart_content, re.DOTALL)

    assert len(matches) > 0, "Could not find Continue button onPressed handler"

    # Extract the handler body (between { and })
    handler_body = matches[0].split('{', 1)[1].rsplit('}', 1)[0].strip()

    # Handler should be empty or only contain comments
    # Remove all comments and whitespace
    handler_no_comments = re.sub(r'//.*', '', handler_body)
    handler_no_comments = re.sub(r'/\*.*?\*/', '', handler_no_comments, flags=re.DOTALL)
    handler_no_comments = handler_no_comments.strip()

    assert handler_no_comments == '', f"Continue button should not have submission logic, but found: {handler_no_comments}"  # $REQ_LOGIN_FORM_010

    # $REQ_LOGIN_FORM_011: Centering at All Viewport Sizes
    print("Testing $REQ_LOGIN_FORM_011: Centering at minimum viewport (320px)...")
    screenshot_path_320 = str(tmp_dir / 'login-form-320x568.png')
    if not take_screenshot(url, screenshot_path_320, 320, 568):
        print("Failed to take screenshot at 320px width")
        sys.exit(1)

    # Simple centering check for narrow viewport
    assert run_visual_test(
        screenshot_path_320,
        "A login form centered in the viewport"
    ), "Form is not centered at 320px viewport width"  # $REQ_LOGIN_FORM_011

    # $REQ_LOGIN_FORM_012: Form Above Background
    print("Testing $REQ_LOGIN_FORM_012: Form appears above background...")
    assert run_visual_test(
        screenshot_path,
        "A login form displayed in the foreground with a visible background behind it"
    ), "Form does not appear above background"  # $REQ_LOGIN_FORM_012

    print("\n✓ All login form tests passed!")
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nTest interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
