#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Test for Build Output Requirements (reqs/00_build-output.md)
"""

import sys
import subprocess
import shutil
from pathlib import Path


def main():
    """Test build output requirements"""

    # Get project root (tests/failing -> tests -> project root)
    test_file = Path(__file__).resolve()
    project_root = test_file.parent.parent.parent

    # Clean up any existing build output
    output_dir = project_root / 'released' / 'skrolbak'
    if output_dir.exists():
        shutil.rmtree(output_dir)

    # Run the build script
    build_script = project_root / 'code' / 'build.py'
    result = subprocess.run(
        [sys.executable, str(build_script)],
        cwd=project_root,
        capture_output=True,
        text=True,
        encoding='utf-8'
    )

    if result.returncode != 0:
        print(f"Build failed with exit code {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        sys.exit(97)  # Build failed

    # Build Output Location
    # Running ./code/build.py copies source files to ./released/skrolbak/
    assert output_dir.exists(), f"Output directory not created: {output_dir}"
    assert output_dir.is_dir(), f"Output path exists but is not a directory: {output_dir}"

    # JavaScript Component Output
    # The build output includes animated-background.js
    js_file = output_dir / 'animated-background.js'
    assert js_file.exists(), f"animated-background.js not found in output: {js_file}"
    assert js_file.is_file(), f"animated-background.js exists but is not a file: {js_file}"

    # Verify the file has content
    js_content = js_file.read_text(encoding='utf-8')
    assert len(js_content) > 0, "animated-background.js is empty"

    print("✓ All build output requirements verified successfully")
    return 0


if __name__ == '__main__':
    sys.exit(main())
