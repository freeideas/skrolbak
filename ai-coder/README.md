# ai-coder: Overview

Build working software from clear documentation with one command.

---

## How To Use

1. Write your docs: `README.md` and files in `specs/` (optionally `docs/` and `extart/`).
2. Run: `sh ai-coder/software-construction.sh` or `ai-coder\software-construction.bat`
3. Find fully-tested and completed software in `./released/`.

### Command-Line Options

- `--skip-reqs` -- Skip requirement generation, use existing `./reqs/` documents
- `--skip-to-testing` -- Skip requirements and code generation, only run test verification loop

---

## Source Of Truth

- You write: `README.md`, `specs/`, `docs/` - the design (WHAT to build).
- AI generates (disposable):
  - `reqs/` - testable requirement flows from your docs
  - `code/` - implementation from requirements + docs
  - `tests/` - test suite from requirements
  - `released/` - build artifacts shaped by tests

Change the docs and rerun to regenerate everything.

---

## Workflow Summary

- Generate requirements -> generate code -> generate tests -> fix until tests pass.
- Runs autonomously; prompts only when docs need fixes or external deps fail.
- Stages: requirements generation, then code generation, then test verification loop.

---

## When You Intervene

- During requirements: if the system proposes doc fixes, review/accept.
- At any other time: if code generation stops, check `./reports/` for details and refine specs as needed.
- When you find a bug: refine specs as needed and re-run software-construction.

---

## Incremental Workflow (Re-running After Changes)

**The system is optimized for iterative refinement.**

When you modify specs and re-run `software-construction.exe`:

1. **Requirements regeneration** - AI edits existing requirement files in `reqs/` where possible
2. **Code regeneration** - AI edits existing code files in `code/` where possible
3. **In-place re-verification** - Tests in `passing/` are re-run to confirm they still pass
4. **Automatic demotion** - Tests that now fail are moved from `passing/` to `failing/`
5. **Focused fixing** - Only genuinely broken tests require AI attention

### Why This Works

**Verify-in-place pattern:**
- Tests stay in their current directory (`passing/`, `failing/`)
- Each iteration re-runs `passing/` tests to catch regressions
- Tests only move to `failing/` if they actually fail
- Integration check runs all tests together after individual tests pass

**Orphan test deletion:**
- If a requirement file is renamed, its test becomes orphaned (no matching requirement)
- Orphaned tests are deleted and regenerated
- This is correct - we cannot reliably match renamed tests to renamed requirements

**Result:** Minor design changes require minimal re-work. Only tests affected by actual behavior changes need fixing.

---

## Project-Invariant System

The `ai-coder/` directory is identical across projects and should not be edited per-project. Copy it into any repo as `./ai-coder/` and use it as-is.

### Git Management (`.disabled` prefix)

The `ai-coder/` directory has its own git repo for independent versioning, but git files are disabled by default to avoid conflicts with the parent project (`.disabled.git/`, `.disabled.gitignore`).

**Why disabled:** The parent project has its own `.git/`. Nested git repos cause confusion for tools and AI agents.

**To commit/push changes to ai-coder:**

Use `./ai-coder/scripts/ai-coder_upload.py [commit message]` - it handles enable/disable automatically.

Or manually:
1. Rename to enable: `mv .disabled.git .git && mv .disabled.gitignore .gitignore`
2. Commit and push as normal
3. Rename to disable: `mv .git .disabled.git && mv .gitignore .disabled.gitignore`

Keep git disabled during normal operation.

---

## More Docs

- PHILOSOPHY.md - core principles
