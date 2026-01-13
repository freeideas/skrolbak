# Run via: ./ai-coder/bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Sequential Test/Code Loop

Processes requirements one at a time until all tests pass.

Exit codes:
  0 - Success (all tests pass)
  1 - Error
"""

import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import signal
import importlib.util
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent
MAX_ITERATIONS = 10
MAX_FIX_ATTEMPTS = 5
BUILD_REQ_STEM = '00_build-output'


def import_script(script_name: str):
    script_path = SCRIPT_DIR / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name.replace('-', '_'), script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run_script_module = import_script('run-script')
run_script = run_script_module.run_script

report_utils = import_script('report-utils')

# Global tracking for summary report
_run_state = {
    'started_at': None,
    'iteration': 0,
    'max_iterations': MAX_ITERATIONS,
    'exit_reason': None,
    'req_results': {},  # req_stem -> {'status': str, 'attempts': int}
    'all_reqs': [],  # All requirement stems found
}


def write_summary_report(exit_code: int):
    """Write a summary report of the loop run."""
    report_path, timestamp = report_utils.get_report_path('LOOP_SUMMARY')

    # Calculate duration
    started = _run_state.get('started_at')
    if started:
        duration = datetime.now() - started
        duration_str = str(duration).split('.')[0]  # Remove microseconds
    else:
        duration_str = 'N/A'

    # Build the table of requirements
    all_reqs = _run_state.get('all_reqs', [])
    req_results = _run_state.get('req_results', {})

    # Build requirement status table
    req_rows = []
    for req_stem in sorted(all_reqs):
        result = req_results.get(req_stem, {})
        status = result.get('status', 'NOT_STARTED')
        attempts = result.get('attempts', 0)

        if status == 'PASS':
            status_icon = '✓'
        elif status == 'EXT_DEP_FAIL':
            status_icon = '⚠'
        elif status == 'FAIL':
            status_icon = '✗'
        else:
            status_icon = '-'

        # Find test location
        test_path, test_loc = report_utils.find_test_in_any_status(req_stem)
        if test_loc:
            test_location = f"{test_loc}/"
        else:
            test_location = "-"

        req_rows.append(f"| {req_stem} | {status_icon} {status} | {attempts} | {test_location} |")

    req_table = '\n'.join(req_rows) if req_rows else '| (no requirements found) | - | - | - |'

    exit_reason = _run_state.get('exit_reason', 'UNKNOWN')

    report_content = f"""# Loop Summary

**Timestamp:** {timestamp}
**Duration:** {duration_str}
**Exit Code:** {exit_code}
**Exit Reason:** {exit_reason}
**Iteration:** {_run_state.get('iteration', 0)} / {_run_state.get('max_iterations', MAX_ITERATIONS)}

## Requirements Status

| Requirement | Status | Attempts | Test Location |
|-------------|--------|----------|---------------|
{req_table}"""

    report_path.write_text(report_content, encoding='utf-8')
    print(f"\nSummary report: {report_path}")


def _signal_handler(signum, frame):
    """Handle interrupt signals gracefully."""
    sig_name = signal.Signals(signum).name if hasattr(signal, 'Signals') else str(signum)
    print(f"\n\nReceived {sig_name}, writing summary report...")
    _run_state['exit_reason'] = f'INTERRUPTED ({sig_name})'
    write_summary_report(130)  # 128 + signal number for SIGINT
    sys.exit(130)


def get_reqs_needing_work() -> list[Path]:
    """Find requirement files whose tests don't pass.

    If the build requirement (00_build-output) fails, returns only that requirement.
    This ensures the build is fixed before checking other tests, which may
    depend on build artifacts.

    Simple rule: if a test is not in passing/, the requirement needs work.
    """
    reqs_dir = Path('./reqs')
    if not reqs_dir.exists():
        return []

    req_files = sorted(reqs_dir.glob('*.md'))

    def needs_work(req_file: Path) -> bool:
        """Check if a requirement's test currently fails."""
        test_path, status = report_utils.find_test_in_any_status(req_file.stem)

        # If no test exists, needs work
        if test_path is None:
            return True

        # If test is in passing/, don't queue it
        if status == 'passing':
            return False

        # Test is in failing/, needs work
        return True

    # Check build requirement FIRST - if it fails, only return that
    for req_file in req_files:
        if req_file.stem.lower() == BUILD_REQ_STEM:
            if needs_work(req_file):
                print(f"  Build requirement failed - fixing that first")
                return [req_file]
            break  # Build passed, continue checking others

    # Build passed (or doesn't exist) - check remaining tests
    reqs_needing_work = []
    for req_file in req_files:
        if req_file.stem.lower() == BUILD_REQ_STEM:
            continue  # Already checked
        if needs_work(req_file):
            reqs_needing_work.append(req_file)

    return reqs_needing_work


def run_all_tests() -> bool:
    """Run quick-test.py and return True if all tests pass."""
    quick_test_script = SCRIPT_DIR / 'quick-test.py'
    result = run_script(quick_test_script, timeout=3600, stream=True)
    return result['exit_code'] == 0


