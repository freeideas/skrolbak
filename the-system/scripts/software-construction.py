# Run via: ./bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Software Construction System

This script orchestrates the complete software construction process:
- Requirements Generation (req-gen.py)
- Code Generation (VIBE_CODE.md prompt)
- Test Preparation and Verification (test-fix-loop.py -> parallel-loop.py)
- Completion and Summary

Exit codes:
  0 - Success (all stages complete)
  1 - Error
"""

import sys
import argparse
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import shutil
import sqlite3
import platform
import importlib.util
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def get_uv_binary() -> str:
    """Get platform-appropriate uv binary path."""
    bin_dir = SCRIPT_DIR.parent / 'bin'
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


# Import run-script utility
_run_script_spec = importlib.util.spec_from_file_location("run_script", SCRIPT_DIR / "run-script.py")
run_script_module = importlib.util.module_from_spec(_run_script_spec)
_run_script_spec.loader.exec_module(run_script_module)
run_script = run_script_module.run_script

# Import helper scripts
def import_script(script_name: str):
    script_path = SCRIPT_DIR / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name.replace('-', '_'), script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


prompt_ai = import_script('prompt-ai')
test_fix_loop = import_script('test-fix-loop')


def print_section(title: str):
    """Print section header."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)
    print()


def run_ai_prompt(prompt_path: Path, report_type: str, timeout=600, extra_context: str | None = None):
    """Run AI prompt and return result."""
    print(f"  Running prompt: {prompt_path.name}")
    prompt_text = Path(prompt_path).read_text(encoding='utf-8')

    if extra_context:
        prompt_text = f"{prompt_text.rstrip()}\n\n---\n\n## Context\n\n{extra_context.strip()}\n"

    # Inject standard template vars
    prompt_text = prompt_text.replace('{{UV_BINARY}}', get_uv_binary())

    return prompt_ai.get_ai_response_text(
        prompt_text,
        report_type=report_type,
        timeout=timeout
    )


# ============================================================================
# CODE GENERATION
# ============================================================================

def generate_code() -> bool:
    """Generate implementation code from documentation."""
    print_section("CODE GENERATION")

    print("Ensuring compiler is available...")
    compiler_prompt_path = SCRIPT_DIR.parent / 'prompts' / 'DOWNLOAD_COMPILER.md'

    if not compiler_prompt_path.exists():
        print(f"  Warning: Prompt not found: {compiler_prompt_path}")
        print(f"  Skipping compiler check")
    else:
        try:
            run_ai_prompt(compiler_prompt_path, report_type='download_compiler', timeout=600)
            print("  OK Compiler check complete")
            print()
        except Exception as e:
            print(f"  Warning: Error checking compiler: {e}", file=sys.stderr)
            print()

    print("AI generating code from README/specs...")

    prompt_path = SCRIPT_DIR.parent / 'prompts' / 'VIBE_CODE.md'
    if not prompt_path.exists():
        print(f"  Error: Prompt not found: {prompt_path}", file=sys.stderr)
        return False

    Path('./code').mkdir(exist_ok=True)

    try:
        run_ai_prompt(prompt_path, report_type='vibe_code', timeout=3600)
        print("  OK AI generated code")
        print()
    except Exception as e:
        print(f"  Error generating code: {e}", file=sys.stderr)
        return False

    return True


# ============================================================================
# COMPLETION
# ============================================================================

