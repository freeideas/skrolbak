# Run via: ./bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Kill any processes running from ./ai-coder/ directories.

Targets the main repo plus any sandboxes (e.g., ./tmp/*/ai-coder).
Detects the platform (Windows/macOS/Linux), finds matching processes, and terminates
them (attempts graceful kill first when supported).
"""

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import json
import os
import platform
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

try:
    import psutil  # type: ignore
except ImportError:
    psutil = None

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent


def normalize_path(path_str: str) -> str:
    """Normalize path for comparisons (lowercase, forward slashes)."""
    return path_str.replace('\\', '/').rstrip('/').lower()


def discover_the_system_dirs() -> list[Path]:
    """Find all ai-coder directories (main repo + sandboxes in ./tmp/)."""
    targets: list[Path] = []

    main_dir = PROJECT_ROOT / 'ai-coder'
    if main_dir.exists():
        targets.append(main_dir.resolve())

    tmp_dir = PROJECT_ROOT / 'tmp'
    if tmp_dir.exists():
        for candidate in tmp_dir.glob('**/ai-coder'):
            if candidate.is_dir():
                try:
                    targets.append(candidate.resolve())
                except OSError:
                    # Skip paths we cannot resolve (permission issues, etc.)
                    continue

    # Deduplicate while preserving order
    unique_targets: list[Path] = []
    seen: set[Path] = set()
    for path in targets:
        if path not in seen:
            unique_targets.append(path)
            seen.add(path)

    return unique_targets


def read_proc_cwd(pid: int) -> str | None:
    """Try to read a process cwd from /proc (Linux-only)."""
    try:
        return os.readlink(f"/proc/{pid}/cwd")
    except FileNotFoundError:
        return None
    except PermissionError:
        return None
    except OSError:
        return None


def process_matches_target(text: str, normalized_targets: list[str]) -> bool:
    """Return True if any normalized target path is present in the text blob."""
    if not text:
        return False
    normalized_text = normalize_path(text)
    return any(target in normalized_text for target in normalized_targets)


def find_processes_psutil(normalized_targets: list[str]) -> list[dict[str, Any]]:
    """Find matching processes using psutil (if available)."""
    matches: list[dict[str, Any]] = []
    if psutil is None:
        return matches

    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'cwd']):
        try:
            info = proc.info
            pid = info.get('pid')
            if pid in (os.getpid(), None):
                continue

            text_parts = [
                info.get('name') or '',
                info.get('exe') or '',
                ' '.join(info.get('cmdline') or []),
                info.get('cwd') or '',
            ]
            combined = ' '.join(text_parts)

            if process_matches_target(combined, normalized_targets):
                matches.append({
                    'pid': pid,
                    'proc': proc,
                    'source': combined.strip(),
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        except Exception:
            continue

    return matches


def find_processes_posix(normalized_targets: list[str]) -> list[dict[str, Any]]:
    """Find matching processes on POSIX systems using ps (fallback when psutil missing)."""
    matches: list[dict[str, Any]] = []
    result = subprocess.run(
        ['ps', '-eo', 'pid=,args='],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return matches

    for line in result.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        pid_text, _, cmd = line.partition(' ')
        try:
            pid = int(pid_text)
        except ValueError:
            continue

        if pid == os.getpid():
            continue

        cmd_text = cmd.strip()
        text_blobs = [cmd_text]

        cwd = read_proc_cwd(pid)
        if cwd:
            text_blobs.append(cwd)

        combined = ' '.join(text_blobs)
        if process_matches_target(combined, normalized_targets):
            matches.append({
                'pid': pid,
                'source': combined.strip(),
            })

    return matches


def find_processes_windows(normalized_targets: list[str]) -> list[dict[str, Any]]:
    """Find matching processes on Windows using PowerShell (fallback when psutil missing)."""
    matches: list[dict[str, Any]] = []
    ps_cmd = [
        'powershell',
        '-NoProfile',
        '-Command',
        'Get-CimInstance Win32_Process | '
        'Select-Object ProcessId,CommandLine,ExecutablePath | ConvertTo-Json'
    ]

    result = subprocess.run(ps_cmd, capture_output=True, text=True)
    if result.returncode != 0 or not result.stdout.strip():
        return matches

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return matches

    processes = data if isinstance(data, list) else [data]
    for proc in processes:
        pid = proc.get('ProcessId')
        if not isinstance(pid, int):
            continue
        if pid == os.getpid():
            continue

        cmdline = proc.get('CommandLine') or ''
        exe_path = proc.get('ExecutablePath') or ''
        combined = f"{cmdline} {exe_path}".strip()

        if process_matches_target(combined, normalized_targets):
            matches.append({
                'pid': pid,
                'source': combined,
            })

    return matches


def find_matching_processes(target_dirs: list[Path]) -> list[dict[str, Any]]:
    """Aggregate process matches using psutil (if present) or OS-specific fallbacks."""
    normalized_targets = [normalize_path(str(p)) for p in target_dirs]
    system = platform.system()

    # Prefer psutil when available (cross-platform)
    matches = find_processes_psutil(normalized_targets)
    if matches:
        return matches

    if system == 'Windows':
        return find_processes_windows(normalized_targets)
    else:
        return find_processes_posix(normalized_targets)


def kill_with_psutil(proc_obj: Any, pid: int) -> bool:
    """Attempt graceful then force kill using psutil."""
    try:
        proc_obj.terminate()
        proc_obj.wait(timeout=3)
        return True
    except psutil.TimeoutExpired:
        try:
            proc_obj.kill()
            proc_obj.wait(timeout=3)
            return True
        except Exception:
            return False
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False
    except Exception:
        return False


def kill_pid(pid: int) -> bool:
    """Kill a PID without psutil."""
    system = platform.system()
    if system == 'Windows':
        result = subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'], capture_output=True)
        return result.returncode == 0

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return True
    except PermissionError:
        return False
    except Exception:
        return False

    time.sleep(0.5)

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return True
    except Exception:
        pass

    try:
        os.kill(pid, signal.SIGKILL)
        return True
    except ProcessLookupError:
        return True
    except Exception:
        return False


def main() -> int:
    project_root = PROJECT_ROOT
    os.chdir(project_root)

    print("KILLER Searching for processes under ./ai-coder/ ...")
    targets = discover_the_system_dirs()
    if not targets:
        print("  No ai-coder directories found; nothing to do.")
        return 0

    print("  Target directories:")
    for path in targets:
        print(f"   - {path}")

    matches = find_matching_processes(targets)
    if not matches:
        print("  OK No matching processes found.")
        return 0

    print(f"  Found {len(matches)} process(es) to kill.")
    killed = 0
    for entry in matches:
        pid = entry.get('pid')
        if not isinstance(pid, int):
            continue

        desc = entry.get('source', '').strip()
        print(f"  Killing PID {pid} ...")

        success = False
        if psutil is not None and entry.get('proc') is not None:
            success = kill_with_psutil(entry['proc'], pid)
        else:
            success = kill_pid(pid)

        if success:
            killed += 1
            if desc:
                print(f"    OK Killed PID {pid}: {desc}")
            else:
                print(f"    OK Killed PID {pid}")
        else:
            print(f"    Warning: Failed to kill PID {pid}", file=sys.stderr)

    print(f"\nDone. Killed {killed} process(es).")
    return 0


if __name__ == '__main__':
    sys.exit(main())
