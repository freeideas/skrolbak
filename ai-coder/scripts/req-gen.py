# Run via: ./bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Requirements Generation

This script handles:
- README/Specs Quality Check
- Requirements Generation with iterative refinement

Exit codes:
  0 - Success (requirements generated)
  1 - Error
"""

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import shutil
import importlib.util
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Import sibling modules (handle hyphenated filenames)
SCRIPT_DIR = Path(__file__).parent
MAX_PARALLEL_WORKERS = 5


def import_script(script_name):
    """Import a script module by filename (handles hyphens)."""
    script_path = SCRIPT_DIR / f"{script_name}.py"
    spec = importlib.util.spec_from_file_location(script_name.replace('-', '_'), script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Import required modules
compute_signature = import_script('compute-signature')
fix_duplicate_req_ids = import_script('fix-duplicate-req-ids')
prompt_ai = import_script('prompt-ai')
report_utils = import_script('report-utils')


def print_section(title):
    """Print a formatted section header."""
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)
    print()


def _write_req_fix_summary(results: dict, errors: list, max_iterations: int):
    """Write a summary report for the parallel req fix operation."""
    report_path, timestamp = report_utils.get_report_path('REQ_FIX_SUMMARY')

    # Build rows for the table
    req_rows = []
    for req_name in sorted(results.keys()):
        converged, iters = results[req_name]
        status_icon, status = ('✓', 'CONVERGED') if converged else ('⚠', 'MAX_ITERS')
        req_rows.append(f"| {req_name} | {status_icon} {status} | {iters} |")

    # Add error entries
    for error in errors:
        req_name = error.split(':')[0] if ':' in error else error
        req_rows.append(f"| {req_name} | ✗ ERROR | - |")

    req_table = '\n'.join(req_rows) if req_rows else '| (no requirements) | - | - |'

    total_reqs = len(results) + len(errors)
    converged_count = sum(1 for (c, _) in results.values() if c)
    max_iters_count = sum(1 for (c, _) in results.values() if not c)
    error_count = len(errors)

    report_content = f"""# Requirement Fix Summary

**Timestamp:** {timestamp}
**Max Iterations:** {max_iterations}

## Summary

- Total requirements: {total_reqs}
- Converged: {converged_count}
- Hit max iterations: {max_iters_count}
- Errors: {error_count}

## Requirements Status

