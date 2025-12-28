#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path


def run_capture(cmd, cwd):
    proc = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        sys.exit(proc.returncode)
    return proc.stdout


def run(cmd, cwd):
    result = subprocess.run(cmd, cwd=cwd, text=True)
    if result.returncode != 0:
        sys.exit(result.returncode)


def get_outer_project_name(repo_dir: Path) -> str:
    outer = repo_dir.parent
    return outer.name


def main():
    script_dir = Path(__file__).resolve().parent
    repo_dir = script_dir.parent

    if not (repo_dir / ".git").exists():
        sys.stderr.write("Expected a git repo at ./the-system (missing .git)\n")
        sys.exit(1)

    status = run_capture(["git", "status", "--porcelain"], cwd=repo_dir).strip()
    if not status:
        print("No changes to upload.")
        return

    outer_name = get_outer_project_name(repo_dir)
    message = f"from {outer_name}"

    run(["git", "add", "-A"], cwd=repo_dir)
    run(["git", "commit", "-m", message], cwd=repo_dir)
    run(["git", "push"], cwd=repo_dir)


if __name__ == "__main__":
    main()
