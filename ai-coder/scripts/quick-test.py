# Run via: ./bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Quick Test Runner

Runs all tests in ./tests/passing/ (sorted by filename) and verifies they pass.
Tests that fail are moved to ./tests/failing/. Does NOT build first.

Exit codes:
    0 - All passing tests still pass
    1 - One or more tests failed (moved to failing/)

Usage:
    ./ai-coder/scripts/quick-test.py
"""

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import importlib.util
from pathlib import Path
from typing import List, Tuple

SCRIPT_DIR = Path(__file__).parent


def import_script(script_name: str):
    script_path = SCRIPT_DIR / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name.replace('-', '_'), script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


run_script_module = import_script('run-script')
run_script = run_script_module.run_script
report_utils = import_script('report-utils')

def get_required_req_stems() -> set:
    """Get all requirement stems from ./reqs/"""
    reqs_dir = Path('./reqs')
    if not reqs_dir.exists():
        return set()

    stems = set()
    for req_file in reqs_dir.glob('*.md'):
        stems.add(req_file.stem)

    return stems


def get_passing_test_stems() -> set:
    """Get all test stems from ./tests/passing/"""
    tests_dir = Path('./tests/passing')
    if not tests_dir.exists():
        return set()

    stems = set()
    for test_file in tests_dir.glob('*.py'):
        stems.add(test_file.stem)

    return stems


def find_tests() -> List[Path]:
    """Find all test files in ./tests/passing/, sorted by filename stem.

    Returns:
        List of test file paths.
    """
    passing_dir = Path('./tests/passing')

    if not passing_dir.exists():
        return []

    tests = list(passing_dir.glob('*.py'))
    tests.sort(key=lambda t: t.stem)

    return tests

def write_test_report(test_path: Path, passed: bool, output: str):
    """Write a report for a test run to ./reports/ with timestamp prefix."""
    # Extract requirement stem from test filename
    req_stem = report_utils.req_stem_from_test_path(test_path)

    # Create report with new naming convention: {timestamp}_{{{req_stem}}}_TEST_{PASS|FAIL}.md
    status = "PASS" if passed else "FAIL"
    report_type = f"TEST_{status}"
    report_path, timestamp = report_utils.get_report_path(report_type, req_stem)

    # Build report content
    report_content = f"""# Test Report: {req_stem}
**Timestamp:** {timestamp}
**Status:** {status}
**Test File:** {test_path}

---

## Output

```
{output}
```

---

**Result:** {"✓ PASS" if passed else "✗ FAIL"}
"""

    # Write report
    report_path.write_text(report_content, encoding='utf-8')

def is_code_review_test(test_path: Path) -> bool:
    """Check if test is a code-review test that calls prompt-ai.

    Code-review tests need longer timeouts (3600s) because they call AI.
    Regular tests that test ./released/ artifacts use shorter timeouts (180s).
    """
    try:
        content = test_path.read_text(encoding='utf-8')
        # Check for references to prompt-ai or code-inspection-assertion scripts
        return ('prompt-ai.py' in content or
                'prompt_agentic_coder' in content or
                'code-inspection-assertion.py' in content)
    except Exception:
        # If we can't read the file, assume regular test
        return False

def run_test(test_path: Path) -> Tuple[bool, str]:
    """
    Run a single test and return (passed, output).

    Returns:
        (True, output) if test passed (exit code 0)
        (False, output) if test failed (non-zero exit code)
    """
    # Auto-detect timeout based on test type
    if is_code_review_test(test_path):
        timeout = 3600  # 1 hour for code-review tests (call AI)
    else:
        timeout = 180   # 3 minutes for regular tests (test ./released/)

    result = run_script(test_path, timeout=timeout)
    passed = result['success']
    output = result['stdout'] + result['stderr']

    if result['exception'] == 'TimeoutExpired':
        output = f"TIMEOUT ({timeout}s)"

    return passed, output

def main():
    # Check that all requirements have passing tests
    required_stems = get_required_req_stems()
    passing_stems = get_passing_test_stems()
    missing_stems = required_stems - passing_stems

    if missing_stems:
        print("=" * 60)
        print("MISSING PASSING TESTS")
        print("=" * 60)
        print(f"\nThe following requirements have no passing test:\n")
        for stem in sorted(missing_stems):
            print(f"  - {stem}")
        print(f"\nTotal: {len(missing_stems)} requirement(s) without passing test\n")
        return 1

    tests = find_tests()

    if not tests:
        print("No tests found in ./tests/passing/")
        return 1

    print(f"Running {len(tests)} passing tests...\n")

    passed_tests = []
    failed_tests = []

    for test_path in tests:
        print(f"Running {test_path.name}... ", end='', flush=True)

        passed, output = run_test(test_path)

        # Write report for this test
        write_test_report(test_path, passed, output)

        if passed:
            print("✓ PASS")
            passed_tests.append(test_path)
        else:
            print("✗ FAIL")
            # Move failing test from passing/ to failing/
            try:
                report_utils.move_test(test_path.stem, 'passing', 'failing')
                print(f"  → Moved to failing/")
            except Exception as e:
                print(f"  Warning: Could not move test: {e}")
            failed_tests.append((test_path, output))

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    if passed_tests:
        print(f"\n✓ PASSED ({len(passed_tests)}):")
        for test_path in passed_tests:
            print(f"  {test_path.name}")

    if failed_tests:
        print(f"\n✗ FAILED ({len(failed_tests)}) - moved to failing/:")
        for test_path, output in failed_tests:
            print(f"  {test_path.name}")

    print(f"\nTotal: {len(passed_tests)} passed, {len(failed_tests)} failed")

    # Exit with 0 if all passed, 1 if any failed
    return 0 if len(failed_tests) == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