def process_requirement(req_file: Path) -> int:
    """
    Process a single requirement using agent-worker.py.
    Returns exit code from agent.
    """
    agent_script = SCRIPT_DIR / 'agent-worker.py'

    result = run_script(
        agent_script,
        args=[str(req_file)],
        timeout=1800,  # 30 minutes per requirement
        stream=True
    )

    return result['exit_code']


def run_integration_check() -> bool:
    """
    Run integration check (all tests in passing/).

    Builds the project first (so ./released/ exists), then runs quick-test.py.
    quick-test.py automatically moves any failing tests to failing/.

    Returns True if all tests pass, False if any failed.
    """
    # Build first so tests have access to compiled artifacts in ./released/
    build_script = Path('./code/build.py')
    if build_script.exists():
        print("Building before integration check...")
        print()
        build_result = run_script(build_script, timeout=600, stream=True)
        if build_result['exit_code'] != 0:
            print(f"Build failed (exit {build_result['exit_code']})")
            return False
        print()

    print("Running integration check...")
    print()
    return run_all_tests()


def main() -> int:
    """
    Main loop for sequential test/code fixing.

    Simple strategy: keep iterating while tests are failing
    - Each iteration: find tests that fail, fix them one at a time
    - Exit when: all tests pass OR max iterations reached
    """
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # Track start time
    _run_state['started_at'] = datetime.now()

    print()
    print("=" * 70)
    print("SEQUENTIAL TEST/CODE LOOP")
    print("=" * 70)
    print()

    # Ensure we're in project root
    project_root = SCRIPT_DIR.parent.parent
    os.chdir(project_root)
    print(f"Working directory: {Path.cwd()}")

    # Discover all requirements and track them
    reqs_dir = Path('./reqs')
    if reqs_dir.exists():
        _run_state['all_reqs'] = [f.stem for f in sorted(reqs_dir.glob('*.md'))]

    # Ensure tests directories exist (failing/, passing/)
    report_utils.ensure_test_directories(Path('./tests'))

    # Ensure tmp directory exists
    Path('./tmp').mkdir(exist_ok=True)

    # Update req index before starting
    try:
        update_req_index = import_script('update-req-index')
        update_req_index.main()
    except Exception as e:
        print(f"  Warning: Failed to update req index: {e}")

    for iteration in range(1, MAX_ITERATIONS + 1):
        _run_state['iteration'] = iteration

        print()
        print(f"--- Iteration {iteration}/{MAX_ITERATIONS} ---")
        print()

        # Find requirements with failing tests
        reqs_needing_work = get_reqs_needing_work()

        if not reqs_needing_work:
            # All tests are in passing/ - verify they actually pass
            print("All tests in passing/ - running integration check...")
            print()
            if run_integration_check():
                # All tests actually pass - success!
                print()
                print("=" * 70)
                print("OK LOOP COMPLETE - ALL TESTS PASS")
                print("=" * 70)
                _run_state['exit_reason'] = 'SUCCESS - All tests pass'
                write_summary_report(0)
                return 0
            else:
                # Some tests failed - they've been moved to failing/
                # Continue to next iteration to fix them
                print()
                print("Some tests failed integration check - continuing to fix...")
                continue

        print(f"Requirements needing work: {len(reqs_needing_work)}")
        for req in reqs_needing_work:
            print(f"  - {req.name}")
        print()

        # Process each requirement sequentially
        for req_file in reqs_needing_work:
            req_stem = req_file.stem
            print(f"Processing: {req_file.name}")
            print()

            exit_code = process_requirement(req_file)

            # Track result
            current = _run_state['req_results'].get(req_stem, {'attempts': 0})
            _run_state['req_results'][req_stem] = {
                'status': 'PASS' if exit_code == 0 else ('EXT_DEP_FAIL' if exit_code == 99 else 'FAIL'),
                'attempts': current['attempts'] + 1
            }

            if exit_code == 0:
                print(f"  ✓ {req_file.name} - PASS")
            elif exit_code == 99:
                print(f"  ⚠ {req_file.name} - External dependency issue (treating as code bug)")
            else:
                print(f"  ✗ {req_file.name} - FAIL")

            print()

        # Update req index after processing
        try:
            update_req_index.main()
        except Exception as e:
            print(f"  Warning: Failed to update req index: {e}")

    # Final check - last iteration may have fixed everything
    if not get_reqs_needing_work() and run_integration_check():
        print()
        print("=" * 70)
        print("OK LOOP COMPLETE - ALL TESTS PASS")
        print("=" * 70)
        _run_state['exit_reason'] = 'SUCCESS - All tests pass'
        write_summary_report(0)
        return 0

    print()
    print("=" * 70)
    print("FAIL - UNABLE TO FIX ALL TESTS")
    print("=" * 70)
    _run_state['exit_reason'] = 'FAILURE - Max iterations reached'
    write_summary_report(1)
    return 1


if __name__ == '__main__':
    sys.exit(main())
