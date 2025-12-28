# /// script
# requires-python = ">=3.11"
# dependencies = ["merge3", "filelock"]
# ///

"""
Agent Sandbox with 3-Way Merge

Replaces git worktrees with a simpler copy-based approach:
1. Copy project to sandbox, snapshot ./code/ state
2. Agent works in sandbox
3. Lock, 3-way merge ./code/ back, unlock

The sandbox is named after the requirement stem (e.g., ./tmp/00_build-output/).
"""

import shutil
from pathlib import Path
from filelock import FileLock
from merge3 import Merge3

# Lock file for serializing merges from concurrent agents
MERGE_LOCK = Path('./tmp/.code_merge.lock')


def _make_sandbox_ignore(project_root: Path):
    """
    Create ignore function for sandbox copying.

    - .git and tmp: excluded only at project root (preserves nested .git like tools/compiler/flutter/.git)
    - __pycache__, *.pyc, .pytest_cache: excluded everywhere
    """
    def ignore_func(directory: str, contents: list[str]) -> list[str]:
        ignored = []
        dir_path = Path(directory)

        # At root level only, exclude .git and tmp
        if dir_path == project_root:
            if '.git' in contents:
                ignored.append('.git')
            if 'tmp' in contents:
                ignored.append('tmp')

        # Everywhere: exclude cache files/dirs
        for item in contents:
            if item == '__pycache__' or item == '.pytest_cache' or item.endswith('.pyc'):
                ignored.append(item)

        return ignored

    return ignore_func


def create_sandbox(req_stem: str, project_root: Path = None) -> tuple[Path, Path]:
    """
    Create isolated sandbox for an agent.

    Args:
        req_stem: The requirement file stem (e.g., '00_build-output')
        project_root: Project root directory (default: current directory)

    Returns:
        (sandbox_path, base_snapshot_path)
    """
    if project_root is None:
        project_root = Path.cwd()

    sandbox = project_root / 'tmp' / req_stem
    base_snapshot = project_root / 'tmp' / f'{req_stem}_base_code'

    # Clean up any existing
    for p in [sandbox, base_snapshot]:
        if p.exists():
            shutil.rmtree(p)

    # Copy entire project to sandbox (except root .git, tmp, and cache dirs)
    shutil.copytree(
        project_root,
        sandbox,
        ignore=_make_sandbox_ignore(project_root)
    )

    # Create fake .git to prevent AI from escaping sandbox
    # (AI looks for .git to find "real" project root)
    fake_git = sandbox / '.git'
    fake_git.mkdir()
    (fake_git / 'HEAD').write_text('ref: refs/heads/main\n')
    (fake_git / 'config').write_text(
        '[core]\n'
        '\trepositoryformatversion = 0\n'
        '\tbare = false\n'
    )

    # Snapshot current ./code/ as the "base" for later 3-way merge
    code_dir = project_root / 'code'
    if code_dir.exists():
        shutil.copytree(code_dir, base_snapshot)
    else:
        # No code dir yet - create empty base snapshot
        base_snapshot.mkdir(parents=True)

    return sandbox, base_snapshot


def merge_file_3way(base: str, ours: str, theirs: str) -> tuple[str, bool]:
    """
    3-way merge of file contents.

    Args:
        base: Original content (when agent started)
        ours: Current content (may have changed since agent started)
        theirs: Agent's modified content

    Returns:
        (merged_content, had_conflicts)
    """
    # Fast paths - no merge needed
    if ours == theirs:
        return ours, False
    if base == ours:
        # Only agent changed, take theirs
        return theirs, False
    if base == theirs:
        # Only main changed, keep ours
        return ours, False

    # Real 3-way merge needed
    m = Merge3(
        base.splitlines(keepends=True),
        ours.splitlines(keepends=True),
        theirs.splitlines(keepends=True)
    )

    merged_lines = list(m.merge_lines(
        name_a='CURRENT',
        name_b='AGENT',
        start_marker='<<<<<<<',
        mid_marker='=======',
        end_marker='>>>>>>>'
    ))

    merged = ''.join(merged_lines)
    has_conflicts = '<<<<<<<' in merged
    return merged, has_conflicts


def _read_file_safe(path: Path) -> str:
    """Read file content, returning empty string if file doesn't exist."""
    if not path.exists():
        return ''
    try:
        return path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        # Binary file - can't merge, just return empty to trigger copy
        return ''


def _is_binary_file(path: Path) -> bool:
    """Check if a file appears to be binary."""
    if not path.exists():
        return False
    try:
        with open(path, 'rb') as f:
            chunk = f.read(8192)
            return b'\x00' in chunk
    except Exception:
        return False


