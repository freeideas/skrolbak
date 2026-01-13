#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = ["playwright"]
# ///

"""
Test for console logging requirements (reqs/03_console-logging.md)

This test verifies:
- Console logs appear once per second ($REQ_CONSOLE_001)
- Console logs follow the expected format ($REQ_CONSOLE_002)
- Console logs include mode indicator ($REQ_CONSOLE_003)
"""

import atexit
import os
import re
import subprocess
import sys
import time
from pathlib import Path

# Add ai-coder/scripts to path for websrvr import
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'ai-coder' / 'scripts'))
from websrvr import start_server, get_server_url, stop_server

# Track processes for cleanup
_procs = []

def cleanup():
    """Clean up any running processes."""
    for p in _procs:
        try:
            p.terminate()
            p.wait(timeout=2)
        except:
            pass
    stop_server()

atexit.register(cleanup)

def main():
    # Ensure tmp directory exists
    os.makedirs('./tmp', exist_ok=True)

    # Start HTTP server
    port = start_server('./released')
    url = get_server_url(port)

    print(f"Starting test server at {url}")

    # Install Playwright browsers if needed (one-time setup)
    # This is safe to run multiple times
    try:
        subprocess.run(
            [sys.executable, '-m', 'playwright', 'install', 'chromium'],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=120
        )
    except Exception as e:
        print(f"Warning: Could not install Playwright browsers: {e}")

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Collect console messages
        console_messages = []

        def handle_console(msg):
            if msg.type == 'log':
                console_messages.append(msg.text)
                print(f"Console: {msg.text}")

        page.on('console', handle_console)

        # Navigate to the page
        page.goto(url)

        # Wait for component to initialize
        page.wait_for_timeout(500)

        # Clear initial messages and start fresh
        console_messages.clear()
        start_time = time.time()

        # Wait for at least 3 seconds to capture multiple log entries
        # We need at least 2 logs to test frequency, but wait 3s to be safe
        page.wait_for_timeout(3500)

        elapsed_time = time.time() - start_time

        # Filter only drift-bg log messages
        drift_logs = [msg for msg in console_messages if msg.startswith('drift-bg:')]

        print(f"\nCollected {len(drift_logs)} drift-bg log messages in {elapsed_time:.1f}s")
        for i, log in enumerate(drift_logs):
            print(f"  {i+1}. {log}")

        # $REQ_CONSOLE_001: Log Frequency
        # The component must log once per second
        # We waited ~3.5 seconds, so we should have at least 3 logs
        assert len(drift_logs) >= 3, \
            f"Expected at least 3 log messages in ~3.5s, got {len(drift_logs)}"  # $REQ_CONSOLE_001

        # Verify logs are approximately 1 second apart by checking we don't have too many
        # In 3.5 seconds, we should have at most 4-5 logs (allowing some timing variance)
        assert len(drift_logs) <= 5, \
            f"Too many log messages ({len(drift_logs)}) in 3.5s, expected ~3-4"  # $REQ_CONSOLE_001

        # $REQ_CONSOLE_002: Log Format
        # Console log output must follow this format:
        # drift-bg: x=12.34 y=-5.67 z=23.45 u=0.12 v=-0.08 w=0.15
        # (with mode indicator, tested separately)

        # Parse first log to verify format
        first_log = drift_logs[0]

        # Pattern: drift-bg: [MODE] x=NUMBER y=NUMBER z=NUMBER u=NUMBER v=NUMBER w=NUMBER
        pattern = r'^drift-bg: \[(SPIRAL|MOUSE)\] x=(-?\d+\.\d+) y=(-?\d+\.\d+) z=(-?\d+\.\d+) u=(-?\d+\.\d+) v=(-?\d+\.\d+) w=(-?\d+\.\d+)$'
        match = re.match(pattern, first_log)

        assert match is not None, \
            f"Log format incorrect. Expected 'drift-bg: [MODE] x=... y=... z=... u=... v=... w=...', got: {first_log}"  # $REQ_CONSOLE_002

        # Verify all logs follow the same format
        for log in drift_logs:
            match = re.match(pattern, log)
            assert match is not None, \
                f"Log format incorrect: {log}"  # $REQ_CONSOLE_002

        # $REQ_CONSOLE_003: Mode Indicator in Log
        # The console log must include a mode indicator: [SPIRAL when in Spiral Mode, or [MOUSE when in Mouse Mode

        # Initially, without mouse movement, should be in SPIRAL mode
        for log in drift_logs:
            assert '[SPIRAL]' in log or '[MOUSE]' in log, \
                f"Log missing mode indicator [SPIRAL] or [MOUSE]: {log}"  # $REQ_CONSOLE_003

        # All initial logs should show SPIRAL mode (no mouse movement yet)
        for log in drift_logs:
            assert '[SPIRAL]' in log, \
                f"Expected [SPIRAL] mode initially (no mouse movement), got: {log}"  # $REQ_CONSOLE_003

        # Now test mouse mode transition
        print("\nTesting mouse mode transition...")
        console_messages.clear()

        # Move mouse to trigger MOUSE mode
        page.mouse.move(100, 100)

        # Wait for next log message (up to 2 seconds)
        page.wait_for_timeout(2000)

        # Get new drift-bg logs
        drift_logs_after_mouse = [msg for msg in console_messages if msg.startswith('drift-bg:')]

        print(f"\nCollected {len(drift_logs_after_mouse)} log messages after mouse movement:")
        for i, log in enumerate(drift_logs_after_mouse):
            print(f"  {i+1}. {log}")

        # Should have at least one log showing MOUSE mode
        assert len(drift_logs_after_mouse) > 0, \
            "Expected at least one log message after mouse movement"  # $REQ_CONSOLE_003

        # At least one log should show MOUSE mode
        has_mouse_mode = any('[MOUSE]' in log for log in drift_logs_after_mouse)
        assert has_mouse_mode, \
            f"Expected [MOUSE] mode after mouse movement, got: {drift_logs_after_mouse}"  # $REQ_CONSOLE_003

        browser.close()

    print("\n✓ All console logging requirements verified")
    return 0

if __name__ == '__main__':
    sys.exit(main())
