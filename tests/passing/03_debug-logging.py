#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "selenium",
# ]
# ///

"""
Test for debug logging requirement.
Tests that the animated background component logs time offset to console every second.
"""

import sys
import time
import subprocess
import atexit
from pathlib import Path

# Add the-system to path for websrvr import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'the-system' / 'scripts'))
from websrvr import start_server, get_server_url, stop_server

# Try to import selenium
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
except ImportError:
    print("Error: selenium not available")
    sys.exit(1)

# Process cleanup
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

def main():
    # Start web server (build is already handled by test.py wrapper)
    released_dir = Path(__file__).resolve().parent.parent.parent / 'released'
    if not released_dir.exists():
        print("Error: released directory not found")
        sys.exit(1)

    port = start_server(str(released_dir))
    url = get_server_url(port) + '/logix/'

    # Set up headless Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')

    # Enable browser logging
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)

        # Navigate to the page
        driver.get(url)

        # Wait for at least 3 seconds to capture multiple log entries
        # Don't clear logs - we want to capture from t=0
        time.sleep(3.5)

        # Get console logs
        logs = driver.get_log('browser')

        # Extract console.log messages that match the t=N pattern
        time_logs = []
        for entry in logs:
            message = entry.get('message', '')
            # Look for t=N pattern in console.log messages
            if 't=' in message:
                # Extract the t=N part
                parts = message.split('"')
                for part in parts:
                    if part.startswith('t='):
                        try:
                            time_val = int(part.split('=')[1])
                            time_logs.append(time_val)
                        except (ValueError, IndexError):
                            pass

        # $REQ_DEBUG_001: Verify that time offset is logged once per second in t=N format
        assert len(time_logs) >= 3, f"Expected at least 3 time log entries, got {len(time_logs)}: {time_logs}"  # $REQ_DEBUG_001

        # Verify the logs are sequential and start from 0
        assert 0 in time_logs, f"Expected t=0 in logs, got: {time_logs}"  # $REQ_DEBUG_001

        # Verify logs are consecutive (allowing for some to be missed due to timing)
        sorted_logs = sorted(time_logs)
        assert sorted_logs[0] == 0, f"First log should be t=0, got t={sorted_logs[0]}"  # $REQ_DEBUG_001

        # Verify we have multiple consecutive logs
        for i in range(len(sorted_logs) - 1):
            diff = sorted_logs[i+1] - sorted_logs[i]
            assert diff >= 1, f"Logs should be at least 1 second apart, got {sorted_logs[i]} and {sorted_logs[i+1]}"  # $REQ_DEBUG_001

        print("✓ All tests passed")
        print(f"  - Captured {len(time_logs)} time log entries: {sorted(time_logs)}")
        return 0

    except Exception as e:
        print(f"✗ Test failed: {e}")
        return 1

    finally:
        if driver:
            driver.quit()
        cleanup()

if __name__ == '__main__':
    sys.exit(main())
