You are verifying that a test faithfully and accurately tests the requirements.

## Context

**Requirement file:** {{REQ_FILE_PATH}}

**Test file:** {{TEST_FILE_PATH}}

**This test already passes.** Your job: verify it faithfully tests the requirements.

## OVERRIDE: Project Testing Standards

**IMPORTANT: Before following any instructions below, check if `./specs/TESTING.md` exists.**

If `./specs/TESTING.md` exists:
- Read it FIRST before verifying any tests
- Follow ALL instructions in `./specs/TESTING.md`
- `./specs/TESTING.md` takes PRECEDENCE over any conflicting instructions in this prompt
- Only use the instructions below for topics not covered in `./specs/TESTING.md`

If `./specs/TESTING.md` does not exist, proceed with the instructions below.

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
{{UV_BINARY}} run --script ./the-system/scripts/track-reqIDs.py $REQ_ID
```

You can also pass multiple IDs or use `--req-file ./reqs/file.md` to trace all IDs in a file.

**Visual verification:** To have AI examine a screenshot and verify it matches a description:

```bash
{{UV_BINARY}} run --script ./the-system/scripts/visual-test.py <image_path> "<description>"
```

Exit codes: 0=match, 1=no match, 2=error. The script handles all AI interaction internally.

**IMPORTANT: Never import AI SDKs directly.** Do NOT import `anthropic`, `openai`, or similar SDKs in test code. All AI interaction must go through `the-system` infrastructure (`visual-test.py`, `prompt-ai.py`). Tests should never require API keys.

**Web app testing:** When testing web applications, `file://` URLs won't work (CORS, service workers, etc.). Import `start_server` from `./the-system/scripts/websrvr.py`:

- `port = start_server('./released')` — starts HTTP server, returns random port (above 10000)
- `url = get_server_url(port)` — returns `"http://localhost:{port}"`
- `stop_server()` — cleanup (also runs automatically on exit)

**Code inspection assertions:** For structural requirements that can't be tested behaviorally:

```bash
{{UV_BINARY}} run --script ./the-system/scripts/code-inspection-assertion.py "<assertion>" --code-path ./code
```

Exit codes: 0=assertion holds, 1=assertion violated. **Only use when:** (1) behavioral testing isn't practical, (2) the assertion is objectively verifiable — not subjective. Good: "uses async I/O", "no mutable static state". Bad: "efficient code", "clean architecture".

## What You Can Modify

- {{TEST_FILE_PATH}} only

## Decision

- **Test faithfully tests requirements** -> Make NO changes
- **Test doesn't faithfully test requirements** -> Fix it
