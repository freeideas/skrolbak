#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["playwright"]
# ///

"""
Test for testing methodology requirements.
Tests the <drift-bg> component using Playwright screenshots and AI-based verification.
"""

import subprocess
import sys
import time
import re
import atexit
from pathlib import Path

# Ensure tmp directory exists
Path('./tmp').mkdir(exist_ok=True)

# Import web server helpers
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'ai-coder' / 'scripts'))
from websrvr import start_server, get_server_url, stop_server

# Start HTTP server for testing
port = start_server('./released')
url = get_server_url(port)

# Import Playwright
from playwright.sync_api import sync_playwright

# Global playwright instance for cleanup
_playwright = None
_browser = None

def cleanup():
    """Cleanup playwright resources."""
    global _browser, _playwright
    if _browser:
        try:
            _browser.close()
        except:
            pass
    if _playwright:
        try:
            _playwright.stop()
        except:
            pass
    stop_server()

atexit.register(cleanup)

# Start playwright
_playwright = sync_playwright().start()
_browser = _playwright.chromium.launch()
page = _browser.new_page()

# List to store console messages
console_messages = []

# Capture console output and errors
def handle_console(msg):
    console_messages.append(msg.text)

def handle_error(msg):
    print(f"[BROWSER ERROR] {msg}")

page.on('console', handle_console)
page.on('pageerror', handle_error)

print("Testing methodology requirements...")

# $REQ_TESTMETH_001: Screenshots via Playwright
# $REQ_TESTMETH_002: Screenshots Saved to tmp Directory
# $REQ_TESTMETH_003: AI-Based Visual Verification
# $REQ_TESTMETH_004: No Byte-Level Screenshot Comparison
# $REQ_TESTMETH_006: Visual Movement Test Process
print("\n[Test 1] Visual Movement Test")
print("Loading page...")
page.goto(url, wait_until='networkidle')
print("Waiting for component to initialize...")
time.sleep(2)  # Give component time to initialize

print("Taking first screenshot...")
page.screenshot(path='./tmp/screenshot_a.png')  # $REQ_TESTMETH_001, $REQ_TESTMETH_002

print("Waiting 5 seconds for animation...")
time.sleep(5)  # $REQ_TESTMETH_006: Wait 5 seconds

print("Taking second screenshot...")
page.screenshot(path='./tmp/screenshot_b.png')  # $REQ_TESTMETH_001, $REQ_TESTMETH_002

print("Verifying background has moved using visual-test.py...")
# $REQ_TESTMETH_003: Use visual-test.py for AI-based verification
# $REQ_TESTMETH_004: Never use byte-level comparison
result = subprocess.run([
    sys.executable,
    './ai-coder/scripts/visual-test.py',
    './tmp/screenshot_a.png',
    './tmp/screenshot_b.png',
    'The background has visibly moved or changed position between the two screenshots',
    '--test-script', __file__
], encoding='utf-8')

assert result.returncode == 0, "Visual movement test failed - background did not move"  # $REQ_TESTMETH_006
print("✓ Visual movement test passed")

# $REQ_TESTMETH_005: Console Log Format
# $REQ_TESTMETH_007: State Change Test Process
print("\n[Test 2] State Change Test")
print("Reloading page for state change test...")
console_messages.clear()
page.goto(url, wait_until='networkidle')
time.sleep(1)  # Give component time to initialize

print("Waiting for at least 2 console log lines...")
# Wait for at least 2 log lines (at least 2 seconds since logs happen once per second)
timeout = time.time() + 10
drift_bg_logs = []
while len(drift_bg_logs) < 2 and time.time() < timeout:
    # Filter for drift-bg messages
    drift_bg_logs = [msg for msg in console_messages if msg.startswith('drift-bg:')]
    time.sleep(0.5)

assert len(drift_bg_logs) >= 2, f"Expected at least 2 console log lines, got {len(drift_bg_logs)}"

print(f"Got {len(drift_bg_logs)} log lines")
print(f"Log 1: {drift_bg_logs[0]}")
print(f"Log 2: {drift_bg_logs[1]}")

# $REQ_TESTMETH_005: Parse log format: drift-bg: x=<value> y=<value> z=<value> u=<value> v=<value> w=<value>
# Note: The actual format includes [MODE] prefix
pattern = r'drift-bg:\s+\[(?:MOUSE|SPIRAL)\]\s+x=([-\d.]+)\s+y=([-\d.]+)\s+z=([-\d.]+)\s+u=([-\d.]+)\s+v=([-\d.]+)\s+w=([-\d.]+)'

