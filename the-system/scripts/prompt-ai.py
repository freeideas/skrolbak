# Run via: ./bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

DEFAULT_AGENT = "claude"

"""
Wrapper for agentic coder -- delegates to the configured agent CLI.

Two usage patterns:

1. Module API (recommended for Python scripts):
    import prompt_ai
    prompt_text = Path('./prompts/MY_PROMPT.md').read_text(encoding='utf-8')
    response = prompt_ai.get_ai_response_text(prompt_text, report_type="my_task")

2. CLI (for manual/testing use):
    cat ./prompts/MY_PROMPT.md | prompt-ai.py

Key points:
- Python scripts MUST use module API, NOT subprocess with stdin
- Prompt text passed as string (read from file or manipulated in memory)
- Reports written to ./reports/ with timestamped filenames
"""

import sys
import json
import subprocess
import argparse
import threading
import hashlib
import importlib.util
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent


def _import_script(script_name: str):
    script_path = SCRIPT_DIR / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name.replace('-', '_'), script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_report_utils = _import_script('report-utils')

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

SUPPORTED_AGENTS = {"codex", "claude"}

CLAUDE_MODELS = {
    "hi":     "opus",
    "high":   "opus",
    "medium": "sonnet",
    "med":    "sonnet",
    "low":    "haiku",
    "lo":     "haiku"
}
DEFAULT_MODEL_TIER = "medium"

def _compute_signature(paths: list[str]) -> str:
    """
    Compute a content signature for the given file/directory paths.
    Returns a hex digest representing the content of all files.
    """
    # Collect all files from paths
    files = set()
    for path_str in paths:
        path = Path(path_str).resolve()
        if not path.exists():
            continue  # Skip non-existent paths
        if path.is_file():
            files.add(path)
        elif path.is_dir():
            for item in path.rglob('*'):
                if item.is_file():
                    files.add(item)

    if not files:
        return "empty"

    # Sort for determinism and compute combined hash
    combined_hash = hashlib.sha256()
    for file_path in sorted(files):
        try:
            rel_path = file_path.relative_to(Path.cwd())
        except ValueError:
            rel_path = file_path
        path_str = str(rel_path).replace('\\', '/')
        combined_hash.update(path_str.encode('utf-8'))
        combined_hash.update(b'\x00')
        try:
            with open(file_path, 'rb') as f:
                combined_hash.update(f.read())
                combined_hash.update(b'\x00')
        except Exception:
            pass  # Skip unreadable files

    return combined_hash.hexdigest()


def run_until_stable(
    signature_paths: list[str],
    prompts: list[tuple[str, str]],  # List of (prompt_text, report_type) tuples
    max_iterations: int = 5,
    timeout: int = 600,
    parallel: bool = False,
    verbose: bool = True,
    pre_iteration_callback: callable = None,
    model_tier: str = "medium"
) -> tuple[bool, int, str]:
    """
    Run prompt(s) in a signature-prompt-signature loop until no changes detected.

    Args:
        signature_paths: List of file/directory paths to monitor for changes
        prompts: List of (prompt_text, report_type) tuples to run each iteration
        max_iterations: Maximum number of iterations before stopping
        timeout: Timeout in seconds for each prompt
        parallel: If True, run multiple prompts in parallel; if False, sequentially
        verbose: If True, print progress messages
        pre_iteration_callback: Optional callable(iteration: int) called before each iteration
        model_tier: Model quality tier - "hi" (opus), "medium" (sonnet), "low" (haiku).
                    Defaults to "medium".

    Returns:
        Tuple of (converged: bool, iterations: int, final_signature: str)
        - converged: True if loop exited due to no changes, False if hit max_iterations
        - iterations: Number of iterations completed
        - final_signature: The final signature after all iterations
    """
    def log(msg):
        if verbose:
            print(msg, file=sys.stderr, flush=True)

    for iteration in range(1, max_iterations + 1):
        log(f"  [run_until_stable] Iteration {iteration}/{max_iterations}")

        # Call pre-iteration hook if provided
        if pre_iteration_callback:
            try:
                pre_iteration_callback(iteration)
            except Exception as e:
                log(f"    Warning: pre_iteration_callback error: {e}")

        # Signature BEFORE
        sig_before = _compute_signature(signature_paths)
        log(f"    Signature BEFORE: {sig_before[:16]}...")

        # Run prompts
        if parallel and len(prompts) > 1:
            # Run prompts in parallel using threads
            results = {}
            errors = []

            def run_prompt_worker(prompt_text, report_type):
                try:
                    response = get_ai_response_text(
                        prompt_text,
                        report_type=report_type,
                        timeout=timeout,
                        model_tier=model_tier
                    )
                    results[report_type] = response
                except Exception as e:
                    errors.append(f"{report_type}: {e}")

            threads = []
            for prompt_text, report_type in prompts:
                t = threading.Thread(
                    target=run_prompt_worker,
                    args=(prompt_text, report_type),
                    daemon=False
                )
                t.start()
                threads.append(t)

            for t in threads:
                t.join()

            if errors:
                log(f"    Warning: Some prompts had errors: {errors}")
        else:
            # Run prompts sequentially
            for prompt_text, report_type in prompts:
                try:
                    get_ai_response_text(
                        prompt_text,
                        report_type=report_type,
                        timeout=timeout,
                        model_tier=model_tier
                    )
                except Exception as e:
                    log(f"    Warning: Error in {report_type}: {e}")

        # Signature AFTER
        sig_after = _compute_signature(signature_paths)
        log(f"    Signature AFTER: {sig_after[:16]}...")

        # Check convergence
        if sig_before == sig_after:
            log(f"    Converged (no changes)")
            return (True, iteration, sig_after)
        else:
            log(f"    Changes detected, continuing...")

    log(f"  [run_until_stable] Reached max iterations ({max_iterations})")
    return (False, max_iterations, _compute_signature(signature_paths))


