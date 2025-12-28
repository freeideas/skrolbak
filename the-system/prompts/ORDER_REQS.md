Order requirement files from foundational to specific using numeric prefixes.

---

## Your Task

Analyze all requirement files in `./reqs/` and order them with numeric prefixes based on dependency.

**Read context:**
- `./README.md` and `./specs/*.md` to understand the system architecture
- All requirement files in `./reqs/` to understand what each covers

**Ordering tiers:**

- **00_:** Build/artifacts (must exist before anything else can run)
- **01_:** Startup/lifecycle (must work before features can be used)
- **02_:** Core functionality (basic use cases that other features depend on)
- **03_:** Advanced features (build on core functionality)
- **04_+:** Edge cases and integrations (depend on everything else)

**Rename requirements as needed:**

Assign appropriate numeric prefixes to requirement files. Use two-digit prefixes.

**Multiple files can share the same tier number** (e.g., both `01_startup.md` and `01_plugin-loading.md` are lifecycle requirements).

**Examples:**

- **REQUIRED:** `build-output.md` → `00_build-output.md` (must use this exact name - downstream build handling depends on it)
- `startup-to-shutdown.md` → `01_startup-to-shutdown.md`
- `plugin-loading.md` → `01_plugin-loading.md`  (same tier as startup)
- `http-endpoints.md` → `02_http-endpoints.md`
- `soap-operations.md` → `03_soap-operations.md`

**Key principles:**
- Build requirements come first (00_)
- Lifecycle/startup requirements come second (01_) - **multiple files may have 01_ prefix**
- Core functionality comes before advanced features
- Dependencies must be satisfied before dependents
- **Files in the same tier can share the same number**

**Important:** Only rename files -- do NOT modify file contents.

---

## Output

After renaming all requirement files, report:
- Brief analysis of requirement dependencies
- List all renames performed (old name -> new name)
- Final ordered list of requirement files
- Rationale for ordering choices

End with summary:
```
[count] requirement files ordered
```
