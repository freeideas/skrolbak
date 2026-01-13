# Run via: ./ai-coder/bin/uv.exe run --script this_file.py <req_file>
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Agent Worker

Works on a single requirement directly on the project (no sandbox).
1. Fix code/test until test passes (FIX_AND_TEST.md)
2. Verify test quality (VERIFY_TEST.md)
3. Move test to appropriate status directory

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


def run_ai_prompt(prompt_path: Path, project_root: Path, report_type: str, template_vars: dict, timeout: int = 1200, req_stem: str | None = None):
    """Run AI prompt in project context."""
    prompt_text = prompt_path.read_text(encoding='utf-8')

    # Always inject standard template vars
    template_vars = dict(template_vars)  # Copy to avoid mutating caller's dict

    # Platform-appropriate uv binary path
    bin_dir = project_root / 'ai-coder' / 'bin'
    uv_binary = get_uv_binary(bin_dir)
    template_vars['{{UV_BINARY}}'] = uv_binary

    # Simple template replacement
    for placeholder, value in template_vars.items():
        prompt_text = prompt_text.replace(placeholder, value)

    # Ensure we're in project root
    original_cwd = os.getcwd()
    os.chdir(project_root)

    try:
        return prompt_ai.get_ai_response_text(
            prompt_text,
            report_type=report_type,
            timeout=timeout,
            req_stem=req_stem
        )
    finally:
        os.chdir(original_cwd)


def run_test(test_path: Path, project_root: Path) -> int:
    """Run test in project context."""
    test_script = project_root / 'ai-coder' / 'scripts' / 'test.py'

    result = run_script(
        test_script,
        args=[str(test_path)],
        timeout=300,
        cwd=project_root
    )

    return result['exit_code']


def move_test_to_status(req_stem: str, target_status: str, project_root: Path):
    """Move test to the target status directory (passing/ or failing/)."""
    tests_dir = project_root / 'tests'
    test_filename = f"{req_stem}.py"

    # Find current test location
    source_path = None
    for status in ['failing', 'passing']:
        candidate = tests_dir / status / test_filename
        if candidate.exists():
            source_path = candidate
            break

    if source_path is None:
        print(f"  Warning: Test file {test_filename} not found")
        return

    target_dir = tests_dir / target_status
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / test_filename

    # If already in correct location, nothing to do
    if source_path == target_path:
        return

    # Move the file
    source_path.rename(target_path)
    print(f"  Test moved to {target_status}/")


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

    # Ensure we're in project root
    os.chdir(project_root)

    # Derive paths
    test_filename = f"{req_stem}.py"

    try:
        # Ensure tests subdirectories exist
        report_utils.ensure_test_directories(project_root / 'tests')

        # Find or create test in failing/
        test_path = project_root / 'tests' / 'failing' / test_filename

        # Fix loop
        test_passed = False
        for attempt in range(1, MAX_FIX_ATTEMPTS + 1):
            print(f"Attempt {attempt}/{MAX_FIX_ATTEMPTS} for {test_filename}")

            # Run FIX_AND_TEST prompt
            fix_prompt = SCRIPT_DIR.parent / 'prompts' / 'FIX_AND_TEST.md'

            # Protected paths that AI should not modify
            protected_paths = """- `./ai-coder/*` - system scripts and prompts
- `./reqs/*` - requirement files (source of truth)
- `./specs/*` - specification files (source of truth)
- `./docs/*` - documentation files (source of truth)
- `./README.md` - project readme (source of truth)
- `./CLAUDE.md` - AI instructions
- `./CODEX.md` - AI instructions"""

            run_ai_prompt(
                fix_prompt,
                project_root,
                report_type=f'FIX_ATTEMPT{attempt}',
                template_vars={
                    '{{REQ_FILE_PATH}}': str(req_file),
                    '{{TEST_FILE_PATH}}': f'tests/failing/{test_filename}',
                    '{{ATTEMPT}}': str(attempt),
                    '{{PROTECTED_PATHS}}': protected_paths
                },
                timeout=1200,
                req_stem=req_stem
            )

            # Find test file (might have been created in a different location)
            actual_test_path = None
            for status in ['failing', 'passing']:
                candidate = project_root / 'tests' / status / test_filename
                if candidate.exists():
                    actual_test_path = candidate
                    break

            if actual_test_path is None:
                print(f"  Test file not created yet")
                continue

            print(f"  Running test: {actual_test_path.relative_to(project_root)}")
            exit_code = run_test(actual_test_path, project_root)

            if exit_code == 99:
                print("  Note: Test reported external dependency failure (treating as code bug)")

            if exit_code == 0:
                print("  Test passed!")
                test_passed = True
                break

            print(f"  Test failed (exit {exit_code})")

        if not test_passed:
            print(f"Max attempts reached for {req_file.name}")
            # Make sure test is in failing/
            move_test_to_status(req_stem, 'failing', project_root)
            return 1

        # Verify test quality
        print("Verifying test quality...")
        verify_prompt = SCRIPT_DIR.parent / 'prompts' / 'VERIFY_TEST.md'

        # Find test again (might have moved)
        actual_test_path = None
        for status in ['failing', 'passing']:
            candidate = project_root / 'tests' / status / test_filename
            if candidate.exists():
                actual_test_path = candidate
                break

        if actual_test_path:
            sig_before = compute_signature.compute_signature([str(actual_test_path)])

            run_ai_prompt(
                verify_prompt,
                project_root,
                report_type='VERIFY',
                template_vars={
                    '{{REQ_FILE_PATH}}': str(req_file),
                    '{{TEST_FILE_PATH}}': str(actual_test_path.relative_to(project_root))
                },
                timeout=600,
                req_stem=req_stem
            )

            sig_after = compute_signature.compute_signature([str(actual_test_path)])

            if sig_before != sig_after:
                print("  Test modified by verification, re-running test...")
                exit_code = run_test(actual_test_path, project_root)
                if exit_code != 0:
                    print(f"  Test failed after verification changes (exit {exit_code})")
                    move_test_to_status(req_stem, 'failing', project_root)
                    return 1

        # Success! Move test to passing/
        move_test_to_status(req_stem, 'passing', project_root)

        print(f"=== Agent complete: {req_file.name} ===")
        return 0

    except Exception as e:
        error_detail = traceback.format_exc()
        print(f"Error: {e}", file=sys.stderr)
        print(error_detail, file=sys.stderr)

        # Write error report
        try:
            reports_dir = project_root / 'reports'
            error_report_path, timestamp = report_utils.get_report_path('AGENT_ERROR', req_stem, reports_dir)

            error_report_content = f"""# Agent Error Report

**Requirement:** {req_file.name}
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

        return 1


if __name__ == '__main__':
    sys.exit(main())