def merge_code_back(
    sandbox: Path,
    base_snapshot: Path,
    project_root: Path = None
) -> list[Path]:
    """
    Merge agent's ./code/ changes back to main project.

    Uses file locking to serialize concurrent merges.

    Args:
        sandbox: Path to agent's sandbox directory
        base_snapshot: Path to the base code snapshot (from when agent started)
        project_root: Main project root (default: current directory)

    Returns:
        List of files with conflicts (empty if clean merge).
    """
    if project_root is None:
        project_root = Path.cwd()

    MERGE_LOCK.parent.mkdir(parents=True, exist_ok=True)

    agent_code = sandbox / 'code'
    main_code = project_root / 'code'
    conflicts = []

    # Lock to serialize merges from concurrent agents
    with FileLock(str(MERGE_LOCK), timeout=300):
        # Ensure main code directory exists
        main_code.mkdir(parents=True, exist_ok=True)

        # Collect all files from all three sources
        all_files: set[Path] = set()
        for src in [base_snapshot, main_code, agent_code]:
            if src.exists():
                all_files.update(f.relative_to(src) for f in src.rglob('*') if f.is_file())

        for rel_path in sorted(all_files):
            base_file = base_snapshot / rel_path
            main_file = main_code / rel_path
            agent_file = agent_code / rel_path

            # Handle binary files - just copy, don't merge
            if _is_binary_file(agent_file) or _is_binary_file(main_file) or _is_binary_file(base_file):
                if agent_file.exists():
                    main_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(agent_file, main_file)
                continue

            # Read contents (empty string if file doesn't exist)
            base = _read_file_safe(base_file)
            ours = _read_file_safe(main_file)
            theirs = _read_file_safe(agent_file)

            # Handle deletions
            if not agent_file.exists() and base_file.exists():
                # Agent deleted the file
                if ours == base:
                    # Main didn't change it, safe to delete
                    if main_file.exists():
                        main_file.unlink()
                    continue
                # Main changed it, conflict - keep main's version
                conflicts.append(rel_path)
                continue

            if not agent_file.exists():
                # File doesn't exist in agent and wasn't in base - skip
                continue

            # Merge
            merged, has_conflict = merge_file_3way(base, ours, theirs)

            if has_conflict:
                conflicts.append(rel_path)

            # Write merged result
            main_file.parent.mkdir(parents=True, exist_ok=True)
            main_file.write_text(merged, encoding='utf-8')

    return conflicts


def copy_test_to_status(
    sandbox: Path,
    req_stem: str,
    target_status: str,
    project_root: Path = None
):
    """
    Copy test file from sandbox to main project's test directory.

    Removes any existing test with the same stem from all status directories,
    then copies from the sandbox to the target status directory.

    Args:
        sandbox: Path to agent's sandbox directory
        req_stem: The requirement stem (test filename without .py)
        target_status: Target status directory ('passing', 'failing', or 'error')
        project_root: Main project root (default: current directory)
    """
    if project_root is None:
        project_root = Path.cwd()

    test_filename = f'{req_stem}.py'
    main_tests = project_root / 'tests'

    # Find the test file in the sandbox (could be in any status subdir)
    sandbox_test = None
    for status in ['failing', 'passing', 'error']:
        candidate = sandbox / 'tests' / status / test_filename
        if candidate.exists():
            sandbox_test = candidate
            break

    if sandbox_test is None:
        print(f"  Warning: No test file found in sandbox for {req_stem}")
        return

    # Remove existing test from all status directories in main project
    for status in ['failing', 'passing', 'error']:
        existing = main_tests / status / test_filename
        if existing.exists():
            existing.unlink()

    # Copy to target status directory
    target_dir = main_tests / target_status
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / test_filename
    shutil.copy2(sandbox_test, target_file)

    print(f"  Moved test to {target_status}/: {test_filename}")


def cleanup_sandbox(sandbox: Path, base_snapshot: Path):
    """Remove sandbox and base snapshot directories."""
    for p in [sandbox, base_snapshot]:
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)


def copy_reports_from_sandbox(sandbox: Path, project_root: Path = None):
    """Copy any reports from sandbox to main project's reports directory."""
    if project_root is None:
        project_root = Path.cwd()

    sandbox_reports = sandbox / 'reports'
    main_reports = project_root / 'reports'

    if not sandbox_reports.exists():
        return

    try:
        shutil.copytree(sandbox_reports, main_reports, dirs_exist_ok=True, copy_function=shutil.copy2)
        print("  Copied reports from sandbox to ./reports/")
    except Exception as e:
        print(f"  Warning: Failed to copy sandbox reports: {e}")
