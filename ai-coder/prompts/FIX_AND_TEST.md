Fix code and/or test until the test passes.

## Context

- **Requirement:** {{REQ_FILE_PATH}}
- **Test:** {{TEST_FILE_PATH}}

## Task

1. Read the requirement file
2. If test doesn't exist, create it
3. Run the test
4. If it fails, fix code or test
5. Repeat until test passes

**Path safety:** Tests must be portable. Do **not** hardcode absolute paths (e.g., `/home/...`, `C:\...`). Use repo-relative paths instead (e.g., `Path('tmp') / 'treename'`, `Path(__file__).resolve().parent`) and assume CWD is the project root when running the test command below.

**Test runner:** Write and fix tests as plain Python scripts that rely only on built-in `assert` and standard library. **Never use pytest or add any pytest dependency.**

## How to Run Tests

```bash
{{UV_BINARY}} run --script ./ai-coder/scripts/test.py {{TEST_FILE_PATH}}
```

Exit codes:
- **0** = Test passed
- **1** = Test failed
- **97** = Build failed (fix ./code/build.py or source files first)
- **99** = Test claims external dependency failure (see below)
- **124** = Timeout

## Handling Exit Code 99 (External Dependency Failure)

When a test exits with code 99, it believes an external dependency is unavailable. However, **this is often a bug in the code or test**, not an actual external problem. Common causes:

- The code under test returns an error that the test misinterprets as "dependency down"
- Test setup code fails and blames an external system
- A bug in error handling or connection logic

**Your job is to fix it anyway.** Investigate the actual error, fix the code or test to make it as correct as possible. Do not give up just because the test claims external dependency failure.

If it truly is an external dependency issue, find a way to make the system behave correctly despite the limitation, while staying faithful to the software's purpose. For example: better error handling, graceful degradation, adjusting what the test verifies, or using a different mechanism.

## Useful Tools

**Track requirement IDs:** To get information about a `$REQ_ID` (definition, source, test coverage, implementation locations):

```bash
{{UV_BINARY}} run --script ./ai-coder/scripts/track-reqIDs.py $REQ_ID
```

You can also pass multiple IDs or use `--req-file ./reqs/file.md` to trace all IDs in a file.

**Visual verification:** To have AI examine screenshot(s) and verify an assertion about them:

```bash
{{UV_BINARY}} run --script ./ai-coder/scripts/visual-test.py <image_path>... "<assertion>" --test-script <test_file>
```

Examples:
- Single image: `visual-test.py ./tmp/screenshot.png "Form is centered with blue button" --test-script ./tests/passing/test.py`
- Two images: `visual-test.py ./tmp/before.png ./tmp/after.png "The two screenshots show different background positions" --test-script ./tests/passing/test.py`

Exit codes: 0=assertion true (code unchanged), 1=assertion false (code was modified), 2=error.

**IMPORTANT: For visual verification requirements (screenshot comparisons, "verify visually", before/after image comparisons, etc.), you MUST use `visual-test.py` wherever it can perform the required test. The test takes screenshots and calls `visual-test.py` with an assertion.**

**IMPORTANT: Never import AI SDKs directly.** Do NOT import `anthropic`, `openai`, or similar SDKs in test code. All AI interaction must go through `ai-coder` infrastructure (`visual-test.py`, `prompt-ai.py`). Tests should never require API keys.

**Web app testing:** When testing web applications, `file://` URLs won't work (CORS, service workers, etc.). Import `start_server` from `./ai-coder/scripts/websrvr.py`:

- `port = start_server('./released')` — starts HTTP server, returns random port (above 10000)
- `url = get_server_url(port)` — returns `"http://localhost:{port}"`
- `stop_server()` — cleanup (also runs automatically on exit)

**Code inspection assertions:** For structural requirements that can't be tested behaviorally:

```bash
{{UV_BINARY}} run --script ./ai-coder/scripts/code-inspection-assertion.py "<assertion>" --code-path ./code
```

Exit codes: 0=assertion holds, 1=assertion violated. **Only use when:** (1) behavioral testing isn't practical, (2) the assertion is objectively verifiable — not subjective. Good: "uses async I/O", "no mutable static state". Bad: "efficient code", "clean architecture".

## Installing Test Tools

If you need additional testing tools, install them into `./tools/`. Prefer portable installations when available, but use non-portable (system) installation if necessary.

**Browser UI testing:** If the project has a browser-based UI, use Playwright for testing. Install it as a uv dependency in your test script:

```python
# /// script
# requires-python = ">=3.8"
# dependencies = ["playwright"]
# ///
```

Then install browser binaries (one-time setup):

```bash
{{UV_BINARY}} run playwright install
```

## What You Can Modify

- `./code/*` -- implementation files
- `{{TEST_FILE_PATH}}` -- the test file for this requirement

## Important: Validate Test Against Requirement

Before spending multiple attempts fixing code, **validate that the test accurately reflects the requirement file**:

1. **Read the requirement file first** and understand what the system is supposed to do
2. **Compare the test expectations against the requirement** - do they match?
3. **If the test expects something different from what the requirement says:**
   - Fix the test to match the requirement
   - Do NOT repeatedly try to change the code to match an incorrect test

This saves time and prevents getting stuck in a loop. A test is part of the implementation; if it contradicts the requirement, the test is wrong, not the code.

## Marking Code with $REQ_IDs

**Always mark implementation code with the $REQ_ID it implements.** This enables traceability from requirements to code.

**In code files:**
```csharp
// $REQ_STARTUP_001
public void StartServer() { ... }

private void ValidateConfig()  // $REQ_CONFIG_002
{
    // $REQ_CONFIG_003: Check for missing required fields
    ...
}
```

**In test files:**
```python
assert server.is_running()  # $REQ_STARTUP_001
assert server.port == 43143  # $REQ_STARTUP_002
```

Use `track-reqIDs.py` to verify your $REQ_ID markers are being tracked.

**Compiler location:** Always use the portable compiler in `./tools/compiler/`. Do **not** rely on PATH. See `./ai-coder/prompts/DOWNLOAD_COMPILER.md` for supported compilers and their paths.

## What You MUST NOT Modify

**These paths are protected. Any changes will be discarded:**

{{PROTECTED_PATHS}}

**IMPORTANT:** If you encounter errors with tools in `./ai-coder/`, do NOT try to fix them. Report the error and stop. The system handles platform-specific binaries automatically.

## Test Requirements

Every `$REQ_ID` from the requirement file must appear in the test:
- Testable: `assert something  # $REQ_ID`
- Not testable: `# $REQ_ID - Not reasonably testable: [reason]`

## Process Cleanup

If your test launches executables, ensure cleanup:

```python
import atexit
import subprocess

_procs = []

def cleanup():
    for p in _procs:
        try:
            p.terminate()
            p.wait(timeout=2)
        except:
            pass

atexit.register(cleanup)

# When launching:
proc = subprocess.Popen(['./released/app.exe'])
_procs.append(proc)
```

## Success

Test exits with code 0.
