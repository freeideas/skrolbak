# Fix Requirements Document

Review and fix a single requirement document for quality issues.

## Context

- **Requirement document:** {{REQ_FILE_PATH}}

Read `./ai-coder/PHILOSOPHY.md` for context on how we approach software and documentation.

## Your Task

1. Read `./README.md` and `./specs/*.md` (source of truth)
2. Read the requirement document
3. Fix any issues found (see checks below)
4. If no issues, leave the file unchanged

---

## THE EIGHT RULES FOR REQUIREMENTS

1. **Complete Coverage** -- Every reasonably testable behavior for this concern must have a $REQ_ID
2. **No Invention** -- Only requirements from `./README.md` or `./specs/*.md` are allowed
3. **No Overspecification** -- Requirements must not be more specific than the source
4. **Tell Stories** -- Requirements in flow order where possible
5. **Source Attribution** -- Every $REQ_ID cites: `**Source:** ./README.md (Section: "Name")` or `**Source:** ./specs/FILE.md (Section: "Name")`
6. **Unique IDs** -- Each $REQ_ID appears exactly once. Format: `$REQ_` + uppercase letters/digits/underscores
7. **Reasonably Testable** -- Requirements must have observable behavior that can be verified
8. **No Implied Requirements** -- Do not write requirements for internal mechanisms when another requirement tests the observable outcome. If "returns correct data" passes, "calls correct API endpoint" is implied. Keep the outcome, delete the mechanism.

---

## Check 1: Source Attribution

Every requirement needs proper source attribution:

```markdown
## $REQ_EXAMPLE_001: Title
**Source:** ./specs/FILE.md (Section: "Name")

Description.
```

**Fix:** Add or correct `**Source:**` lines.

---

## Check 2: Accuracy

Requirements must accurately reflect the source documentation.

**Common inaccuracies to fix:**
- Inverting behavior (README says X, requirement says opposite)
- Misinterpreting examples as requirements (e.g., "crashes with OOM" was illustrating non-blocking, not requiring OOM)
- Adding error handling not in source (focus on happy paths unless error behavior is explicitly documented)
- Contradictions between requirements

**Fix:** Correct requirements to match source, or delete invented requirements.

---

## Check 3: Completeness

All reasonably testable behaviors for this concern should be covered.

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

**Fix:** Add missing requirements with proper format and source attribution.

---

## Check 4: Testability

Requirements must be testable.

**Testable types:**
- Behavioral: "Returns HTTP 404 for missing resources"
- Architectural: "Network I/O must never block on disk writes"

**Untestable (fix or delete):**
- Performance claims: "Handles 10k requests/sec"
- Vague statements: "Should be user-friendly", "Must be reliable"
- Exclusions: "Does not support UDP", "Does not use MVC pattern"

**Difficult to test:***
- Requires more than one minute to test: "Can run continuously for days"

**Fix:** Rewrite to be testable, or delete if not reasonably testable.

---

## Check 5: Overspecification

Requirements must not add details beyond the source.

**Examples:**
- Source: "returns simple HTML" → Requirement: "Returns HTML" (not "HTML must be simple")
- Source: "Exits with an error message if port is not specified" → Requirement: "Prints an error and exits if a port is not specified" (not "Prints 'UNSPECIFIED PORT' and exits with status code 88 if port not specified")

**Fix:** Remove invented details, keeping only what's in the source.

---

## Check 6: Implied Requirements

For each requirement A in this document, ask: "Is there another requirement B such that if B fails, A will always fail too?"

If yes, A is implied by B. Delete A.

**The Dependency Test:**
- If requirement B fails, must requirement A also fail?
- If yes, A is redundant - B already covers it

**Examples of implied requirements to DELETE:**
- "Uses HTTP Basic Auth" is implied by "Authentication succeeds" → if auth fails, the mechanism check also fails
- "Calls GET /sites endpoint" is implied by "Returns list of sites correctly" → if sites aren't returned, the endpoint check also fails
- "Constructs URL as {base}/api/..." is implied by "API calls succeed" → if API calls work, the URL was correct

**Keep the behavioral outcome, delete the internal mechanism.**

**Fix:** Delete requirements that are implied by other requirements in this document.

---

## Important

**Avoid trivial changes:**
- Do NOT reword requirements that are already correct
- Do NOT make cosmetic changes (formatting, spacing)
- Do NOT "improve clarity" of clear enough requirements
- ONLY modify when there's an actual error

**When in doubt, leave unchanged.**
