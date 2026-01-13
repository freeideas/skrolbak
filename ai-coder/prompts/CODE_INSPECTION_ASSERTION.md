You are verifying a code inspection assertion.

---

## Your Task

**Assertion to verify:** {ASSERTION}

**Code location:** {CODE_PATH}

**Requirement ID:** {REQ_ID}

---

## Project-Specific Testing Rules

Check if `./specs/TESTING.md` exists. If it does, read it first and follow any project-specific instructions it contains. Those instructions take precedence over the defaults below.

If `./specs/TESTING.md` does not exist, proceed with the instructions below.

---

## Instructions

1. **Read all code files** in `{CODE_PATH}`

2. **Check if the assertion is true:**
   - Look for evidence that the code conforms to the assertion
   - Search for patterns, keywords, architectural decisions
   - Consider both what should be present AND what should NOT be present

3. **If assertion is TRUE:**
   - Do NOT modify any files
   - Explain what you found that confirms the assertion

4. **If assertion is FALSE:**
   - Modify the code to make the assertion true
   - Make minimal changes necessary to satisfy the assertion
   - **Mark changes with $REQ_ID comment: `// {REQ_ID}`**
   - Explain what was wrong and what you changed

---

## Examples

### Example 1: Threading Model

**Assertion:** "Uses Kestrel's thread pool for request handling"

**If TRUE:**
- Found `ConfigureKestrel` or `WebApplication.CreateBuilder`
- No manual `new Thread()` or `ThreadPool.QueueUserWorkItem`
- Report: "Code uses Kestrel's default threading -- no changes needed"

**If FALSE:**
- Found manual thread creation with `new Thread()`
- Modified code to remove manual threading, rely on Kestrel
- Report: "Removed manual thread creation, now uses Kestrel's thread pool"

### Example 2: Singleton Pattern

**Assertion:** "Single plugin instance serves all requests"

**If TRUE:**
- Found `AddSingleton<IDataConnector>`
- Plugin instance stored as field, not recreated per request
- Report: "Plugin registered as singleton -- no changes needed"

**If FALSE:**
- Found `AddTransient` or `new` in request handler
- Changed to `AddSingleton` and stored instance
- Report: "Changed to singleton registration for shared instance"

### Example 3: Thread Safety

**Assertion:** "No mutable static state"

**If TRUE:**
- All `static` fields are `readonly` or `const`
- No mutable static collections
- Report: "No mutable static state found -- no changes needed"

**If FALSE:**
- Found `private static List<T>` or similar
- Changed to instance field or thread-safe collection
- Report: "Removed mutable static field, now instance field"

---

## What to Report

**Format:**

```
ASSERTION: {ASSERTION}
STATUS: [PASS|FAIL]

FINDINGS:
[What you found in the code]

CHANGES:
[If FAIL: what you modified and why]
[If PASS: "No changes -- assertion already satisfied"]

EVIDENCE:
[Specific code snippets or file:line references supporting your conclusion]
```

---

## Useful Tools

**Track requirement IDs:** To get information about a `$REQ_ID` (definition, source, test coverage, implementation locations):

```bash
{{UV_BINARY}} run --script ./ai-coder/scripts/track-reqIDs.py $REQ_ID
```

You can also pass multiple IDs or use `--req-file ./reqs/file.md` to trace all IDs in a file.

---

## Important Notes

- **Minimal changes:** Only modify what's necessary to satisfy the assertion
- **Preserve functionality:** Don't break existing behavior
- **Document changes:** Clearly explain what you changed and why
- **If uncertain:** Err on the side of NO CHANGE -- only modify if clearly violated
- **No test files:** This checks implementation in {CODE_PATH}, not tests

---

Begin your inspection now.