def _process_codex_output(raw_stdout):
    final_agent_message = None

    for line in raw_stdout.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            event = json.loads(stripped)
            if event.get("type") == "item.completed":
                item = event.get("item", {})
                if item.get("type") == "agent_message":
                    final_agent_message = item.get("text", "")
        except json.JSONDecodeError:
            continue

    if final_agent_message is None:
        final_agent_message = raw_stdout.strip()

    return final_agent_message


def _process_claude_output(raw_stdout):
    stripped = raw_stdout.strip()

    if not stripped:
        return ""

    try:
        payload = json.loads(stripped)
    except json.JSONDecodeError:
        return stripped

    # Handle both dict and list responses
    if isinstance(payload, dict):
        result_text = payload.get("result")
        if result_text is None:
            result_text = stripped
    elif isinstance(payload, list):
        # For list responses, try to extract result from the last item
        if payload:
            last_item = payload[-1]
            if isinstance(last_item, dict):
                result_text = last_item.get("result") or last_item.get("text") or stripped
            else:
                result_text = str(last_item)
        else:
            result_text = stripped
    else:
        result_text = stripped

    return result_text


def get_ai_response_text(prompt_text: str, report_type: str = "prompt", timeout: int = 3600, req_stem: str | None = None, model_tier: str = "medium") -> str:
    """
    Run a prompt by delegating to the configured agent CLI using JSON output.

    Args:
        prompt_text: The prompt to send to the agent
        report_type: Type of report for filename (e.g., "FIX_ATTEMPT1", "VERIFY")
        timeout: Maximum seconds to wait for the agent (default: 3600 = 1 hour)
        req_stem: Optional requirement file stem (e.g., "05_discovery-operations").
                  If provided, report filename will be {timestamp}_{{{req_stem}}}_{report_type}.md
        model_tier: Model quality tier - "hi" (opus), "medium" (sonnet), "low" (haiku).
                    Defaults to "medium".

    Returns:
        str: The AI's response text (NOT a subprocess.CompletedProcess object)
    """
    agent = DEFAULT_AGENT

    # Create directories if needed
    Path("./tmp").mkdir(exist_ok=True)
    Path("./reports").mkdir(exist_ok=True)

    # Build agent CLI command (cross-platform: use .bat on Windows, bare command on Unix)
    import platform
    is_windows = platform.system() == 'Windows'

    if agent == "codex":
        codex_cmd = "cdxcli.bat" if is_windows else "cdxcli"
        agent_cmd = [
            codex_cmd, "exec", "-",
            "--json",
            "--skip-git-repo-check",
            "--dangerously-bypass-approvals-and-sandbox"
        ]
    else:  # agent == "claude"
        claude_cmd = "claude.bat" if is_windows else "claude"
        # Resolve model tier to claude model name
        model_name = CLAUDE_MODELS.get(model_tier, CLAUDE_MODELS[DEFAULT_MODEL_TIER])
        agent_cmd = [
            claude_cmd,
            "-",
            "--output-format=json",
            "--dangerously-skip-permissions",
            "--verbose",
            "--model",
            model_name,
        ]

    #print(f"DEBUG [prompt-ai]: Launching {agent} CLI (timeout: {timeout}s, report_type: {report_type})...", file=sys.stderr, flush=True)

    # Capture start time (UTC ISO format)
    start_time = datetime.utcnow()
    start_time_iso = start_time.isoformat() + "Z"

    # Write PROMPT report to ./reports/ before sending to AI
    reports_dir = Path("./reports")
    reports_dir.mkdir(exist_ok=True)

    prompt_report_type = f"{report_type}_PROMPT"
    prompt_report_path, prompt_timestamp = _report_utils.get_report_path(prompt_report_type, req_stem, reports_dir)
    report_title = report_type.replace('_', ' ').title()

    prompt_report_content = f"""# {report_title} [PROMPT]
**Timestamp:** {prompt_timestamp}
**Requirement:** {req_stem or 'N/A'}

---

## Prompt

{prompt_text}
"""

    prompt_report_path.write_text(prompt_report_content, encoding='utf-8')
    #print(f"DEBUG [prompt-ai]: Wrote PROMPT report to {prompt_report_path}", file=sys.stderr, flush=True)

    # Launch agent CLI and capture output
    try:
        # Internal subprocess result - NOT what this function returns!
        _subprocess_result = subprocess.run(
            agent_cmd,
            input=prompt_text,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeout
        )

        # Capture end time and calculate elapsed seconds
        end_time = datetime.utcnow()
        end_time_iso = end_time.isoformat() + "Z"
        elapsed_secs = (end_time - start_time).total_seconds()

        raw_stdout = _subprocess_result.stdout or ""
        raw_stderr = _subprocess_result.stderr or ""

        final_agent_message = None

        if agent == "codex":
            final_agent_message = _process_codex_output(raw_stdout)
        else:
            final_agent_message = _process_claude_output(raw_stdout)

        ai_response = final_agent_message or ""

        if raw_stderr:
            ai_response += f"\n\n--- stderr ---\n{raw_stderr}"

        #print(f"DEBUG [prompt-ai]: {agent} CLI completed (exit code: {_subprocess_result.returncode}, duration: {elapsed_secs:.1f}s)", file=sys.stderr, flush=True)
        #print(f"DEBUG [prompt-ai]: Final message length: {len(ai_response)} chars", file=sys.stderr, flush=True)

        # Write RESPONSE report to ./reports/ with AI response (no prompt)
        response_report_type = f"{report_type}_RESPONSE"
        response_report_path, response_timestamp = _report_utils.get_report_path(response_report_type, req_stem, reports_dir)

        # Pretty-format the JSON output with timing info
        try:
            parsed_json = json.loads(raw_stdout)
            # Add timing fields -- wrap in dict if it's a list
            if isinstance(parsed_json, dict):
                parsed_json["_START-TIME"] = start_time_iso
                parsed_json["_END-TIME"] = end_time_iso
                parsed_json["_ELAPSED-SECS"] = elapsed_secs
                pretty_json = json.dumps(parsed_json, indent=1)
            else:
                # For list or other types, wrap in a dict with timing info
                wrapped = {
                    "_START-TIME": start_time_iso,
                    "_END-TIME": end_time_iso,
                    "_ELAPSED-SECS": elapsed_secs,
                    "_RESPONSE": parsed_json
                }
                pretty_json = json.dumps(wrapped, indent=1)
        except (json.JSONDecodeError, ValueError):
            # If it's not valid JSON, create a wrapper with timing info
            parsed_json = {
                "_START-TIME": start_time_iso,
                "_END-TIME": end_time_iso,
                "_ELAPSED-SECS": elapsed_secs,
                "_RAW_OUTPUT": raw_stdout
            }
            pretty_json = json.dumps(parsed_json, indent=1)

        response_report_content = f"""# {report_title} [RESPONSE]
**Timestamp:** {response_timestamp}
**Requirement:** {req_stem or 'N/A'}

---

## Response

{ai_response}

---

## Raw JSON Output

```json
// FULL JSON FROM AI
{pretty_json}
// FULL JSON FROM AI END
```
"""

        response_report_path.write_text(response_report_content, encoding='utf-8')
        #print(f"DEBUG [prompt-ai]: Wrote RESPONSE report to {response_report_path}", file=sys.stderr, flush=True)

        if _subprocess_result.returncode != 0:
            raise RuntimeError(f"{agent} CLI exited with {_subprocess_result.returncode}")

        return ai_response  # Returns str, not subprocess result!

    except subprocess.TimeoutExpired:
        end_time = datetime.utcnow()
        elapsed_secs = (end_time - start_time).total_seconds()
        error_msg = f"Timeout: {agent} CLI did not complete within {timeout}s (elapsed: {elapsed_secs:.1f}s)"
        print(f"ERROR [prompt-ai]: {error_msg}", file=sys.stderr, flush=True)
        raise TimeoutError(error_msg)
    except Exception as e:
        error_msg = f"Error running {agent} CLI: {e}"
        print(f"ERROR [prompt-ai]: {error_msg}", file=sys.stderr, flush=True)
        raise

