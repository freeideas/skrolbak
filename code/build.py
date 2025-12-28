#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
import os
import shutil

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def main():
    print("Building Skrolbak: Animated Background Component...")

    # Determine paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    release_dir = os.path.join(project_root, 'released', 'skrolbak')

    # Create release directory
    print(f"Creating release directory: {release_dir}")
    os.makedirs(release_dir, exist_ok=True)

    # Files to copy
    files = [
        'animated-background.js',
        'index.html',
        'bg.jpg'
    ]

    # Copy each file
    for filename in files:
        src = os.path.join(script_dir, filename)
        dst = os.path.join(release_dir, filename)

        if not os.path.exists(src):
            print(f"✗ Error: Source file not found: {src}")
            return 1

        print(f"Copying {filename}...")
        shutil.copy2(src, dst)
        print(f"  ✓ {filename} -> released/skrolbak/")

    print("\n✓ Build complete!")
    print(f"  Output: {release_dir}")
    print(f"  Files: {', '.join(files)}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
