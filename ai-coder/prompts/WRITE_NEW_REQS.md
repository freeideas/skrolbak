# Plan Requirement Documents

Read `./README.md` and `./specs/*.md` to identify concerns. Write stub documents to `./tmp/new-reqs/`.

Do not write requirements. That will be done later. Your job is to create stub documents (title and description only) into which requirements will be written.

Read `./ai-coder/PHILOSOPHY.md` for context on how we approach software and documentation.

---

## Your Task

1. Read all documentation (`./README.md` and `./specs/*.md`)
2. Identify distinct concerns
3. Write one stub file per concern to `./tmp/new-reqs/`

---

## What Is a Concern?

A concern is a **cohesive area of functionality** that can be documented and tested independently.

**Examples:**
- `lifecycle.md` -- Startup, health checks, shutdown
- `logging.md` -- Log output format, levels, destinations
- `ui.md` -- The appearance of the UI and sequence of operation thereof
- `api.md` -- HTTP endpoints, request/response formats
- `configuration.md` -- Config file format, environment variables
- `cli.md` -- Command-line arguments and options

**Guidelines for splitting concerns:**
- Each concern should be independently testable
- Group related behaviors together
- Don't create huge monolithic files (split unrelated items)
- Name files descriptively using lowercase with hyphens
- If source content presents specific named flows or scenarios, each one MUST be its own requirement document

**IMPORTANT - Avoid Duplication:**
- Review all files already present in `./tmp/new-reqs/` (these are templates/seeds from `./ai-coder/prompts/`)
- Do NOT create stubs that duplicate or overlap with existing files
- For example: if `build-output.md` is already seeded there, do NOT create stubs named `build`, `output`, `build-artifacts`, etc.
- Read the existing files to understand what concerns they cover, then generate stubs for OTHER concerns only

---

## What to Include

**Not everything in documentation needs to be a concern.** READMEs include descriptive context to help readers understand. Only create concerns for actual testable behavior.

**DO create concerns for observable, testable behavior of delivered software**

**DO NOT create concerns for:**
- Build scripts or build processes (how to compile, what commands to run)
- How to compile or package (no step-by-step build instructions)
- Development tooling or infrastructure
- **Wrong inputs/edge cases** (unless README explicitly documents error behavior)
- **Negative capabilities** (e.g., "does not support UDP" - absence of feature)
- **Performance/load characteristics** (e.g., "handles 10k requests/sec" - hard to test reliably)
- **Natural consequences** (e.g., OOM crashes, data loss on process kill)
- **OS/runtime behavior** (e.g., process termination on SIGKILL)

**EXCEPTION - Mandated Testing Methodology:**

If `./specs/TESTING.md` (or similar) explicitly mandates HOW tests must be performed (e.g., "use screenshots", "visual verification", "capture before/after images"), create a `testing-methodology.md` concern for these mandates. Per PHILOSOPHY.md: "Requirements specify WHAT, and HOW only when documentation specifies HOW."

This is NOT general "development infrastructure" -- it's explicitly mandated methodology that must become requirements.

---

## Source of Truth

The source of truth is `./README.md` and `./specs/*.md` taken together as one body of documentation. Read all of it.

If these documents reference other files (e.g., `./docs/` for API specs, WSDL files, etc.), you may scan those for context, but the source of truth remains README and specs only.

There is no one-to-one relationship between spec files and requirement documents. A single concern may draw from multiple spec files, and a single spec file may contribute to multiple concerns.

---

## Outline File Format

Each file in `./tmp/new-reqs/` should contain just a title and description:

```markdown
# Server Lifecycle

Documents the complete lifecycle of the server from startup through shutdown.
```

That's it. Title and description only. Description should be short and high-level with very little technical detail.

---

## Process

### Step 1: Read All Documentation

Read thoroughly:
- `./README.md`
- All files in `./specs/*.md`

Scan any referenced files (e.g., `./docs/`) for context as needed.

### Step 2: Identify Concerns

Group related testable behaviors into concerns. Consider:
- What distinct areas of functionality exist?
- What can be tested independently?
- What groupings make logical sense?

### Step 3: Write Outline Files

For each concern, create `./tmp/new-reqs/[concern-name].md` with:
- Title
- Description
