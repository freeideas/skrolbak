#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Push ai-coder to its GitHub repository.

This script handles the .disabled.git* convention: ai-coder keeps its git
files renamed (e.g., .git -> .disabled.git) so it doesn't appear as a nested
repo when copied into other projects.

Workflow:
1. Rename .disabled.git* -> .git* (enable git)
2. Stage all changes, commit, and push
3. Rename .git* -> .disabled.git* (disable git)

Usage:
    ai-coder_push.py [commit message]

If no commit message is provided, opens an editor or uses a default message.
"""

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import subprocess
from pathlib import Path

# Change to ai-coder directory (one level up from scripts/)
SCRIPT_DIR = Path(__file__).parent.resolve()
THE_SYSTEM_DIR = SCRIPT_DIR.parent
os.chdir(THE_SYSTEM_DIR)


def run(cmd, check=True):
    """Run a command and return the result."""
    result = subprocess.run(
        cmd,
        shell=True,
        text=True,
        encoding='utf-8',
        capture_output=True
    )
    if check and result.returncode != 0:
        print(f"Command failed: {cmd}", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    return result


def find_disabled_git_files():
    """Find all .disabled.git* files/directories in ai-coder root."""
    disabled = []
    for item in THE_SYSTEM_DIR.iterdir():
        if item.name.startswith('.disabled.git'):
            disabled.append(item)
    return disabled


def find_git_files():
    """Find all .git* files/directories in ai-coder root."""
    git_files = []
    for item in THE_SYSTEM_DIR.iterdir():
        if item.name.startswith('.git'):
            git_files.append(item)
    return git_files


def enable_git():
    """Rename .disabled.git* -> .git* to enable git."""
    disabled = find_disabled_git_files()
    if not disabled:
        # Check if git is already enabled
        if find_git_files():
            print("Git already enabled (.git* files present)")
            return True
        else:
            print("Error: No .disabled.git* or .git* files found", file=sys.stderr)
            print("This directory doesn't appear to be a git repository", file=sys.stderr)
            return False

    print("Enabling git...")
    for item in disabled:
        new_name = item.name.replace('.disabled.git', '.git')
        new_path = item.parent / new_name
        print(f"  {item.name} -> {new_name}")
        item.rename(new_path)
    return True


def disable_git():
    """Rename .git* -> .disabled.git* to hide git from outer projects."""
    git_files = find_git_files()
    if not git_files:
        print("No .git* files to disable")
        return

    print("Disabling git...")
    for item in git_files:
        new_name = item.name.replace('.git', '.disabled.git')
        new_path = item.parent / new_name
        print(f"  {item.name} -> {new_name}")
        item.rename(new_path)


def get_status():
    """Get git status summary."""
    result = run("git status --porcelain", check=False)
    return result.stdout.strip()


def commit_and_push(message=None):
    """Stage all changes, commit, and push."""
    # Check for changes
    status = get_status()
    if not status:
        print("No changes to commit")
        return True

    print("\nChanges to commit:")
    print(status)
    print()

    # Stage all changes
    print("Staging changes...")
    run("git add -A")

    # Commit
    if message is None:
        message = "Update ai-coder"

    # Escape message for shell
    escaped_message = message.replace("'", "'\\''")

    print(f"Committing: {message}")
    commit_cmd = f"""git commit -m $'{escaped_message}

🤖 Generated with [Claude Code](https://claude.com/claude-code)'"""

    result = run(commit_cmd, check=False)
    if result.returncode != 0:
        if "nothing to commit" in result.stdout or "nothing to commit" in result.stderr:
            print("Nothing to commit")
            return True
        print(f"Commit failed: {result.stderr}", file=sys.stderr)
        return False

    print(result.stdout)

    # Push
    print("Pushing to origin...")
    result = run("git push origin main", check=False)
    if result.returncode != 0:
        # Try with gh auth
        print("Retrying with gh auth...")
        run("gh auth setup-git", check=False)
        result = run("git push origin main", check=False)
        if result.returncode != 0:
            print(f"Push failed: {result.stderr}", file=sys.stderr)
            return False

    print("✓ Push successful")
    return True


def main():
    # Get commit message from args
    message = None
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])

    print(f"Working directory: {THE_SYSTEM_DIR}")
    print()

    success = False
    try:
        # Step 1: Enable git
        if not enable_git():
            sys.exit(1)

        # Step 2: Commit and push
        success = commit_and_push(message)

    finally:
        # Step 3: Always disable git, even on failure
        print()
        disable_git()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
