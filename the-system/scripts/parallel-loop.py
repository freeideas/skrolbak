# Run via: ./the-system/bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Parallel Test/Code Loop

Spawns one agent per requirement file. Each agent works in an isolated sandbox.
Outer loop repeats until all tests pass.

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
from concurrent.futures import ThreadPoolExecutor, as_completed

SCRIPT_DIR = Path(__file__).parent
MAX_ITERATIONS = 10
MAX_PARALLEL_AGENTS = 5
BUILD_REQ_STEM = '00_build-output'


def import_script(script_name: str):
    script_path = SCRIPT_DIR / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name.replace('-', '_'), script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run_script_module = import_script('run-script')
run_script = run_script_module.run_script

update_req_index = import_script('update-req-index')
report_utils = import_script('report-utils')

# Global tracking for summary report
_run_state = {
    'started_at': None,
    'iteration': 0,
    'max_iterations': MAX_ITERATIONS,
    'exit_reason': None,
    'agent_results': {},  # req_stem -> {'exit_code': int, 'attempts': int}
    'all_reqs': [],  # All requirement stems found
}


def write_summary_report(exit_code: int):
    """Write a summary report of the parallel loop run."""
    reports_dir = Path('./reports')
    report_path, timestamp = report_utils.get_report_path('PARALLEL_LOOP_SUMMARY')

    # Calculate duration
    started = _run_state.get('started_at')
    if started:
        duration = datetime.now() - started
        duration_str = str(duration).split('.')[0]  # Remove microseconds
    else:
        duration_str = 'N/A'

    # Build the table of requirements
    all_reqs = _run_state.get('all_reqs', [])
    agent_results = _run_state.get('agent_results', {})

    # Build requirement status table
    req_rows = []
    for req_stem in sorted(all_reqs):
        result = agent_results.get(req_stem, {})
        exit_code_val = result.get('exit_code', None)
        attempts = result.get('attempts', 0)

        if exit_code_val is None:
            status = 'NOT_STARTED'
            status_icon = '-'
        elif exit_code_val == 0:
            status = 'PASS'
            status_icon = '✓'
        elif exit_code_val == 99:
            status = 'EXT_DEP_FAIL'
            status_icon = '⚠'
        else:
            status = 'FAIL'
            status_icon = '✗'

        # Find test location
        test_path, test_loc = report_utils.find_test_in_any_status(req_stem)
        if test_loc:
            test_location = f"{test_loc}/"
        else:
            test_location = "-"

        req_rows.append(f"| {req_stem} | {status_icon} {status} | {attempts} | {test_location} |")

    req_table = '\n'.join(req_rows) if req_rows else '| (no requirements found) | - | - | - |'

    exit_reason = _run_state.get('exit_reason', 'UNKNOWN')

    report_content = f"""# Parallel Loop Summary

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
        """Check if a requirement's test currently fails.

        Rule: Queue any test that is NOT in passing/.
        This includes: missing tests, tests in failing/, tests in error/.
        """
        test_path, status = report_utils.find_test_in_any_status(req_file.stem)

        # If no test exists, needs work
        if test_path is None:
            return True

        # If test is in error/, move it to failing/ for retry
        if status == 'error':
            try:
                report_utils.move_test(req_file.stem, 'error', 'failing')
                print(f"  Moved {req_file.stem} from error/ to failing/ (retry)")
            except Exception as e:
                print(f"  Warning: Could not move test: {e}")

        # If test is in passing/, don't queue it
        if status == 'passing':
            return False

        # Test is in failing/ (or was just moved from error/), needs work
        return True

    # Check build requirement FIRST - if it fails, only return that
    # This prevents false failures in other tests due to missing artifacts
    for req_file in req_files:
        if req_file.stem.lower() == BUILD_REQ_STEM:
            if needs_work(req_file):
                print(f"  Build requirement failed - skipping other test checks")
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


def spawn_agent(req_file: Path) -> dict:
    """
    Spawn agent-worker.py for a single requirement.
    Returns dict with 'req_file', 'exit_code', 'output'.
    """
    agent_script = SCRIPT_DIR / 'agent-worker.py'

    result = run_script(
        agent_script,
        args=[str(req_file)],
        timeout=1800,  # 30 minutes per agent
        stream=True
    )

    return {
        'req_file': req_file,
        'exit_code': result['exit_code'],
        'output': result.get('stdout', '') + result.get('stderr', '')
    }


def run_parallel_agents(req_files: list[Path]) -> list[dict]:
    """Spawn agents in parallel (max 5 concurrent), wait for all to complete."""
    results = []

    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_AGENTS) as executor:
        futures = {
            executor.submit(spawn_agent, req_file): req_file
            for req_file in req_files
        }

        for future in as_completed(futures):
            req_file = futures[future]
            try:
                result = future.result()
                results.append(result)
                status = "OK" if result['exit_code'] == 0 else f"FAIL ({result['exit_code']})"
                print(f"  {status} {req_file.name}")
            except Exception as e:
                print(f"  ERROR {req_file.name}: {e}")
                results.append({
                    'req_file': req_file,
                    'exit_code': 1,
                    'output': str(e)
                })

    return results


def run_integration_check() -> bool:
    """
    Run integration check (all tests in passing/).

    quick-test.py automatically moves any failing tests to failing/.

    Returns True if all tests pass, False if any failed.
    """
    print("Running integration check...")
    print()
    return run_all_tests()


def main() -> int:
    """
    Main loop for parallel test/code fixing.

    Simple strategy: keep iterating while tests are failing
    - Each iteration: find tests that fail, spawn agents to fix them
    - Exit when: all tests pass OR max iterations reached OR agents make no progress
    """
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    # Track start time
    _run_state['started_at'] = datetime.now()

    print()
    print("=" * 70)
    print("PARALLEL TEST/CODE LOOP")
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

    # Ensure tests directories exist (failing/, passing/, error/)
    report_utils.ensure_test_directories(Path('./tests'))

    # Ensure tmp directory exists
    Path('./tmp').mkdir(exist_ok=True)

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
                print("OK PARALLEL LOOP COMPLETE - ALL TESTS PASS")
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

        # Spawn agents to fix failing requirements
        print("Spawning agents...")
        results = run_parallel_agents(reqs_needing_work)

        # Track results
        for result in results:
            req_stem = result['req_file'].stem
            _run_state['agent_results'][req_stem] = {
                'exit_code': result['exit_code'],
                'attempts': _run_state['agent_results'].get(req_stem, {}).get('attempts', 0) + 1
            }
            if result['exit_code'] == 99:
                print(f"  Note: {req_stem} reported external dependency failure (treating as code bug)")

        # Update req index after agents may have modified code/tests
        try:
            update_req_index.main()
        except Exception as e:
            print(f"  Warning: Failed to update req index: {e}")

    # Final check - last iteration may have fixed everything
    if not get_reqs_needing_work() and run_integration_check():
        print()
        print("=" * 70)
        print("OK PARALLEL LOOP COMPLETE - ALL TESTS PASS")
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
