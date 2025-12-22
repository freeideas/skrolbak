#!/usr/bin/env python3
"""
Test for build output requirements.
Tests $REQ_BUILD_001 and $REQ_BUILD_002.
"""

import sys
import subprocess
from pathlib import Path

# Assume CWD is project root
PROJECT_ROOT = Path.cwd()
RELEASED_DIR = PROJECT_ROOT / "released"
BUILD_SCRIPT = PROJECT_ROOT / "code" / "build.py"
UV_BIN = PROJECT_ROOT / "the-system" / "bin" / "uv.linux"


def main():
    print("Testing build output requirements...")

    # First, run the build if released directory doesn't exist or is empty
    if not RELEASED_DIR.exists() or not list(RELEASED_DIR.iterdir()):
        print("\n• Running build process...")
        result = subprocess.run(
            [str(UV_BIN), "run", "--script", str(BUILD_SCRIPT)],
            cwd=PROJECT_ROOT,
            text=True,
            encoding='utf-8',
            capture_output=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.returncode != 0:
            print(f"✗ Build failed with exit code {result.returncode}", file=sys.stderr)
            sys.exit(97)  # Build failed

    # $REQ_BUILD_001: Build output MUST appear in the ./released/ directory
    print("\n• Checking $REQ_BUILD_001: Build output location...")
    assert RELEASED_DIR.exists(), f"Released directory does not exist at {RELEASED_DIR}"  # $REQ_BUILD_001
    assert RELEASED_DIR.is_dir(), f"Released path is not a directory: {RELEASED_DIR}"  # $REQ_BUILD_001

    # Check that the directory is not empty
    files = list(RELEASED_DIR.iterdir())
    assert len(files) > 0, f"Released directory is empty: {RELEASED_DIR}"  # $REQ_BUILD_001
    print(f"  ✓ Build output exists in {RELEASED_DIR}")
    print(f"  ✓ Contains {len(files)} files/directories")

    # $REQ_BUILD_002: The project MUST be built as a Flutter web app
    print("\n• Checking $REQ_BUILD_002: Flutter web app output...")

    # Check for Flutter web app artifacts
    index_html = RELEASED_DIR / "index.html"
    assert index_html.exists(), f"index.html not found in {RELEASED_DIR}"  # $REQ_BUILD_002

    # Check for Flutter-specific files/directories
    flutter_js = RELEASED_DIR / "flutter.js"
    flutter_service_worker = RELEASED_DIR / "flutter_service_worker.js"
    canvaskit_dir = RELEASED_DIR / "canvaskit"

    # At least one of these should exist for a Flutter web build
    has_flutter_artifact = (
        flutter_js.exists() or
        flutter_service_worker.exists() or
        canvaskit_dir.exists()
    )
    assert has_flutter_artifact, "No Flutter web artifacts found (flutter.js, flutter_service_worker.js, or canvaskit/)"  # $REQ_BUILD_002

    # Verify index.html contains Flutter references
    index_content = index_html.read_text(encoding='utf-8')
    assert 'flutter' in index_content.lower(), "index.html does not reference Flutter"  # $REQ_BUILD_002

    print(f"  ✓ index.html exists")
    if flutter_js.exists():
        print(f"  ✓ flutter.js exists")
    if flutter_service_worker.exists():
        print(f"  ✓ flutter_service_worker.js exists")
    if canvaskit_dir.exists():
        print(f"  ✓ canvaskit/ directory exists")
    print(f"  ✓ index.html references Flutter")

    print("\n✓ All build output requirements verified!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
