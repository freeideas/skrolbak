# Build System Execution Hierarchy

Create a detailed execution hierarchy that documents the complete flow of the **@ai-coder/ build system itself** (not any project using it). Reference `@ai-coder/00_OVERVIEW.md` to understand the overall context and workflow.

## Instructions

1. **Start with the root script**: Read `@ai-coder/scripts/software-construction.py` and create a hierarchy starting from the `main()` function.

2. **Include all execution details at each level**:
   - Function/method names that are called (e.g., `main()`, `generate_code()`, `run_ai_prompt()`, `run_test_fix_loop()`)
   - All conditional branches (if/else, try/except) with their execution paths
   - The order of execution as it flows through the code

3. **Recursively break down called Python scripts**:
   - Whenever a `.py` script is called (via `run_script()`, `import_script()`, or direct import), create a subtree that:
     - Reads and analyzes that script file
     - Breaks down its main function and all significant functions it calls
     - Shows their execution order
     - Recursively continues for any scripts those scripts call
   - Automatically discover all referenced scripts and follow the call chain
   - All scripts are within `@ai-coder/scripts/` directory

4. **Document all AI prompt executions**:
   - Whenever a prompt is executed (via `run_ai_prompt()` with a `.md` file path), create a subtree that:
     - Reads the actual `.md` prompt file at that path within `@ai-coder/prompts/`
     - Extracts and lists the key steps/sections the prompt performs or requests
     - Shows what outputs or artifacts it creates
   - Automatically discover all prompt files referenced in the code

5. **Format the hierarchy**:
   - Use a clear tree structure (indentation or markdown bullets)
   - Show conditional paths clearly (e.g., "IF --skip-reqs flag: [branch] ELSE: [branch]")
   - Include line numbers from source files where relevant (e.g., `scripts/software-construction.py:275`)
   - Show what each node does and what it produces (files, artifacts, outputs)
   - Focus scope: only on @ai-coder/ internals

6. **Output format**: Write the complete hierarchy to a file under `./reports/` directory with a time-stamped prefix:
   - Format: `./reports/YYYY-MM-DD-HH-MM-SS-mmm_HOW-THIS-WORKS.md`
   - Example: `./reports/2025-12-07-22-34-11-816_HOW-THIS-WORKS.md`
   - Include a timestamp in the report itself (generated at execution time)
