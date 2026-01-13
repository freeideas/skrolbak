# Ensure Requirements Coverage

Check that all reasonably testable specifications are covered by requirements.

Read `./ai-coder/PHILOSOPHY.md` for context on how we approach software and documentation.

## Your Task

1. Read `./README.md` and `./specs/*.md` (source of truth)
2. Read all files in `./reqs/*.md` (existing requirements)
3. Identify any reasonably testable specification NOT covered by an existing requirement
4. Add missing requirements to the most appropriate `./reqs/` document
5. If everything is already covered, do nothing

---

## What Is "Covered"?

A specification is covered if there exists a $REQ_ID in `./reqs/` that tests the same behavior.

The requirement doesn't need identical wording -- it just needs to verify the same observable behavior.

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
- **Implied requirements** (internal mechanisms proven correct when another requirement passes -- e.g., "uses HTTP Basic Auth" is implied by "authentication succeeds"; "calls GET /endpoint" is implied by "returns correct data from that endpoint")

**EXCEPTION - Mandated Testing Methodology:**

If `./specs/TESTING.md` (or similar) explicitly mandates HOW tests must be performed (e.g., "use screenshots", "visual verification", "capture before/after images"), these mandates ARE requirements. Per PHILOSOPHY.md: "Requirements specify WHAT, and HOW only when documentation specifies HOW."

This is NOT general "development infrastructure" -- it's explicitly mandated methodology that must become requirements.

---

## Adding Missing Requirements

When you find an uncovered specification:

1. **PREFER EXISTING FILES** - Look for an existing requirement file that covers a related concern
   - If you find one, add the missing requirement there
   - Only create a new file if no existing file could reasonably cover it
   - Examples:
     - Missing artifact details → add to `build-output.md`, don't create `build-artifacts.md`
     - Missing startup behavior → add to `startup.md`, don't create `initialization.md`
     - Missing completely new concern → OK to create new file

2. Add the requirement at the end of the document
3. Use proper format:

```markdown
## $REQ_CONCERN_NNN: Short Title
**Source:** ./specs/FILE.md (Section: "Name")

Clear, testable statement of the requirement.
```

4. Use a unique $REQ_ID that follows the document's naming pattern
5. Cite the correct source file and section

---

## Important

- Do NOT reorganize or rewrite existing requirements
- Do NOT make cosmetic changes
- ONLY add requirements that are genuinely missing
- If everything is covered, make no changes at all
