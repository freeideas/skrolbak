#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, text=True)
    if result.returncode != 0:
        sys.exit(result.returncode)


def get_outer_project_name(repo_dir: Path) -> str:
    outer = repo_dir.parent
    return outer.name


def is_dirty(repo_dir: Path) -> bool:
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_dir,
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        sys.exit(proc.returncode)
    return bool(proc.stdout.strip())


def main():
    script_dir = Path(__file__).resolve().parent
    repo_dir = script_dir.parent

    if not (repo_dir / ".git").exists():
        sys.stderr.write("Expected a git repo at ./ai-coder (missing .git)\n")
        sys.exit(1)

    if is_dirty(repo_dir):
        outer_name = get_outer_project_name(repo_dir)
        print(f"Working tree is dirty in {outer_name}/ai-coder.")
        print("Press Enter to continue with git pull, or Ctrl-C to stop.")
        try:
            input()
        except KeyboardInterrupt:
            print("Aborted.")
            sys.exit(1)

    run(["git", "pull"], cwd=repo_dir)


if __name__ == "__main__":
    main()