| Requirement | Status | Iterations |
|-------------|--------|------------|
{req_table}
"""

    report_path.write_text(report_content, encoding='utf-8')
    print(f"\n  Summary report: {report_path}")


def prepare_workspace():
    """Prepare workspace (clean reports, create directories)."""
    print_section("Preparing Workspace")

    # Create necessary directories
    for directory in ['./reqs', './reports', './tmp']:
        Path(directory).mkdir(exist_ok=True)
        print(f"OK Directory ready: {directory}")

    print()




def run_ai_prompt(prompt_name, report_type, timeout=600, model_tier="hi"):
    """Helper to run an AI prompt and return the response."""
    prompt_text = load_prompt(prompt_name)
    if not prompt_text:
        raise FileNotFoundError(f"Prompt not found: {prompt_name}")

    print(f"  Running prompt: {prompt_name}")

    # Run the prompt
    response = prompt_ai.get_ai_response_text(
        prompt_text,
        report_type=report_type,
        timeout=timeout,
        model_tier=model_tier
    )

    return response


def load_prompt(name: str) -> str | None:
    """Load a prompt file from @ai-coder/prompts/. Return None if not found."""
    path = SCRIPT_DIR.parent / 'prompts' / name
    if not path.exists():
        print(f"  Warning: Prompt not found: {path}")
        return None
    return path.read_text(encoding='utf-8')


def _generate_diff_report(backup_dir: Path, report_path: Path) -> str:
    """
    Generate a unified diff between backed-up files and current files.
    Returns the diff text and writes it to report file.
    """
    import difflib

    diffs = []
    project_root = Path.cwd()

    # Check README.md
    backup_readme = backup_dir / 'README.md'
    current_readme = project_root / 'README.md'

    if backup_readme.exists() and current_readme.exists():
        backup_text = backup_readme.read_text(encoding='utf-8').splitlines(keepends=True)
        current_text = current_readme.read_text(encoding='utf-8').splitlines(keepends=True)

        if backup_text != current_text:
            diff_lines = difflib.unified_diff(
                backup_text,
                current_text,
                fromfile='README.md (original)',
                tofile='README.md (modified)',
                lineterm=''
            )
            diffs.extend(diff_lines)

    # Check specs directory
    backup_specs = backup_dir / 'specs'
    current_specs = project_root / 'specs'

    if backup_specs.exists() and current_specs.exists():
        # Get all files in both directories
        backup_files = sorted(backup_specs.rglob('*.md'))
        current_files = sorted(current_specs.rglob('*.md'))

        all_files = set()
        for f in backup_files:
            all_files.add(f.relative_to(backup_specs))
        for f in current_files:
            all_files.add(f.relative_to(current_specs))

        for rel_path in sorted(all_files):
            backup_file = backup_specs / rel_path
            current_file = current_specs / rel_path

            backup_exists = backup_file.exists()
            current_exists = current_file.exists()

            if backup_exists and current_exists:
                backup_text = backup_file.read_text(encoding='utf-8').splitlines(keepends=True)
                current_text = current_file.read_text(encoding='utf-8').splitlines(keepends=True)

                if backup_text != current_text:
                    diff_lines = difflib.unified_diff(
                        backup_text,
                        current_text,
                        fromfile=f'specs/{rel_path} (original)',
                        tofile=f'specs/{rel_path} (modified)',
                        lineterm=''
                    )
                    diffs.extend(diff_lines)
            elif backup_exists and not current_exists:
                diffs.append(f"--- specs/{rel_path} (deleted)\n")
                diffs.append("+++ /dev/null\n")
            elif not backup_exists and current_exists:
                diffs.append(f"--- /dev/null\n")
                diffs.append(f"+++ specs/{rel_path} (created)\n")

    diff_text = ''.join(diffs)
    return diff_text


def check_requirements_quality():
    """
    README/Specs Quality Check with iterative refinement

    Returns: True if successful, False if should exit
    """
    print_section("README/SPECS QUALITY CHECK")

    print("Computing signature BEFORE quality check...")
    signature_before = compute_signature.compute_signature(['README.md', './specs'])
    print(f"  Signature BEFORE: {signature_before[:16]}...")
    print()

    print("Creating timestamped backup of README and specs...")
    timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')[:-3]  # Millisecond precision
    project_root = Path.cwd()
    backup_dir = project_root / 'tmp' / f'backup-readme-specs-{timestamp}'
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Backup README.md
    if (project_root / 'README.md').exists():
        shutil.copy2(project_root / 'README.md', backup_dir / 'README.md')

    # Backup specs directory
    specs_dir = project_root / 'specs'
    if specs_dir.exists():
        backup_specs = backup_dir / 'specs'
        shutil.copytree(specs_dir, backup_specs, dirs_exist_ok=True)

    print(f"  Backed up to: {backup_dir.relative_to(project_root)}")
    print()

    print("AI checking README/specs quality (iterative refinement, max 5 iterations)...")
    prompt_template = load_prompt('FIX_README-SPECS.md')
    if not prompt_template:
        print(f"  Skipping quality check")
        return True

    try:
        # Run the quality check in a signature-stabilize loop
        converged, iterations, final_signature = prompt_ai.run_until_stable(
            signature_paths=['README.md', './specs'],
            prompts=[(prompt_template, 'readme_specs_quality')],
            max_iterations=5,
            timeout=900,  # 15 minutes per iteration
            parallel=False,
            verbose=True,
            model_tier="hi"
        )

        if converged:
            print(f"  OK AI stabilized after {iterations} iteration(s)")
        else:
            print(f"  AI completed maximum {iterations} iterations")
        print()
    except Exception as e:
        print(f"  Error running quality check: {e}", file=sys.stderr)
        return False

    print("Computing signature AFTER quality check...")
    signature_after = compute_signature.compute_signature(['README.md', './specs'])
    print(f"  Signature AFTER: {signature_after[:16]}...")
    print()

    if signature_before != signature_after:
        print("AI made changes to README.md and/or ./specs/")
        print()

        # Generate diff report
        print("Generating diff report...")
        report_path, report_timestamp = report_utils.get_report_path('README_SPECS_CHANGES')
        diff_text = _generate_diff_report(backup_dir, report_path)

        # Write diff to report file
        report_content = f"""# README/Specs Changes Summary

**Timestamp:** {report_timestamp}
**Backup Location:** {backup_dir.relative_to(project_root)}

---

## Changes

```diff
{diff_text}
```

---

## What This Means

The AI has refined your README.md and/or specs/ files through up to 5 iterations to:
- Fix internal contradictions
- Clarify vague specifications
- Remove untestable performance claims
- Ensure documentation is clear and testable

