# Run via: ./bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Safe Script Execution Utility

Provides a consistent mechanism for executing Python scripts via subprocess,
isolating the parent process from any errors in the child script.

This handles:
- Missing scripts
- Syntax errors
- Runtime exceptions
- Timeouts
- Import errors
- Any other script failures

All scripts are executed via ./bin/uv.exe run --script to respect dependency declarations.
"""

import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import subprocess
from pathlib import Path
from typing import Dict, List, Optional


def get_uv_path() -> Path:
    """Get path to platform-appropriate uv binary in ai-coder/bin/"""
    import platform
    script_dir = Path(__file__).parent
    bin_dir = script_dir.parent / 'bin'

    system = platform.system()
    if system == 'Windows':
        uv_path = bin_dir / 'uv.exe'
    elif system == 'Darwin':
        uv_path = bin_dir / 'uv.mac'
    else:  # Linux and others
        uv_path = bin_dir / 'uv.linux'

    if not uv_path.exists():
        raise FileNotFoundError(f"uv binary not found at: {uv_path}")
    return uv_path


def run_script(
    script_path: str | Path,
    args: Optional[List[str]] = None,
    timeout: int = 600,
    cwd: Optional[str | Path] = None,
    stream: bool = False
) -> Dict:
    """
    Execute a Python script safely via subprocess using ./bin/uv.exe run --script.

    Args:
        script_path: Path to the Python script to execute
        args: Optional list of command-line arguments to pass to the script
        timeout: Timeout in seconds (default: 600 = 10 minutes)
        cwd: Working directory for script execution (default: current directory)
        stream: If True, stream stdout/stderr directly to parent instead of capturing

    Returns:
        Dict with keys:
            - success: bool (True if exit code was 0)
            - exit_code: int (script's exit code, or special codes for errors)
            - stdout: str (captured stdout)
            - stderr: str (captured stderr)
            - exception: str | None (exception type if subprocess itself failed)

    Special exit codes:
        - 127: Script file not found
        - 124: Timeout expired
        - Other non-zero: Script's actual exit code
    """
    script_path = Path(script_path).resolve()

    # Check if script exists
    if not script_path.exists():
        return {
            'success': False,
            'exit_code': 127,
            'stdout': '',
            'stderr': f'Script not found: {script_path}',
            'exception': 'FileNotFoundError'
        }

    # Build command using our local uv.exe
    try:
        uv_path = get_uv_path()
    except FileNotFoundError as e:
        return {
            'success': False,
            'exit_code': 127,
            'stdout': '',
            'stderr': str(e),
            'exception': 'FileNotFoundError'
        }

    cmd = [str(uv_path), 'run', '--script', str(script_path)]
    if args:
        cmd.extend(args)

    # Execute in subprocess
    try:
        if stream:
            completed = subprocess.run(
                cmd,
                text=True,
                encoding='utf-8',
                timeout=timeout,
                cwd=cwd or Path.cwd()
            )
            return {
                'success': completed.returncode == 0,
                'exit_code': completed.returncode,
                'stdout': '',
                'stderr': '',
                'exception': None
            }
        else:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=timeout,
                cwd=cwd or Path.cwd()
            )

            return {
                'success': result.returncode == 0,
                'exit_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exception': None
            }

    except subprocess.TimeoutExpired as e:
        return {
            'success': False,
            'exit_code': 124,
            'stdout': e.stdout.decode('utf-8') if e.stdout else '',
            'stderr': e.stderr.decode('utf-8') if e.stderr else f'Script timed out after {timeout} seconds',
            'exception': 'TimeoutExpired'
        }

    except Exception as e:
        return {
            'success': False,
            'exit_code': 1,
            'stdout': '',
            'stderr': f'Error executing script: {e}',
            'exception': type(e).__name__
        }


def run_script_streaming(
    script_path: str | Path,
    args: Optional[List[str]] = None,
    timeout: int = 600,
    cwd: Optional[str | Path] = None,
    env: Optional[Dict[str, str]] = None
) -> Dict:
    """
    Execute a Python script with real-time output streaming AND capture.

    This uses Popen with threading to stream output to console while also
    capturing it for later use (e.g., report writing). Handles timeout with
    proper process termination.

    Args:
        script_path: Path to the Python script to execute
        args: Optional list of command-line arguments to pass to the script
        timeout: Timeout in seconds (default: 600 = 10 minutes)
        cwd: Working directory for script execution (default: current directory)
        env: Optional environment variables dict (defaults to os.environ)

    Returns:
        Dict with keys:
            - success: bool (True if exit code was 0)
            - exit_code: int (script's exit code, or special codes for errors)
            - output: str (combined stdout+stderr, captured during streaming)
            - exception: str | None (exception type if subprocess itself failed)

    Special exit codes:
        - 127: Script file not found
        - 124: Timeout expired
        - Other non-zero: Script's actual exit code
    """
    import threading
    import time

    script_path = Path(script_path).resolve()

    # Check if script exists
    if not script_path.exists():
        return {
            'success': False,
            'exit_code': 127,
            'output': f'Script not found: {script_path}',
            'exception': 'FileNotFoundError'
        }

    # Build command using our local uv
    try:
        uv_path = get_uv_path()
    except FileNotFoundError as e:
        return {
            'success': False,
            'exit_code': 127,
            'output': str(e),
            'exception': 'FileNotFoundError'
        }

    cmd = [str(uv_path), 'run', '--script', str(script_path)]
    if args:
        cmd.extend(args)

    # Use provided env or inherit current environment
    if env is None:
        import os
        env = os.environ.copy()

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            bufsize=1,  # Line buffered
            cwd=cwd or Path.cwd(),
            env=env
        )

        output_lines = []
        start_time = time.time()
        timed_out = False

        def read_stream(stream, output_list, prefix=""):
            """Read from stream line by line, print and capture."""
            try:
                for line in iter(stream.readline, ''):
                    if not line:
                        break
                    print(prefix + line, end='', flush=True)
                    output_list.append(prefix + line)
            except Exception as e:
                msg = f"\n[ERROR reading stream: {e}]\n"
                print(msg, end='')
                output_list.append(msg)

        # Start threads to read stdout and stderr concurrently
        stdout_thread = threading.Thread(target=read_stream, args=(process.stdout, output_lines))
        stderr_thread = threading.Thread(target=read_stream, args=(process.stderr, output_lines, "[stderr] "))
        stdout_thread.daemon = True
        stderr_thread.daemon = True
        stdout_thread.start()
        stderr_thread.start()

        # Monitor for timeout
        while process.poll() is None:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                timed_out = True
                timeout_msg = f"\n{'=' * 60}\n[TIMEOUT] Process exceeded {timeout} seconds\n{'=' * 60}\n"
                print(timeout_msg, end='')
                output_lines.append(timeout_msg)

                # Try graceful termination first
                try:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                        kill_msg = "[KILLED] Process terminated gracefully\n"
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
                        kill_msg = "[KILLED] Process force-killed\n"
                    print(kill_msg, end='')
                    output_lines.append(kill_msg)
                except Exception as e:
                    err_msg = f"[ERROR] Failed to kill process: {e}\n"
                    print(err_msg, end='')
                    output_lines.append(err_msg)
                break
            time.sleep(0.1)  # Check every 100ms

        # Wait for reading threads to finish
        stdout_thread.join(timeout=5)
        stderr_thread.join(timeout=5)

        # Get final return code
        if timed_out:
            returncode = 124
        else:
            returncode = process.returncode

        return {
            'success': returncode == 0,
            'exit_code': returncode,
            'output': ''.join(output_lines),
            'exception': 'TimeoutExpired' if timed_out else None
        }

    except Exception as e:
        return {
            'success': False,
            'exit_code': 1,
            'output': f'Error executing script: {e}',
            'exception': type(e).__name__
        }


def run_script_and_exit(
    script_path: str | Path,
    args: Optional[List[str]] = None,
    timeout: int = 600,
    cwd: Optional[str | Path] = None
) -> None:
    """
    Execute a script and exit with its exit code.

    Useful for wrapper scripts that just need to forward to another script.
    Prints stdout/stderr from the child script and exits with its exit code.
    """
    result = run_script(script_path, args, timeout, cwd)

    # Print captured output
    if result['stdout']:
        print(result['stdout'], end='')
    if result['stderr']:
        print(result['stderr'], end='', file=sys.stderr)

    # Exit with the script's exit code
    sys.exit(result['exit_code'])


if __name__ == '__main__':
    # When run directly, execute the script specified as first argument
    if len(sys.argv) < 2:
        print("Usage: run-script.py <script_path> [args...]", file=sys.stderr)
        sys.exit(1)

    script_path = sys.argv[1]
    script_args = sys.argv[2:] if len(sys.argv) > 2 else None

    run_script_and_exit(script_path, script_args)
