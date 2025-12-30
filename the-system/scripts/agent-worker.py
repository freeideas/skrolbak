# Run via: ./the-system/bin/uv.exe run --script this_file.py <req_file>
# /// script
# requires-python = ">=3.11"
# dependencies = ["merge3", "filelock"]
# ///

"""
Agent Worker

Works on a single requirement in an isolated sandbox (copy of project).
1. Create sandbox (copy project to ./tmp/{req_stem}/)
2. Fix code/test until test passes (FIX_AND_TEST.md)
3. Verify test quality (VERIFY_TEST.md)
4. 3-way merge ./code/ back to main project
5. Copy test to appropriate status directory
6. Cleanup sandbox

Exit codes:
  0 - Success
  1 - Error
  99 - External dependency failure
"""

import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import platform
import traceback
import importlib.util
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
MAX_FIX_ATTEMPTS = 5


def import_script(script_name: str):
    script_path = SCRIPT_DIR / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name.replace('-', '_'), script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prompt_ai = import_script('prompt-ai')
compute_signature = import_script('compute-signature')
run_script_module = import_script('run-script')
run_script = run_script_module.run_script
report_utils = import_script('report-utils')
sandbox_merge = import_script('sandbox-merge')


def get_uv_binary(bin_dir: Path) -> str:
    """Get platform-appropriate uv binary path."""
    system = platform.system()

    if system == 'Windows':
        uv_path = bin_dir / 'uv.exe'
    elif system == 'Darwin':
        uv_path = bin_dir / 'uv.mac'
    else:  # Linux and others
        uv_path = bin_dir / 'uv.linux'

    if uv_path.exists():
        return str(uv_path)

    # Fall back to PATH
    return 'uv'


def run_ai_prompt(prompt_path: Path, sandbox_path: Path, report_type: str, template_vars: dict, timeout: int = 1200, req_stem: str | None = None):
    """Run AI prompt in sandbox context."""
    prompt_text = prompt_path.read_text(encoding='utf-8')

    # Always inject standard template vars
    template_vars = dict(template_vars)  # Copy to avoid mutating caller's dict

    # Platform-appropriate uv binary path (in sandbox)
    bin_dir = sandbox_path / 'the-system' / 'bin'
    uv_binary = get_uv_binary(bin_dir)
    template_vars['{{UV_BINARY}}'] = uv_binary

    # Simple template replacement
    for placeholder, value in template_vars.items():
        prompt_text = prompt_text.replace(placeholder, value)

    # Change to sandbox for AI to work there
    original_cwd = os.getcwd()
    os.chdir(sandbox_path)

    try:
        return prompt_ai.get_ai_response_text(
            prompt_text,
            report_type=report_type,
            timeout=timeout,
            req_stem=req_stem
        )
    finally:
        os.chdir(original_cwd)