match1 = re.search(pattern, drift_bg_logs[0])
match2 = re.search(pattern, drift_bg_logs[1])

assert match1, f"First log line does not match expected format: {drift_bg_logs[0]}"  # $REQ_TESTMETH_005
assert match2, f"Second log line does not match expected format: {drift_bg_logs[1]}"  # $REQ_TESTMETH_005

# Extract values
state1 = {
    'x': float(match1.group(1)),
    'y': float(match1.group(2)),
    'z': float(match1.group(3)),
    'u': float(match1.group(4)),
    'v': float(match1.group(5)),
    'w': float(match1.group(6))
}

state2 = {
    'x': float(match2.group(1)),
    'y': float(match2.group(2)),
    'z': float(match2.group(3)),
    'u': float(match2.group(4)),
    'v': float(match2.group(5)),
    'w': float(match2.group(6))
}

print(f"State 1: {state1}")
print(f"State 2: {state2}")

# $REQ_TESTMETH_007: Verify every variable has a different value between the two log lines
for var in ['x', 'y', 'z', 'u', 'v', 'w']:
    assert state1[var] != state2[var], f"Variable {var} did not change: {state1[var]} == {state2[var]}"  # $REQ_TESTMETH_007

print("✓ State change test passed - all variables changed")

# $REQ_TESTMETH_008: Mouse Interaction Test Process
print("\n[Test 3] Mouse Interaction Test")
print("Reloading page for mouse interaction test...")
console_messages.clear()
page.goto(url, wait_until='networkidle')
time.sleep(1)  # Give component time to initialize

print("Waiting for SPIRAL mode log...")
# Wait for at least one log line with [SPIRAL] mode
timeout = time.time() + 10
spiral_found = False
while not spiral_found and time.time() < timeout:
    for msg in console_messages:
        if msg.startswith('drift-bg:') and '[SPIRAL' in msg:  # $REQ_TESTMETH_008
            spiral_found = True
            print(f"Found SPIRAL mode: {msg}")
            break
    time.sleep(0.5)

assert spiral_found, "Did not find SPIRAL mode in console logs"  # $REQ_TESTMETH_008

print("Moving mouse within canvas...")
# Record current message count before mouse move
messages_before = len(console_messages)
print(f"Messages before mouse move: {messages_before}")

# Trigger a mousemove event and wait for the next console log  # $REQ_TESTMETH_008
# Use Playwright's mouse.move() to move the mouse to the canvas center
# Get canvas position
canvas_rect = page.evaluate("""() => {
    const driftBg = document.querySelector('drift-bg');
    const canvas = driftBg.querySelector('canvas');
    const rect = canvas.getBoundingClientRect();
    return {
        x: rect.left,
        y: rect.top,
        width: rect.width,
        height: rect.height
    };
}""")

# Move mouse to center of canvas
mouse_x = canvas_rect['x'] + canvas_rect['width'] * 0.5
mouse_y = canvas_rect['y'] + canvas_rect['height'] * 0.5

print(f"Moving mouse to ({mouse_x}, {mouse_y})")
page.mouse.move(mouse_x, mouse_y)

# Give the browser time to process the event and run animation frames
# The animation loop logs once per second, so we need to wait at least 1 second
# for the next log that reflects the mouse event
print("Waiting for browser to process event and run animation cycles...")
# Give browser time to process and run animation cycles (logs happen once per second)
time.sleep(2.0)

# Trigger a page interaction to ensure animation frames continue processing
# (Playwright may pause animation frames without this)
page.evaluate("() => { /* ensure animation frames continue */ }")

print("Checking for MOUSE mode in drift-bg logs...")

# Wait for at least one drift-bg log that contains [MOUSE] mode
# Logs happen once per second, so we need to wait for the next log cycle
timeout = time.time() + 10.0
mouse_mode_found = False

while not mouse_mode_found and time.time() < timeout:
    # Check all drift-bg logs for [MOUSE] mode
    for msg in console_messages:
        if msg.startswith('drift-bg:') and '[MOUSE' in msg:
            mouse_mode_found = True
            print(f"Found MOUSE mode: {msg}")
            break

    if not mouse_mode_found:
        time.sleep(0.2)

assert mouse_mode_found, "Console logs did not show [MOUSE] mode after mouse move"  # $REQ_TESTMETH_008
print("✓ Mouse interaction test passed")

print("\n" + "="*60)
print("All tests passed!")
print("="*60)

sys.exit(0)
