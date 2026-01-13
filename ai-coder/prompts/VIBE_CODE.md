You are generating a complete implementation from human-written documentation.

## Context

**Source of truth:** README.md and ./specs/*.md (human-written documentation)

**Your task:** Generate all code files in ./code/ including ./code/build.py

**Philosophy:** See ./ai-coder/PHILOSOPHY.md for core principles (minimal viable project, ruthless simplification, requirement-focused modularity)

## Inputs

- **README.md** -- Project overview, build information, expected artifacts in ./released/
- **./specs/*.md** -- Detailed specifications organized by workflow/concern (primary source)
- **./docs/** (if exists) -- Supporting documentation (WSDL, API docs, protocol specs)

## What You Must Generate

### 1. Complete Implementation (./code/*)

Generate ALL source code files needed to implement the system described in README.md and ./specs/.

**Implementation requirements:**
- Follow @PHILOSOPHY.md: implement only what the docs require, choose the simplest approach, and omit "nice to have" extras (including logging/error handling) unless explicitly specified.
- **Mark implementation code with $REQ_IDs** -- add comments like `// $REQ_STARTUP_001` to trace requirements to code.
- Do **not** write, simulate, or run any tests here. Produce implementation code that would compile/build if required; test generation and execution are handled elsewhere.

**Marking code with $REQ_IDs:**
```csharp
// $REQ_STARTUP_001
public void StartServer() { ... }

private void ValidateConfig()  // $REQ_CONFIG_002
{
    // $REQ_CONFIG_003: Check for missing required fields
    ...
}
```

### 2. Build Script (./code/build.py)

**CRITICAL:** You MUST generate ./code/build.py with these characteristics:

```python
#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     # List all build dependencies here
# ]
# ///

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Build implementation here
```

**Build script MUST:**
1. Compile/package the code
2. Copy all final artifacts to ./released/
3. Exit with code 0 on success, non-zero on failure
4. Print clear progress messages
5. Build must actually work; focus on making build.py correct and runnable. It is the only place you should perform any build/compile/check; do not add test runs anywhere.

**Compiler location:** Always use the portable compiler in `./tools/compiler/`. Do **not** rely on PATH. See `./ai-coder/prompts/DOWNLOAD_COMPILER.md` for supported compilers and their paths.

## Useful Tools

**Track requirement IDs:** To get information about a `$REQ_ID` (definition, source, test coverage, implementation locations):

```bash
{{UV_BINARY}} run --script ./ai-coder/scripts/track-reqIDs.py $REQ_ID
```

You can also pass multiple IDs or use `--req-file ./reqs/file.md` to trace all IDs in a file.

**Artifacts in ./released/:**
- Must match what README.md and ./specs/*.md describes
- Should be ready to use (executable, deployable, etc.)
- Include all dependencies needed to run (unless, of course, the project requires stand-alone)

## What You Cannot Modify

Anything outside of the ./code/ directory

## Output Format

Write or edit ALL files in ./code/ -- delete obsolete files if specs changed.

## Success Criteria

- All ./code/* files generated
- ./code/build.py exists with proper shebang
- Running ./code/build.py produces artifacts in ./released/
- Artifacts match what README.md describes
- Code appears to implement what readme/specs describe -- no more, no less
- No tests created or executed at this stage (all testing happens later)

## Now: Generate the Code

Read README.md and ./specs/* then generate complete implementation in ./code/, including ./code/build.py