def run_test_in_sandbox(test_path: Path, sandbox_path: Path) -> int:
    """Run test in sandbox context."""
    # test.py expects to be run from project root
    test_script = sandbox_path / 'the-system' / 'scripts' / 'test.py'

    result = run_script(
        test_script,
        args=[str(test_path)],
        timeout=300,
        cwd=sandbox_path
    )

    return result['exit_code']


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: agent-worker.py <req_file>", file=sys.stderr)
        return 1

    req_file = Path(sys.argv[1])
    req_stem = req_file.stem

    print()
    print(f"=== Agent: {req_file.name} ===")
    print()

    # Get project root (two levels up from script)
    project_root = SCRIPT_DIR.parent.parent.resolve()

    # Derive paths
    test_filename = f"{req_stem}.py"

    sandbox_path = None
    base_snapshot = None

    try:
        # Create sandbox
        print(f"Creating sandbox: ./tmp/{req_stem}/")
        sandbox_path, base_snapshot = sandbox_merge.create_sandbox(req_stem, project_root)

        # Paths within sandbox
        sandbox_req_file = sandbox_path / req_file
        sandbox_test_path = sandbox_path / 'tests' / 'failing' / test_filename

        # Ensure tests subdirectories exist in sandbox
        report_utils.ensure_test_directories(sandbox_path / 'tests')

        # Fix loop
        test_passed = False
        for attempt in range(1, MAX_FIX_ATTEMPTS + 1):
            print(f"Attempt {attempt}/{MAX_FIX_ATTEMPTS} for {test_filename}")

            # Run FIX_AND_TEST prompt
            fix_prompt = SCRIPT_DIR.parent / 'prompts' / 'FIX_AND_TEST.md'

            run_ai_prompt(
                fix_prompt,
                sandbox_path,
                report_type=f'FIX_ATTEMPT{attempt}',
                template_vars={
                    '{{REQ_FILE_PATH}}': str(sandbox_req_file.relative_to(sandbox_path)),
                    '{{TEST_FILE_PATH}}': str(sandbox_test_path.relative_to(sandbox_path)),
                    '{{ATTEMPT}}': str(attempt)
                },
                timeout=1200,
                req_stem=req_stem
            )

            # Find test file (might have been created in a different location)
            actual_test_path = None
            for status in ['failing', 'passing']:
                candidate = sandbox_path / 'tests' / status / test_filename
                if candidate.exists():
                    actual_test_path = candidate
                    break

            if actual_test_path is None:
                print(f"  Test file not created yet")
                continue

            print(f"  [DEBUG] Running test: {actual_test_path}")
            exit_code = run_test_in_sandbox(actual_test_path, sandbox_path)
            print(f"  [DEBUG] Test exit_code = {exit_code}")

            if exit_code == 99:
                print("  Note: Test reported external dependency failure (treating as code bug)")

            if exit_code == 0:
                print("  Test passed!")
                test_passed = True
                break

            print(f"  Test failed (exit {exit_code})")

        if not test_passed:
            print(f"Max attempts reached for {req_file.name}")
            # Copy reports before cleanup
            sandbox_merge.copy_reports_from_sandbox(sandbox_path, project_root)
            # Copy test to failing/ (don't merge code)
            sandbox_merge.copy_test_to_status(sandbox_path, req_stem, 'failing', project_root)
            sandbox_merge.cleanup_sandbox(sandbox_path, base_snapshot)
            return 1

        # Verify test quality
        print("Verifying test quality...")
        verify_prompt = SCRIPT_DIR.parent / 'prompts' / 'VERIFY_TEST.md'

        # Find test again (might have moved)
        actual_test_path = None
        for status in ['failing', 'passing']:
            candidate = sandbox_path / 'tests' / status / test_filename
            if candidate.exists():
                actual_test_path = candidate
                break

        if actual_test_path:
            sig_before = compute_signature.compute_signature([str(actual_test_path)])

            run_ai_prompt(
                verify_prompt,
                sandbox_path,
                report_type='VERIFY',
                template_vars={
                    '{{REQ_FILE_PATH}}': str(sandbox_req_file.relative_to(sandbox_path)),
                    '{{TEST_FILE_PATH}}': str(actual_test_path.relative_to(sandbox_path))
                },
                timeout=600,
                req_stem=req_stem
            )

            sig_after = compute_signature.compute_signature([str(actual_test_path)])

            if sig_before != sig_after:
                print("  Test modified by verification, re-running test...")
                exit_code = run_test_in_sandbox(actual_test_path, sandbox_path)
                if exit_code != 0:
                    print(f"  Test failed after verification changes (exit {exit_code})")
                    # Copy reports, copy test to failing, don't merge code
                    sandbox_merge.copy_reports_from_sandbox(sandbox_path, project_root)
                    sandbox_merge.copy_test_to_status(sandbox_path, req_stem, 'failing', project_root)
                    sandbox_merge.cleanup_sandbox(sandbox_path, base_snapshot)
                    return 1

        # Success! Merge code back and move test to passing
        print("Merging code back to main project...")
        conflicts = sandbox_merge.merge_code_back(sandbox_path, base_snapshot, project_root)

        if conflicts:
            print(f"  Warning: Merge conflicts in {len(conflicts)} files:")
            for f in conflicts:
                print(f"    - {f}")

        # Copy test to passing/
        sandbox_merge.copy_test_to_status(sandbox_path, req_stem, 'passing', project_root)

        # Copy reports
        sandbox_merge.copy_reports_from_sandbox(sandbox_path, project_root)

        # Cleanup
        sandbox_merge.cleanup_sandbox(sandbox_path, base_snapshot)

        print(f"=== Agent complete: {req_file.name} ===")
        return 0

    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"Error: {e}", file=sys.stderr)
        print(error_detail, file=sys.stderr)

        # Write error report to main reports directory
        try:
            reports_dir = project_root / 'reports'
            error_report_path, timestamp = report_utils.get_report_path('AGENT_ERROR', req_stem, reports_dir)

            error_report_content = f"""# Agent Error Report

**Requirement:** {req_file.name}
**Sandbox:** ./tmp/{req_stem}/
**Timestamp:** {timestamp}

## Error

```
{e}
```

## Stack Trace

```
{error_detail}
```
"""
            error_report_path.write_text(error_report_content, encoding='utf-8')
            print(f"Error report: {error_report_path.name}", file=sys.stderr)
        except Exception as report_error:
            print(f"Failed to write error report: {report_error}", file=sys.stderr)

        # Try to copy reports from sandbox before cleanup
        if sandbox_path and sandbox_path.exists():
            try:
                sandbox_merge.copy_reports_from_sandbox(sandbox_path, project_root)
            except Exception as copy_error:
                print(f"Failed to copy sandbox reports: {copy_error}", file=sys.stderr)

        # Try to cleanup
        if sandbox_path and base_snapshot:
            try:
                sandbox_merge.cleanup_sandbox(sandbox_path, base_snapshot)
            except:
                pass

        return 1


if __name__ == '__main__':
    sys.exit(main())