Please review these changes to ensure they align with your intended design.
"""

        report_path.write_text(report_content, encoding='utf-8')
        print(f"  Diff report written to: {report_path}")
        print()

        print("=" * 70)
        print("*** REVIEW REQUIRED ***")
        print("=" * 70)
        print()
        print("The AI has iteratively refined your README.md and/or specs/ files.")
        print()
        print("Please review the changes:")
        print(f"  - See detailed diff in: ./reports/ (latest report)")
        print(f"  - Backup of originals: {backup_dir.relative_to(project_root)}")
        print()
        print("  - Press ENTER to accept these changes and continue")
        print("  - Press CTRL-C to abort and revise manually")
        print()
        print("=" * 70)
        sys.stdout.flush()  # Force output to appear immediately

        try:
            user_input = input("Your choice (press ENTER to continue): ")
            print()
            print("Continuing with AI changes...")
            print()
        except KeyboardInterrupt:
            print()
            print()
            print("Aborted by user. Please revise documentation and re-run.")
            print(f"Original files backed up to: {backup_dir}")
            return False
    else:
        print("No changes made to README.md or ./specs/")
        print()

    return True


def generate_requirements():
    """
    Requirements Generation

    Returns: True if successful, False on error
    """
    print_section("REQUIREMENTS GENERATION")

    print("Preparing requirements directory...")
    reqs_dir = Path('./reqs')
    reqs_dir.mkdir(exist_ok=True)
    print(f"  OK Directory ready: ./reqs/")
    print()

    # Check if requirements already exist
    existing_reqs = list(reqs_dir.glob('*.md'))
    if existing_reqs:
        print(f"Found {len(existing_reqs)} existing requirement files in ./reqs/")
        print("Skipping stub generation (use existing requirements)")
        print()
    else:
        # No existing requirements - generate from scratch
        print("Preparing ./tmp/new-reqs/ directory...")
        new_reqs_dir = Path('./tmp/new-reqs')
        if new_reqs_dir.exists():
            shutil.rmtree(new_reqs_dir)
        new_reqs_dir.mkdir(parents=True, exist_ok=True)

        # Copy reference files from prompts directory (build-output.md and any *-REQ.md stubs)
        # This ensures the AI sees these existing templates and won't duplicate them
        prompts_dir = SCRIPT_DIR.parent / 'prompts'

        # Always seed build-output.md if it exists (required for predictable build handling)
        build_output_src = prompts_dir / 'build-output.md'
        if build_output_src.exists():
            dest = new_reqs_dir / build_output_src.name
            shutil.copy2(build_output_src, dest)
            print(f"  OK Seeded {build_output_src.name} to ./tmp/new-reqs/ (AI will see this and not duplicate)")

        # Copy any other *-REQ.md stub files
        stub_files = list(prompts_dir.glob('*-REQ.md'))
        for stub_file in stub_files:
            dest = new_reqs_dir / stub_file.name
            shutil.copy2(stub_file, dest)
            print(f"  OK Copied {stub_file.name} to ./tmp/new-reqs/")

        if not stub_files:
            print(f"  No stub files found in {prompts_dir}")
        print()

        print("AI identifying concerns and creating stub files...")
        try:
            response = run_ai_prompt(
                'WRITE_NEW_REQS.md',
                report_type='write_new_reqs',
                timeout=900,  # 15 minutes
                model_tier="hi"
            )
            print(f"  OK AI created stub files")
            print()
        except Exception as e:
            print(f"  Error creating stub files: {e}", file=sys.stderr)
            return False

        print("AI writing requirements for each stub file (parallel)...")
        write_req_template = load_prompt('WRITE_NEW_REQ.md')
        if not write_req_template:
            return False

        # Get all stub files in ./tmp/new-reqs/
        stub_files = sorted(new_reqs_dir.glob('*.md'))
        if not stub_files:
            print(f"  Warning: No stub files found in ./tmp/new-reqs/")
            return False

        print(f"  Found {len(stub_files)} stub files")

        write_results = {}
        write_errors = []

        def write_req_for_stub(stub_file):
            """Run WRITE_NEW_REQ.md for a single stub file."""
            try:
                prompt_text = write_req_template.replace('{{STUB_FILE_PATH}}', str(stub_file))

                response = prompt_ai.get_ai_response_text(
                    prompt_text,
                    report_type='WRITE_NEW_REQ',
                    timeout=900,  # 15 minutes per file
                    req_stem=stub_file.stem,
                    model_tier="hi"
                )
                write_results[stub_file.name] = True
            except Exception as e:
                write_errors.append(f"{stub_file.name}: {e}")

        # Run in parallel with limited concurrency
        with ThreadPoolExecutor(max_workers=MAX_PARALLEL_WORKERS) as executor:
            executor.map(write_req_for_stub, stub_files)

        # Report results
        print()
        for stub_name in sorted(write_results.keys()):
            print(f"    OK {stub_name}")

        if write_errors:
            print()
            for error in write_errors:
                print(f"    ERROR {error}", file=sys.stderr)
            return False

        print()

        print("Moving completed requirements to ./reqs/...")
        completed_files = sorted(new_reqs_dir.glob('*.md'))
        for req_file in completed_files:
            dest = reqs_dir / req_file.name
            shutil.copy2(req_file, dest)
            print(f"  OK {req_file.name} -> ./reqs/")
        print()

    print("Ensuring all specs have corresponding requirements...")
    coverage_prompt_text = load_prompt('REQ_ENSURE_COVERAGE.md')
    if coverage_prompt_text:
        converged, iterations, _ = prompt_ai.run_until_stable(
            signature_paths=['./reqs'],
            prompts=[(coverage_prompt_text, 'req_ensure_coverage')],
            max_iterations=3,
            timeout=900,
            parallel=False,
            verbose=True,
            model_tier="hi"
        )
        if converged:
            print(f"  OK Coverage complete after {iterations} iteration(s)")
        else:
            print(f"  Coverage reached max iterations ({iterations})")
        print()

    print("Fixing requirement files (parallel)...")
    print()

    max_iterations = int(os.environ.get('MAX_REQ_ITERATIONS', '5'))

    # Load REQ_FIX.md template
    req_fix_template = load_prompt('REQ_FIX.md')
    if not req_fix_template:
        return False

    # Get all req files
    req_files = sorted(Path('./reqs').glob('*.md'))
    if not req_files:
        print(f"  Warning: No requirement files found in ./reqs/")
        return False

    print(f"  Found {len(req_files)} requirement files")

    # Run REQ_FIX.md for each file in parallel, each with its own signature loop
    results = {}
    errors = []

    def fix_req_file(req_file):
        """Run REQ_FIX.md for a single req file until stable."""
        try:
            # Substitute the file path into the template
            prompt_text = req_fix_template.replace('{{REQ_FILE_PATH}}', str(req_file))
            report_type = f"req_fix_{req_file.stem}"

            converged, iters, _ = prompt_ai.run_until_stable(
                signature_paths=[str(req_file)],
                prompts=[(prompt_text, report_type)],
                max_iterations=max_iterations,
                timeout=600,
                parallel=False,
                verbose=False,  # Reduce noise from parallel runs
                model_tier="hi"
            )
            results[req_file.name] = (converged, iters)
        except Exception as e:
            errors.append(f"{req_file.name}: {e}")

    # Run in parallel with limited concurrency
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_WORKERS) as executor:
        executor.map(fix_req_file, req_files)

    # Report results
    print()
    for req_name, (converged, iters) in sorted(results.items()):
        status = "OK" if converged else "MAX"
        print(f"    {status} {req_name} ({iters} iteration(s))")

    if errors:
        print()
        for error in errors:
            print(f"    ERROR {error}", file=sys.stderr)

    # Write summary report for parallel req fix
    _write_req_fix_summary(results, errors, max_iterations)

    print()

    # Fix duplicate $REQ_IDs after REQ_FIX loop (may have introduced duplicates)
    print("Fixing duplicate $REQ_IDs...")
    try:
        fixes = fix_duplicate_req_ids.scan_and_fix_duplicates()
        if fixes > 0:
            print(f"  OK Fixed {fixes} duplicate(s)")
        else:
            print(f"  OK No duplicates found")
    except Exception as e:
        print(f"  Warning: Error fixing duplicates: {e}", file=sys.stderr)
    print()

    print("AI ordering requirements by dependency...")
    try:
        response = run_ai_prompt(
            'ORDER_REQS.md',
            report_type='order_reqs',
            timeout=600,
            model_tier="hi"
        )
        print(f"  OK AI ordered requirements")
    except Exception as e:
        print(f"  Warning: Error ordering requirements: {e}", file=sys.stderr)

    print()

    print("Requirements generation complete")
    print()

    # List generated requirements
    req_files = sorted(Path('./reqs').glob('*.md'))
    if req_files:
        print(f"Generated {len(req_files)} requirement files:")
        for req_file in req_files:
            print(f"  - {req_file.name}")
        print()
    else:
        print("  Warning: No requirement files found in ./reqs/", file=sys.stderr)
        return False

    return True


def main():
    """Main entry point."""
    print()
    print("=" * 70)
    print("REQUIREMENTS GENERATION")
    print("=" * 70)

    # Change to project root (two levels up from this script)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    os.chdir(project_root)
    print(f"Working directory: {Path.cwd()}")
    print()

    prepare_workspace()

    if not check_requirements_quality():
        print()
        print("FAIL Quality check failed or was aborted")
        return 1

    if not generate_requirements():
        print()
        print("FAIL Requirements generation failed")
        return 1

    # Success
    print()
    print("=" * 70)
    print("OK REQUIREMENTS GENERATION COMPLETE")
    print("=" * 70)
    print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