def complete_build() -> bool:
    """Verify completion and generate summary."""
    print_section("COMPLETION")

    print("Generating summary...")

    db_path = './tmp/reqs.sqlite'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM req_definitions")
        num_reqs = cursor.fetchone()[0]
        conn.close()
    else:
        num_reqs = 0

    tests = list(Path('./tests').rglob('*.py'))
    num_tests = len(tests)

    released_dir = Path('./released')
    if released_dir.exists():
        artifacts = sorted([f for f in released_dir.rglob('*') if f.is_file()])
    else:
        artifacts = []

    print()
    print("=" * 70)
    print("BUILD SUMMARY")
    print("=" * 70)
    print(f"Requirements defined: {num_reqs}")
    print(f"Tests passing: {num_tests}")
    print(f"Artifacts in ./released/: {len(artifacts)}")

    if artifacts:
        print()
        print("Artifacts:")
        for artifact in artifacts:
            rel_path = artifact.relative_to(released_dir)
            size = artifact.stat().st_size
            print(f"  - {rel_path} ({size:,} bytes)")

    print("=" * 70)
    print()

    return True


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Software Construction System")
    parser.add_argument(
        '--skip-reqs',
        action='store_true',
        help='Skip requirement generation and any edits to ./reqs/ documents (use existing reqs instead).'
    )
    parser.add_argument(
        '--skip-to-testing',
        action='store_true',
        help='Skip directly to test generation/verification loop (skip requirements, code generation, and test staging).'
    )
    args = parser.parse_args()

    skip_requirements = args.skip_reqs or args.skip_to_testing
    skip_code_generation = args.skip_to_testing
    skip_reqs_reason = '--skip-to-testing' if args.skip_to_testing else '--skip-reqs'

    print()
    print("=" * 70)
    print("SOFTWARE CONSTRUCTION SYSTEM")
    print("=" * 70)
    print()
    print("This will run the complete build process:")
    if skip_requirements:
        print(f"  - Requirements Generation (skipped via {skip_reqs_reason})")
    else:
        print("  - Requirements Generation")
    if skip_code_generation:
        print("  - Code Generation (skipped via --skip-to-testing)")
    else:
        print("  - Code Generation")
    print("  - Test Preparation")
    print("  - Test Generation and Verification")
    print("  - Completion and Summary")
    print()

    # Change to project root (two levels up from this script)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    os.chdir(project_root)
    print(f"Working directory: {Path.cwd()}")
    print()

    # Copy global_CLAUDE.md to ./CLAUDE.md if it doesn't exist
    claude_md = Path('./CLAUDE.md')
    global_claude_md = SCRIPT_DIR.parent / 'prompts' / 'global_CLAUDE.md'
    if not claude_md.exists() and global_claude_md.exists():
        shutil.copy2(global_claude_md, claude_md)
        print(f"Created CLAUDE.md from {global_claude_md.name}")
        print()

    # Copy global_CODEX.md to ./CODEX.md if it doesn't exist
    codex_md = Path('./CODEX.md')
    global_codex_md = SCRIPT_DIR.parent / 'prompts' / 'global_CODEX.md'
    if not codex_md.exists() and global_codex_md.exists():
        shutil.copy2(global_codex_md, codex_md)
        print(f"Created CODEX.md from {global_codex_md.name}")
        print()

    # Cleanup temporary directories
    cleanup_script = SCRIPT_DIR / 'cleanup.py'
    result = run_script(cleanup_script, stream=True)
    if not result['success']:
        print(f"Warning: Cleanup failed (exit {result['exit_code']})", file=sys.stderr)
        print()

    if skip_requirements:
        print("=" * 70)
        print(f"SKIP REQUIREMENTS GENERATION ({skip_reqs_reason})")
        print("=" * 70)
        print()
        print("Using existing ./reqs/ documents; no edits will be made to requirements.")
        print()
    else:
        print("=" * 70)
        print("STARTING REQUIREMENTS GENERATION")
        print("=" * 70)
        print()

        req_gen_script = SCRIPT_DIR / 'req-gen.py'
        result = run_script(req_gen_script, timeout=10800, stream=True)  # 3 hours

        if result['exit_code'] != 0:
            if result['exit_code'] == 124:
                print()
                print("=" * 70)
                print("WARNING  REQUIREMENTS GENERATION TIMED OUT (continuing with partial requirements)")
                print("=" * 70)
                print()
            else:
                print()
                print("=" * 70)
                print("FAIL REQUIREMENTS GENERATION FAILED OR ABORTED")
                print("=" * 70)
                print()
                return result['exit_code']

    if skip_code_generation:
        print("=" * 70)
        print("SKIP CODE GENERATION (--skip-to-testing)")
        print("=" * 70)
        print()
        print("Using existing code in ./code/; no regeneration performed.")
        print()
    else:
        if not generate_code():
            print()
            print("FAIL Code generation failed")
            return 1

    exit_code = test_fix_loop.run_test_fix_loop()
    if exit_code != 0:
        return exit_code

    if not complete_build():
        print()
        print("FAIL Completion failed")
        return 1

    # Success
    print()
    print("=" * 70)
    print("OK SOFTWARE CONSTRUCTION COMPLETE")
    print("=" * 70)
    print()
    print("All stages completed successfully!")
    print("Your working software is in the ./released/ directory")
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
