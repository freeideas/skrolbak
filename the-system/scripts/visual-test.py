# Run via: ./the-system/bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

"""
Visual verification testing using AI.

Asks AI to examine a screenshot and verify it matches a description.
If it doesn't match, AI modifies the code to fix it.
Test passes if code is unchanged (already matched), fails if code was modified.

Usage:
    visual-test.py <image_file> <description> --test-script <path>

Examples:
    visual-test.py ./tmp/screenshot.png "A login form with blue button" --test-script ./tests/passing/03_visual.py
    visual-test.py ./tmp/app.png "Dark theme with sidebar" --test-script ./tests/passing/ui_test.py

Exit codes:
    0 - Visual verification passed (code unchanged)
    1 - Visual verification failed (code was modified to fix)
    2 - Error (code path doesn't exist, or other error)

This script can also be imported and used as a module:
    from visual_test import check_visual
    passed = check_visual(
        image_file="./tmp/screenshot.png",
        description="A login form with blue button",
        test_script="./tests/passing/03_visual.py"
    )
"""

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import argparse
import shutil
from datetime import datetime
from pathlib import Path

# Change to project root (two levels up from this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
os.chdir(PROJECT_ROOT)


def import_script(script_name):
    """Import a script from the same directory as a module."""
    import importlib.util
    script_path = SCRIPT_DIR / f'{script_name}.py'
    spec = importlib.util.spec_from_file_location(script_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Import required modules
prompt_ai = import_script('prompt-ai')
compute_signature = import_script('compute-signature')


def check_visual(
    image_file: str,
    description: str,
    test_script: str,
    code_path: str = './code',
    timeout: int = 600
) -> tuple:
    """
    Check if a screenshot matches a description using AI visual verification.

    If the screenshot doesn't match, AI modifies the code to fix it.
    Test passes if code is unchanged (already matched).

    Args:
        image_file: Path to the image file to examine
        description: Expected visual description to match against
        test_script: Path to the test script (AI can reference this for screenshot examples)
        code_path: Path to code directory (default: ./code)
        timeout: Maximum seconds for AI analysis (default: 600)

    Returns:
        tuple: (passed: bool, explanation: str)
            - passed: True if code unchanged (matched), False if modified (was fixed)
            - explanation: Description of what happened

    Raises:
        RuntimeError: If AI execution fails
        FileNotFoundError: If image file, test script, or prompt template doesn't exist
    """
    image_path = Path(image_file)
    test_script_path = Path(test_script)
    code_path = Path(code_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image file does not exist: {image_path}")

    if not test_script_path.exists():
        raise FileNotFoundError(f"Test script does not exist: {test_script_path}")

    if not code_path.exists():
        raise FileNotFoundError(f"Code path does not exist: {code_path}")

    # Copy screenshot to reports directory with timestamped filename
    reports_dir = Path("./reports")
    reports_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")[:-3]  # milliseconds
    image_ext = image_path.suffix  # preserve original extension (.png, .jpg, etc.)
    report_image_name = f"{timestamp}_visual_test{image_ext}"
    report_image_path = reports_dir / report_image_name
    shutil.copy2(image_path, report_image_path)

    print(f"\nVisual verification test")
    print(f"  Image: {image_path}")
    print(f"  Report copy: {report_image_path}")
    print(f"  Description: {description}")
    print(f"  Test script: {test_script_path}")
    print(f"  Code path: {code_path}")
    print()

    # Take signature BEFORE
    print("Computing signature BEFORE visual check...")
    sig_before = compute_signature.compute_signature([str(code_path)])
    print(f"  Signature BEFORE: {sig_before[:16]}...")
    print()

    # Load prompt template
    prompt_template_path = SCRIPT_DIR.parent / 'prompts' / 'VISUAL_TEST.md'
    if not prompt_template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {prompt_template_path}")

    prompt_template = prompt_template_path.read_text(encoding='utf-8')

    # Fill in template variables
    prompt_text = prompt_template.replace('{IMAGE_FILE}', str(image_path.resolve()))
    prompt_text = prompt_text.replace('{DESCRIPTION}', description)
    prompt_text = prompt_text.replace('{TEST_SCRIPT}', str(test_script_path.resolve()))
    prompt_text = prompt_text.replace('{CODE_PATH}', str(code_path))

    # Run AI prompt
    print("Running AI visual inspection...")
    try:
        response = prompt_ai.get_ai_response_text(
            prompt_text,
            report_type='visual_test',
            timeout=timeout
        )
        print("AI inspection completed")
        print()
    except Exception as e:
        raise RuntimeError(f"AI execution failed: {e}")

    # Take signature AFTER
    print("Computing signature AFTER visual check...")
    sig_after = compute_signature.compute_signature([str(code_path)])
    print(f"  Signature AFTER: {sig_after[:16]}...")
    print()

    # Compare signatures
    if sig_before == sig_after:
        explanation = "Code unchanged - screenshot already matches expected description"
        print(f"OK VISUAL TEST PASSED")
        print()
        print(explanation)
        print()
        return (True, explanation)
    else:
        explanation = "Code was modified - AI fixed the code to match expected description"
        print(f"X VISUAL TEST FAILED")
        print()
        print(explanation)
        print("Review the changes in the code to see what was fixed.")
        print()
        return (False, explanation)


def main():
    parser = argparse.ArgumentParser(
        description='Visual verification testing using AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./tmp/screenshot.png "A login form with blue button" --test-script ./tests/passing/03_visual.py
  %(prog)s ./tmp/app.png "Dark theme with sidebar" --test-script ./tests/passing/ui_test.py --timeout 600
        """
    )
    parser.add_argument(
        'image_file',
        help='Path to the image file to examine'
    )
    parser.add_argument(
        'description',
        help='Expected visual description to match against'
    )
    parser.add_argument(
        '--test-script',
        required=True,
        help='Path to the test script (AI references this for screenshot examples)'
    )
    parser.add_argument(
        '--code-path',
        default='./code',
        help='Path to code directory (default: ./code)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=600,
        help='Maximum seconds for AI analysis (default: 600)'
    )

    args = parser.parse_args()

    try:
        passed, explanation = check_visual(
            image_file=args.image_file,
            description=args.description,
            test_script=args.test_script,
            code_path=args.code_path,
            timeout=args.timeout
        )

        sys.exit(0 if passed else 1)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(130)


if __name__ == '__main__':
    main()
