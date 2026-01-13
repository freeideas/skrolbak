You are verifying that a test faithfully and accurately tests the requirements.

## Context

**Requirement file:** {{REQ_FILE_PATH}}

**Test file:** {{TEST_FILE_PATH}}

**This test already passes.** Your job: verify it faithfully tests the requirements.

## Your Task

Read {{REQ_FILE_PATH}} and {{TEST_FILE_PATH}}.

For each requirement, check:
1. **If test has assertions for it:** Does the assertion actually test what the requirement describes?
2. **If test marks it "not reasonably testable":** Do you agree it's not reasonably testable?

**Path safety:** Tests must stay portable. If you see absolute paths (e.g., `/home/...`, `C:\...`), replace them with project-relative paths (use `Path(__file__).resolve().parent` or `Path('tmp') / ...`), assuming CWD is the project root.

If all requirements are handled correctly: **Do nothing.**

If any requirement is not faithfully tested or wrongly marked as untestable: **Fix the test.**

**Note:** Tests use plain Python (normal `assert`, `sys.exit()`, exceptions), not pytest. Never import or depend on pytest when updating these files.

## Examples

**Missing assertion:**
```python
# $REQ_BUILD_001
# (no assertion) <- FIX: Add assertion
```

**Vague assertion:**
```python
# $REQ_HTTP_001
assert result is not None  # Too vague <- FIX: assert result.status_code == 200
```

**Wrongly marked untestable:**
```python
# $REQ_PORT_001 - Not reasonably testable: Port configuration
# But port IS testable! <- FIX: Add assertion to test port
```

**Correctly marked untestable:**
```python
# $REQ_INTERNAL_001 - Not reasonably testable: Internal implementation detail with no observable behavior
# OK Agree this can't be tested
```

**Correct assertion:**
```python
# $REQ_BUILD_001
assert Path('./released/MyApp.exe').exists()  # OK Tests the requirement
```

## Understanding "Reasonably Testable"

This test already passed, so it completed within the timeout.

When you see a requirement marked "not reasonably testable," **trust that decision if**:
- The comment explains it would require compiling code during the test
- The comment explains it would require downloading packages during the test
- The comment explains it would require building test fixtures during the test

**DO NOT try to "fix" these by adding slow operations.** If a requirement is marked "not reasonably testable" for performance reasons, that's a valid choice.

**Only question it if:**
- The requirement IS actually testable quickly (example: marked "not testable" but you could just check a file exists)
- The "not testable" comment doesn't make sense

**Your job**: Verify correctness and coverage, not performance. Accept "not reasonably testable" markings for slow operations.

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

## What You Can Modify

- {{TEST_FILE_PATH}} only

## Decision

- **Test faithfully tests requirements** -> Make NO changes
- **Test doesn't faithfully test requirements** -> Fix it
