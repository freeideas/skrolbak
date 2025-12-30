#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
import os
import shutil
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def main():
    print("Building Skrolbak...")

    # Get project root (parent of code/)
    code_dir = Path(__file__).parent
    project_root = code_dir.parent

    # $REQ_BUILD_001: Released Directory Contains Component Script
    released_dir = project_root / 'released' / 'skrolbak'

    # Create released directory
    print(f"Creating output directory: {released_dir}")
    released_dir.mkdir(parents=True, exist_ok=True)

    # Copy JavaScript component
    src_file = code_dir / 'animated-background.js'
    dest_file = released_dir / 'animated-background.js'
    print(f"Copying {src_file.name} to {released_dir}")
    shutil.copy2(src_file, dest_file)

    # Copy demo files
    demo_file = code_dir / 'demo.html'
    demo_dest = released_dir / 'demo.html'
    print(f"Copying {demo_file.name} to {released_dir}")
    shutil.copy2(demo_file, demo_dest)

    # Copy demo image from extart/
    extart_dir = project_root / 'extart'
    bg_src = extart_dir / 'bg.jpg'
    bg_dest = released_dir / 'bg.jpg'
    if bg_src.exists():
        print(f"Copying {bg_src.name} to {released_dir}")
        shutil.copy2(bg_src, bg_dest)
    else:
        print(f"Warning: {bg_src} not found, skipping")

    print("\nBuild completed successfully!")
    print(f"Output directory: {released_dir}")
    print("\nContents:")
    for item in sorted(released_dir.iterdir()):
        print(f"  - {item.name}")

    return 0

if __name__ == '__main__':
    sys.exit(main())
