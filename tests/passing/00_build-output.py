#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Test for build output requirements.
Tests that the build produces exactly the required files in ./released/
"""

import sys
from pathlib import Path

def main():
    """Test that ./released/ contains exactly the required files."""

    # Assume CWD is project root
    released_dir = Path("./released")

    # Verify directory exists
    if not released_dir.exists():
        print(f"FAIL: ./released/ directory does not exist")
        return 1

    if not released_dir.is_dir():
        print(f"FAIL: ./released/ exists but is not a directory")
        return 1

    # $REQ_BUILD_001: Check for exact file set
    required_files = {"index.html", "animated-background.js", "bg.jpg"}

    # Get actual files in directory
    actual_files = {f.name for f in released_dir.iterdir() if f.is_file()}

    # Check for missing files
    missing = required_files - actual_files
    if missing:
        print(f"FAIL: Missing required files: {missing}")
        return 1

    # Check for extra files
    extra = actual_files - required_files
    if extra:
        print(f"FAIL: Extra files found (must have exactly 3 files): {extra}")
        return 1

    # Verify exact count
    assert len(actual_files) == 3, f"Expected exactly 3 files, found {len(actual_files)}"  # $REQ_BUILD_001

    # Verify each required file exists
    assert (released_dir / "index.html").is_file()  # $REQ_BUILD_001
    assert (released_dir / "animated-background.js").is_file()  # $REQ_BUILD_001
    assert (released_dir / "bg.jpg").is_file()  # $REQ_BUILD_001

    print("PASS: ./released/ contains exactly the required 3 files:")
    for filename in sorted(required_files):
        filepath = released_dir / filename
        size = filepath.stat().st_size
        print(f"  ✓ {filename} ({size:,} bytes)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
