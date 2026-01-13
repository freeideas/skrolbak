# Run via: imported by other scripts
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Report Utilities

Shared utilities for consistent report naming across ai-coder scripts.

Report naming convention:
  - Req-specific: {timestamp}_{{{req_stem}}}_{report_type}.md
  - General:      {timestamp}_{report_name}.md

Examples:
  - 2025-12-14-23-03-16-461_{00_BUILD-REQ}_TEST_PASS.md
  - 2025-12-14-23-03-16-461_{05_discovery-operations}_FIX_PROMPT.md
  - 2025-12-14-23-03-16-461_PARALLEL_LOOP_SUMMARY.md
"""

from datetime import datetime
from pathlib import Path


def get_timestamp() -> str:
    """Get current timestamp in standard format (millisecond precision)."""
    return datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')[:-3]


def get_report_filename(report_type: str, req_stem: str | None = None, timestamp: str | None = None) -> str:
    """
    Generate a standardized report filename.

    Args:
        report_type: Type/name of report (e.g., "TEST_PASS", "FIX_PROMPT", "PARALLEL_LOOP_SUMMARY")
        req_stem: Optional requirement file stem (e.g., "00_BUILD-REQ", "05_discovery-operations").
                  If provided, will be wrapped in curly braces.
        timestamp: Optional timestamp string. If not provided, current time is used.

    Returns:
        Filename like "2025-12-14-23-03-16-461_{00_BUILD-REQ}_TEST_PASS.md"
        or "2025-12-14-23-03-16-461_PARALLEL_LOOP_SUMMARY.md"
    """
    if timestamp is None:
        timestamp = get_timestamp()

    if req_stem:
        return f"{timestamp}_{{{req_stem}}}_{report_type}.md"
    else:
        return f"{timestamp}_{report_type}.md"


def get_report_path(report_type: str, req_stem: str | None = None, reports_dir: Path | None = None, timestamp: str | None = None) -> tuple[Path, str]:
    """
    Generate full path for a report file.

    Args:
        report_type: Type/name of report
        req_stem: Optional requirement file stem
        reports_dir: Optional reports directory (defaults to ./reports)
        timestamp: Optional timestamp string. If not provided, current time is used.

    Returns:
        Tuple of (full Path to the report file, timestamp used)
    """
    if reports_dir is None:
        reports_dir = Path('./reports')

    if timestamp is None:
        timestamp = get_timestamp()

    reports_dir.mkdir(parents=True, exist_ok=True)
    filename = get_report_filename(report_type, req_stem, timestamp)
    return reports_dir / filename, timestamp


def req_stem_from_test_path(test_path: Path) -> str:
    """
    Extract the requirement stem from a test file path.

    Args:
        test_path: Path to test file (e.g., "tests/05_discovery-operations.py")

    Returns:
        Requirement stem (e.g., "05_discovery-operations")
    """
    return test_path.stem


# ============================================================================
# TEST FILE LOCATION HELPERS
# ============================================================================

# Valid test status directories
TEST_STATUSES = ('failing', 'passing')


def get_test_dir(status: str = 'failing', tests_base: Path | None = None) -> Path:
    """
    Get the test directory for a given status.

    Args:
        status: Test status ('failing' or 'passing')
        tests_base: Base tests directory (defaults to ./tests)

    Returns:
        Path to the status subdirectory (e.g., ./tests/failing/)
    """
    if status not in TEST_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of: {TEST_STATUSES}")

    if tests_base is None:
        tests_base = Path('./tests')

    return tests_base / status


def get_test_path(req_stem: str, status: str = 'failing', tests_base: Path | None = None) -> Path:
    """
    Get the test file path for a requirement in a specific status directory.

    Args:
        req_stem: Requirement file stem (e.g., "05_discovery-operations")
        status: Test status ('failing' or 'passing')
        tests_base: Base tests directory (defaults to ./tests)

    Returns:
        Path to the test file (e.g., ./tests/failing/05_discovery-operations.py)
    """
    return get_test_dir(status, tests_base) / f"{req_stem}.py"


def find_test_in_any_status(req_stem: str, tests_base: Path | None = None) -> tuple[Path | None, str | None]:
    """
    Find a test file in any status directory.

    Searches in order: passing, failing, error.

    Args:
        req_stem: Requirement file stem (e.g., "05_discovery-operations")
        tests_base: Base tests directory (defaults to ./tests)

    Returns:
        Tuple of (path, status) if found, (None, None) if not found.
        Status is 'passing' or 'failing'.
    """
    if tests_base is None:
        tests_base = Path('./tests')

    # Search order: passing first (skip work), then failing
    for status in ('passing', 'failing'):
        test_path = get_test_path(req_stem, status, tests_base)
        if test_path.exists():
            return test_path, status

    return None, None


def move_test(req_stem: str, from_status: str, to_status: str, tests_base: Path | None = None) -> Path:
    """
    Move a test file from one status directory to another.

    Args:
        req_stem: Requirement file stem (e.g., "05_discovery-operations")
        from_status: Source status ('failing' or 'passing')
        to_status: Destination status ('failing' or 'passing')
        tests_base: Base tests directory (defaults to ./tests)

    Returns:
        New path of the test file

    Raises:
        FileNotFoundError: If source test file doesn't exist
        ValueError: If invalid status provided
    """
    if from_status not in TEST_STATUSES:
        raise ValueError(f"Invalid from_status '{from_status}'. Must be one of: {TEST_STATUSES}")
    if to_status not in TEST_STATUSES:
        raise ValueError(f"Invalid to_status '{to_status}'. Must be one of: {TEST_STATUSES}")

    if tests_base is None:
        tests_base = Path('./tests')

    from_path = get_test_path(req_stem, from_status, tests_base)
    to_path = get_test_path(req_stem, to_status, tests_base)

    if not from_path.exists():
        raise FileNotFoundError(f"Test file not found: {from_path}")

    # Ensure destination directory exists
    to_path.parent.mkdir(parents=True, exist_ok=True)

    # Move the file
    from_path.rename(to_path)

    # Defensive: ensure no duplicates exist in OTHER directories
    for status in TEST_STATUSES:
        if status != to_status:
            other = get_test_path(req_stem, status, tests_base)
            if other.exists():
                other.unlink()
                print(f"  Warning: Removed stale duplicate from {status}/")

    return to_path


def ensure_test_directories(tests_base: Path | None = None):
    """
    Ensure all test status directories exist.

    Args:
        tests_base: Base tests directory (defaults to ./tests)
    """
    if tests_base is None:
        tests_base = Path('./tests')

    for status in TEST_STATUSES:
        (tests_base / status).mkdir(parents=True, exist_ok=True)


def migrate_flat_tests(tests_base: Path | None = None) -> int:
    """
    Move flat tests to failing/ subdirectory (one-time migration).

    Also removes 'test_' prefix from filenames to match current naming convention.

    Args:
        tests_base: Base tests directory (defaults to ./tests)

    Returns:
        Number of tests migrated
    """
    if tests_base is None:
        tests_base = Path('./tests')

    # Check for flat structure (test files directly in ./tests/)
    # Look for both old style (test_*.py) and new style (*.py) files
    flat_tests = list(tests_base.glob('*.py'))
    # Filter out any files in subdirectories
    flat_tests = [f for f in flat_tests if f.is_file()]

    if not flat_tests:
        return 0  # No migration needed

    # Ensure subdirectories exist
    ensure_test_directories(tests_base)

    # Move flat tests to failing/ and remove 'test_' prefix if present
    migrated = 0
    for test_file in flat_tests:
        # Remove 'test_' prefix if present
        new_name = test_file.name
        if new_name.startswith('test_'):
            new_name = new_name[5:]  # Remove 'test_' prefix

        dest = tests_base / 'failing' / new_name
        test_file.rename(dest)
        if dest.name != test_file.name:
            print(f"  Migrated and renamed {test_file.name} to failing/{dest.name}")
        else:
            print(f"  Migrated {test_file.name} to failing/")
        migrated += 1

    return migrated
