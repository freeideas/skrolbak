#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
import os
import shutil
from pathlib import Path

# $REQ_BUILD_001: Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def main():
    """Build script to copy source files and demo image to ./released/ directory."""

    print("Starting Skrolbak build...")

    # Define paths
    project_root = Path(__file__).parent.parent
    code_dir = project_root / "code"
    extart_dir = project_root / "extart"
    released_dir = project_root / "released"

    # Create released directory if it doesn't exist
    released_dir.mkdir(exist_ok=True)
    print(f"✓ Created/verified release directory: {released_dir}")

    # Define files to copy
    files_to_copy = [
        (code_dir / "index.html", released_dir / "index.html"),
        (code_dir / "animated-background.js", released_dir / "animated-background.js"),
        (extart_dir / "bg.jpg", released_dir / "bg.jpg"),
    ]

    # Copy each file
    for src, dst in files_to_copy:
        if not src.exists():
            print(f"✗ ERROR: Source file not found: {src}")
            return 1

        shutil.copy2(src, dst)
        print(f"✓ Copied {src.name} to {dst}")

    # Verify all required files exist in released directory
    required_files = ["index.html", "animated-background.js", "bg.jpg"]
    for filename in required_files:
        filepath = released_dir / filename
        if not filepath.exists():
            print(f"✗ ERROR: Required file missing in release: {filename}")
            return 1

    print(f"\n✓ Build successful! All files copied to {released_dir}")
    print("\nRelease contents:")
    for filename in required_files:
        filepath = released_dir / filename
        size = filepath.stat().st_size
        print(f"  - {filename} ({size:,} bytes)")

    return 0

if __name__ == "__main__":
    sys.exit(main())
