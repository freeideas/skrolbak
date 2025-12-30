# Run via: ./bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Test Fix Loop

This script handles test preparation and test generation/verification:
- Test Preparation (cleanup orphans, prepare directories)
- Test Verification Loop (parallel-loop.py)

Can be run standalone or called from software-construction.py.

Exit codes:
  0 - Success (all stages complete)
  1 - Error
"""

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import subprocess
import platform
import time
import importlib.util
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


# Import run-script utility
_run_script_spec = importlib.util.spec_from_file_location("run_script", SCRIPT_DIR / "run-script.py")
run_script_module = importlib.util.module_from_spec(_run_script_spec)
_run_script_spec.loader.exec_module(run_script_module)
run_script = run_script_module.run_script

# Import helper scripts
def import_script(script_name: str):
    script_path = SCRIPT_DIR / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name.replace('-', '_'), script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


update_req_index = import_script('update-req-index')
find_orphan_reqIDs = import_script('find-orphan-reqIDs')
prompt_ai = import_script('prompt-ai')


def get_uv_binary() -> str:
    """Get platform-appropriate uv binary path."""
    bin_dir = SCRIPT_DIR.parent / 'bin'
    system = platform.system()

    if system == 'Windows':
        uv_path = bin_dir / 'uv.exe'
    elif system == 'Darwin':
        uv_path = bin_dir / 'uv.mac'
    else:  # Linux and others
        uv_path = bin_dir / 'uv.linux'

    if uv_path.exists():
        return str(uv_path)

    # Fall back to PATH
    return 'uv'


def print_section(title: str):
    """Print section header."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)
    print()


def run_ai_prompt(prompt_path: Path, report_type: str, timeout=600, extra_context: str | None = None):
    """Run AI prompt and return result."""
    print(f"  Running prompt: {prompt_path.name}")
    prompt_text = Path(prompt_path).read_text(encoding='utf-8')

    if extra_context:
        prompt_text = f"{prompt_text.rstrip()}\n\n---\n\n## Context\n\n{extra_context.strip()}\n"

    # Inject standard template vars
    prompt_text = prompt_text.replace('{{UV_BINARY}}', get_uv_binary())

    return prompt_ai.get_ai_response_text(
        prompt_text,
        report_type=report_type,
        timeout=timeout
    )