def test_worker(task_name, prompt, expected_answer, results):
    """Worker thread for test mode"""
    try:
        print(f"[TEST] {task_name}: Submitting prompt...", file=sys.stderr, flush=True)
        result = get_ai_response_text(prompt, report_type=f"test_{task_name}")

        # Check if expected answer is in the result
        if str(expected_answer) in result:
            print(f"[TEST] {task_name}: OK Got expected answer: {expected_answer}", file=sys.stderr, flush=True)
            results[task_name] = True
        else:
            print(f"[TEST] {task_name}: X Expected {expected_answer} not found in result", file=sys.stderr, flush=True)
            print(f"[TEST] {task_name}: Result was: {result[:200]}...", file=sys.stderr, flush=True)
            results[task_name] = False
    except Exception as e:
        print(f"[TEST] {task_name}: X Error: {e}", file=sys.stderr, flush=True)
        results[task_name] = False

def run_test_mode():
    """Run test mode with two concurrent prime number tasks"""
    test_tasks = {
        "test1": {
            "prompt": "Calculate the 100th prime number and output only that number.",
            "expected": 541
        },
        "test2": {
            "prompt": "Calculate the 50th prime number and output only that number.",
            "expected": 229
        }
    }

    print("[TEST] Starting test mode with 2 concurrent tasks...", file=sys.stderr, flush=True)

    results = {}
    threads = []

    # Spawn worker threads (each will launch its own agent CLI process)
    for task_name, config in test_tasks.items():
        thread = threading.Thread(
            target=test_worker,
            args=(task_name, config["prompt"], config["expected"], results),
            daemon=False
        )
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Check results
    all_passed = all(results.values())

    if all_passed:
        print("\n[TEST] OK All tests passed!", file=sys.stderr, flush=True)
        sys.exit(0)
    else:
        print("\n[TEST] X Some tests failed", file=sys.stderr, flush=True)
        sys.exit(1)

def main():
    """Main entry point - handles both test mode and normal stdin mode."""
    parser = argparse.ArgumentParser(description="Agentic coder prompt wrapper")
    parser.add_argument("--test", action="store_true", help="Run in test mode with concurrent prime number tasks")
    args = parser.parse_args()

    # Test mode: run concurrent tests and exit
    if args.test:
        run_test_mode()
        return

    # Normal mode: read prompt from stdin, launch agent CLI, write result to stdout
    prompt = sys.stdin.read()

    if not prompt.strip():
        print("Error: No prompt provided on stdin", file=sys.stderr)
        sys.exit(1)

    # Execute via agent CLI
    try:
        result = get_ai_response_text(prompt, report_type="stdin_prompt")
        # Write output to stdout
        sys.stdout.write(result)
        sys.exit(0)
    except TimeoutError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
