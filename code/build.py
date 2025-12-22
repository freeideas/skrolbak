#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
import os
import subprocess
import shutil
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# $REQ_BUILD_001: Build script paths
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent
FLUTTER_BIN = PROJECT_ROOT / "tools" / "compiler" / "flutter" / "bin" / "flutter"
ASSETS_DIR = PROJECT_ROOT / "extart"
CODE_ASSETS_DIR = SCRIPT_DIR / "assets"
RELEASED_DIR = PROJECT_ROOT / "released"

def print_step(message):
    """Print a build step message"""
    print(f"• {message}")

def run_command(cmd, cwd=None):
    """Run a command and return exit code"""
    result = subprocess.run(
        cmd,
        cwd=cwd or SCRIPT_DIR,
        text=True,
        encoding='utf-8',
        capture_output=True
    )
    if result.stdout:
        print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, end='', file=sys.stderr)
    return result.returncode

def main():
    print_step("Starting build process...")

    # $REQ_BUILD_002: Copy background image to assets directory
    print_step("Copying assets...")
    CODE_ASSETS_DIR.mkdir(exist_ok=True)
    bg_source = ASSETS_DIR / "bg.jpg"
    bg_dest = CODE_ASSETS_DIR / "bg.jpg"

    if not bg_source.exists():
        print(f"✗ Error: Background image not found at {bg_source}", file=sys.stderr)
        return 1

    shutil.copy2(bg_source, bg_dest)
    print(f"  Copied {bg_source} → {bg_dest}")

    # Run flutter pub get
    print_step("Getting Flutter dependencies...")
    ret = run_command([str(FLUTTER_BIN), "pub", "get"])
    if ret != 0:
        print("✗ Failed to get dependencies", file=sys.stderr)
        return ret

    # Build for web
    print_step("Building Flutter web app...")
    ret = run_command([
        str(FLUTTER_BIN),
        "build",
        "web",
        "--release",
        "--web-renderer",
        "canvaskit"
    ])
    if ret != 0:
        print("✗ Build failed", file=sys.stderr)
        return ret

    # Copy build output to ./released/
    print_step("Copying artifacts to ./released/...")
    build_output = SCRIPT_DIR / "build" / "web"

    if not build_output.exists():
        print(f"✗ Error: Build output not found at {build_output}", file=sys.stderr)
        return 1

    # Clean and recreate released directory
    if RELEASED_DIR.exists():
        shutil.rmtree(RELEASED_DIR)
    RELEASED_DIR.mkdir(parents=True)

    # Copy all web build files
    shutil.copytree(build_output, RELEASED_DIR, dirs_exist_ok=True)
    print(f"  Copied {build_output} → {RELEASED_DIR}")

    print_step("✓ Build completed successfully!")
    print(f"\nArtifacts available in: {RELEASED_DIR}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