def kill_orphan_processes():
    """
    Kill any orphaned processes running executables from ./released/

    This is a safety net for tests that fail to cleanup properly.
    Prevents DLL/file locking issues on Windows.

    Tests should use atexit.register() to cleanup their own processes,
    but this catches cases where they don't.
    """
    released_dir = Path('./released')
    if not released_dir.exists():
        print("  No ./released/ directory; skipping orphan process cleanup")
        return

    print("  Checking for orphaned processes from ./released/...")

    try:
        killed_any = False

        if platform.system() == 'Windows':
            # Find all .exe files in released/
            executables = [f.name for f in released_dir.rglob('*.exe')]

            for exe_name in executables:
                result = subprocess.run(
                    ['taskkill', '/F', '/IM', exe_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    print(f"  OK Killed orphaned {exe_name} processes")
                    killed_any = True
                # Silently ignore "not found" errors

            if killed_any:
                # Give Windows time to released file handles
                time.sleep(1)
            else:
                print("  OK No orphaned processes found")

        else:
            # On Unix-like systems, find executable files
            executables = []
            for f in released_dir.rglob('*'):
                if f.is_file() and os.access(f, os.X_OK):
                    executables.append(f.name)

            for exe_name in executables:
                result = subprocess.run(
                    ['pkill', '-9', '-f', exe_name],
                    capture_output=True,
                    timeout=5
                )

                if result.returncode == 0:
                    print(f"  OK Killed orphaned {exe_name} processes")
                    killed_any = True
                # pkill returns 1 when no processes found -- silently ignore

            if killed_any:
                time.sleep(0.5)
            else:
                print("  OK No orphaned processes found")

    except subprocess.TimeoutExpired:
        print("  Warning: Process cleanup timed out", file=sys.stderr)
    except FileNotFoundError:
        print("  Warning: Process cleanup tool not found (taskkill/pkill)", file=sys.stderr)
    except Exception as e:
        print(f"  Warning: Process cleanup failed: {e}", file=sys.stderr)


# ============================================================================
# TEST PREPARATION
# ============================================================================

# Import report_utils for test directory helpers
report_utils = import_script('report-utils')


def prepare_tests() -> bool:
    """Prepare test directories and clean up orphans."""
    print_section("TEST PREPARATION")

    print("Preparing test directories...")
    tests_dir = Path('./tests')
    tests_dir.mkdir(parents=True, exist_ok=True)

    # Migrate flat tests to failing/ subdirectory (one-time migration)
    migrated = report_utils.migrate_flat_tests(tests_dir)
    if migrated > 0:
        print(f"  Migrated {migrated} tests from flat structure to failing/")

    # Ensure all status subdirectories exist
    report_utils.ensure_test_directories(tests_dir)
    print("  OK Directories ready: ./tests/failing/, ./tests/passing/")
    print()

    print("Checking for orphan $REQ_IDs...")
    print("  Building requirements index...")
    try:
        update_req_index.main()
    except SystemExit:
        pass

    print("  Finding orphan $REQ_IDs...")
    orphans = find_orphan_reqIDs.find_orphans()
    if orphans:
        print(f"  Found {len(orphans)} orphan $REQ_IDs, running REMOVE_ORPHAN_REQS prompt...")
        orphan_lines = ["Orphan $REQ_IDs to remove:"]
        for req_id in sorted(orphans.keys()):
            orphan_lines.append(f"  {req_id}:")
            for filespec, line_num, category in orphans[req_id]:
                orphan_lines.append(f"    - {filespec}:{line_num} ({category})")
        orphan_summary = "\n".join(orphan_lines)
        print(orphan_summary)
        prompt_path = SCRIPT_DIR.parent / 'prompts' / 'REMOVE_ORPHAN_REQS.md'
        if prompt_path.exists():
            try:
                run_ai_prompt(
                    prompt_path,
                    report_type='remove_orphan_reqs',
                    timeout=600,
                    extra_context=orphan_summary
                )
                print("  OK AI removed orphan $REQ_IDs")
            except Exception as e:
                print(f"  Warning: Error removing orphans: {e}", file=sys.stderr)
        else:
            print(f"  Warning: Prompt not found: {prompt_path}")
            print("  Skipping orphan removal")
    else:
        print("  OK No orphan $REQ_IDs found")
    print()

    print("Cleaning orphan tests...")
    req_stems = {p.stem for p in Path('./reqs').glob('*.md')}

    # Clean orphan tests from ALL status directories (failing, passing)
    if tests_dir.exists():
        for status in report_utils.TEST_STATUSES:
            status_dir = tests_dir / status
            if status_dir.exists():
                for test_file in list(status_dir.glob('*.py')):
                    stem = test_file.stem
                    if stem not in req_stems:
                        test_file.unlink()
                        print(f"  Deleted orphan test (no matching req): {status}/{test_file.name}")

    print("  OK Tests prepared")
    print()

    kill_orphan_processes()
    print()

    return True


# ============================================================================
# TEST VERIFICATION LOOP
# ============================================================================

def verify_and_fix_tests() -> int:
    """
    Run parallel-loop.py for test verification and fixing.

    Returns:
        0 - Success
        1 - Error
    """
    print_section("TEST VERIFICATION AND FIXING")

    # Delegate to the parallel loop, which handles 00_BUILD-REQ first and
    # runs remaining requirements concurrently in isolated sandboxes.
    parallel_loop_script = SCRIPT_DIR / 'parallel-loop.py'
    result = run_script(parallel_loop_script, timeout=21600, stream=True)  # 6 hours
    return result['exit_code']


# ============================================================================
# MAIN
# ============================================================================

def run_test_fix_loop() -> int:
    """
    Run test preparation and test verification loop.

    Returns exit code:
        0 - Success
        1 - Error
    """
    if not prepare_tests():
        print()
        print("FAIL Test preparation failed")
        return 1

    exit_code = verify_and_fix_tests()

    if exit_code != 0:
        print()
        print("=" * 70)
        print("FAIL TEST GENERATION FAILED")
        print("=" * 70)
        print()

    return exit_code


def main():
    """Main entry point for standalone execution."""
    print()
    print("=" * 70)
    print("TEST FIX LOOP")
    print("=" * 70)
    print()
    print("This will run:")
    print("  - Test Preparation (cleanup orphans, prepare directories)")
    print("  - Test Verification Loop (parallel execution)")
    print()

    # Change to project root (two levels up from this script)
    project_root = SCRIPT_DIR.parent.parent
    os.chdir(project_root)
    print(f"Working directory: {Path.cwd()}")
    print()

    exit_code = run_test_fix_loop()

    if exit_code == 0:
        print()
        print("=" * 70)
        print("OK TEST FIX LOOP COMPLETE")
        print("=" * 70)
        print()

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
