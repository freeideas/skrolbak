# Write Requirements for a Concern

Edit the stub document to add requirements.

## Context

- **Stub document:** {{STUB_FILE_PATH}}

Read `./ai-coder/PHILOSOPHY.md` for context on how we approach software and documentation.

## Your Task

1. Read the stub document (title and description of the concern)
2. Read `./README.md` and `./specs/*.md` to find all testable behaviors for this concern
3. Edit the stub document to add the requirements (keep the title and description)

## Source of Truth

The source of truth is `./README.md` and `./specs/*.md` taken together. If these reference other files (e.g., `./docs/`), you may scan those for context, but requirements must trace back to README or specs.

---

## Requirement Format

```markdown
# [Pre-existing title from stub]

[Pre-existing description from stub]

## $REQ_CONCERN_001: Short Title
**Source:** ./specs/FILE.md (Section: "Name")

Clear, testable statement of the requirement.

## $REQ_CONCERN_002: Short Title
**Source:** ./README.md (Section: "Name")

Clear, testable statement of the requirement.
```

---

## THE EIGHT RULES FOR REQUIREMENTS

1. **Complete Coverage** -- Every reasonably testable behavior for this concern must have a $REQ_ID
2. **No Invention** -- Only requirements from `./README.md` or `./specs/*.md` are allowed (./docs/ is NEVER a valid source)
3. **No Overspecification** -- Requirements must not be more specific than README.md or ./specs/
4. **Tell Stories** -- Wherever possible, requirements are in flow order (e.g. you must add an item before you can edit it)
5. **Source Attribution** -- Every $REQ_ID cites ONLY: `**Source:** ./README.md (Section: "Name")` or `**Source:** ./specs/FILE.md (Section: "Name")`
6. **Unique IDs** -- Each $REQ_ID appears exactly once. Format: `$REQ_` followed by letters/digits/underscores/hyphens (e.g., $REQ_STARTUP_001)
7. **Reasonably Testable** -- Requirements must have observable behavior that can be verified
8. **No Implied Requirements** -- Do not write requirements for internal mechanisms when another requirement tests the observable outcome. If "returns correct data" passes, "calls correct API endpoint" is implied. If "authentication succeeds" passes, "uses HTTP Basic Auth" is implied. Keep the outcome, delete the mechanism.

---

## What to Include

**Not everything in documentation needs to be a requirement.** READMEs include descriptive context to help readers understand. Extract the actual requirement, not the description.

**DO write requirements for observable, testable behavior of delivered software**

**DO NOT write requirements for:**
- Build scripts or build processes (how to compile, what commands to run)
- How to compile or package (no step-by-step build instructions)
- Development tooling or infrastructure
- **Wrong inputs/edge cases** (unless README explicitly documents error behavior)
- **Negative capabilities** (e.g., "does not support UDP" - absence of feature)
- **Performance/load characteristics** (e.g., "handles 10k requests/sec" - hard to test reliably)
- **Natural consequences** (e.g., OOM crashes, data loss on process kill)
- **OS/runtime behavior** (e.g., process termination on SIGKILL)

**EXCEPTION - Mandated Testing Methodology:**

If `./specs/TESTING.md` (or similar) explicitly mandates HOW tests must be performed (e.g., "use screenshots", "visual verification", "capture before/after images"), these mandates ARE requirements. Per PHILOSOPHY.md: "Requirements specify WHAT, and HOW only when documentation specifies HOW."

Example: If specs say "Take screenshot A, wait, take screenshot B, verify they differ" -- create a requirement like:
```markdown
## $REQ_TEST_METHOD_001: Visual Verification via Screenshots
**Source:** ./specs/TESTING.md (Section: "Test Process")

Tests must capture screenshots before and after actions and verify visual changes occurred.
```

This is NOT general "development infrastructure" -- it's explicitly mandated methodology.

---

## How to Write Requirements

### Step 1: Read All Documentation

Read thoroughly:
- `./README.md`
- All files in `./specs/*.md`

You may skim `./docs/` to understand technical context (e.g., WSDL schemas, API references), but **./docs/ can NEVER be cited as a source**. If a behavior appears only in `./docs/` and not in README.md or ./specs/, it is NOT a requirement.

Identify within the context specified by {{STUB_FILE_PATH}}, reasonably testable behaviors **of delivered software:** anchored in README.md or ./specs/ only.
- Actions users take with executable (with correct inputs)
- System responses (to valid requests)
- Observable outputs
- Error conditions **only explicitly documented in README.md or ./specs/**
- Success criteria

**Skip sections about:**
- "Building from source" (HOW to compile)
- "Development prerequisites" (what tools are needed to build)
- Build/compilation instructions (steps to run the build)
- Limitations stated as absences ("doesn't support X")
- Performance/load claims ("handles 10k req/sec")
- What happens with wrong inputs (unless README.md or ./specs/ documents it)
- Behaviors described only in `./docs/` (./docs/ is NEVER a valid source)
