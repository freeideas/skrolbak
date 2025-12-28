## Environment

- **GitHub**: Already logged in and authenticated
- **Project Repositories**: All project repos are located under `/home/ace/prjx`
- **Git Branch Naming**: Always use "main" instead of "master" for default branch names, as some people find "master" offensive

## Available Tools

System-wide tools available in any directory:
- `rg` (ripgrep) - Fast text search: `rg "pattern" --type py`
- `jq` - JSON processor: `fd "*.json" | xargs jq .`
- `fd` (fdfind) - Fast file finder
- `bat` (batcat) - Enhanced cat with syntax highlighting
- `tree` - Directory structure: `tree -L 2`
- `xmlstarlet` - XML processing
- `dos2unix` - Fix line endings
- `file` - Determine file types
- `git-extras` - Git utilities (git-flow, git-changelog, git-ignore, etc.)
- `httpie` - Modern HTTP client: `http GET example.com`
- `ncdu` - NCurses disk usage analyzer
- `tldr` - Simplified man pages with practical examples
- `fzf` - Fuzzy finder for terminal
- `ag` (silversearcher) - Fast code searching tool
- `docker` & `docker-compose` - Container tools
- `go` - Go programming language
- `rustc` & `cargo` - Rust programming language and package manager
- `gh` - GitHub CLI
- `uv` - Fast Python package manager and script runner

### Python Development

**IMPORTANT: NEVER run Python scripts with `python script.py`. ALWAYS run them with uv:**
- [OK] CORRECT: `uv run --script ./scripts/my_script.py`
- [X] WRONG: `python scripts/my_script.py` or `python3 scripts/my_script.py`

**All Python scripts MUST have this shebang as the first line:**
```python
#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = [
    # List PyPI packages here
]
# ///
```

**Key points:**
- Scripts can use ANY PyPI package without pre-installation - just list it in dependencies
- The script metadata block (`# /// script`) declares dependencies inline
- Use `uv run` to execute Python scripts with automatic dependency management

**When creating new Python scripts:**
1. ALWAYS start with the `#!/usr/bin/env uvrun` shebang
2. Add the script metadata block with dependencies
3. Make the script executable: `chmod +x script.py`
4. Run it directly: `./script.py` NOT `python script.py`

### Node.js Tools (global npm packages)
- `prettier` - Code formatter for JS/TS/CSS/etc
- `eslint` - JavaScript linter
- `typescript` - TypeScript compiler
- `tsx` - TypeScript execute
- `nodemon` - Auto-restart node apps
- `pm2` - Process manager
- `yarn`, `pnpm` - Alternative package managers

**Note**: If you need any standard development tools that aren't listed above or that you discover are missing during your work, feel free to install them using the appropriate package manager (apt, pip, npm, etc.). This ensures you have all necessary tools to complete tasks efficiently.

**ALWAYS use ./tmp directory for temporary scripts:**

```bash
# Create tmp directory if it doesn't exist
mkdir -p ./tmp
# Run tests with absolute or relative paths (NO cd!)
uv run --script ./tmp/test_script.py
# Or specify output paths:
uv run --script script.py --output ./tmp/results.json

# Bad - Never create temporary files in:
# - Git repository roots (except in tmp/, which should be added to .gitignore)
# - Project source directories
# - Any version-controlled directory (except tmp/, which should be added to .gitignore)
```

Python: Always use `./tmp` directory (create it with `os.makedirs('./tmp', exist_ok=True)` if needed).

## Important Instructions

## Git LFS

**Never use Git LFS.** Files that exceed GitHub's hard limit should be excluded instead of using LFS.

## Unicode and Subprocess Encoding

**Use Unicode characters in output when it improves readability, but avoid adding new Unicode characters to source files unless they already use them.**

**CRITICAL: All Python subprocess calls MUST explicitly specify `encoding='utf-8'` on Windows, but even on MacOS and Linux so they will be cross-platform ready:**

```python
# ❌ WRONG - Windows defaults to cp1252, mangles Unicode
subprocess.run(cmd, text=True)
subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE)

# ✅ CORRECT - Explicit UTF-8 encoding
subprocess.run(cmd, text=True, encoding='utf-8')
subprocess.Popen(cmd, text=True, encoding='utf-8', stdout=subprocess.PIPE)
```

**Why:** On Windows, `text=True` without explicit `encoding='utf-8'` defaults to cp1252 encoding. This causes UTF-8 characters (like ✓ and ✗) to be misread and appear as garbage characters (âœ") in captured output and reports.

**Always add `encoding='utf-8'` when using:**
- `subprocess.run(..., text=True)`
- `subprocess.Popen(..., text=True)`
- `subprocess.check_output(..., text=True)`
- Any subprocess call with `text=True` or `universal_newlines=True`

## Cross Platform
- We try to write everything in the most Windows and Linux -compatible way
- We often name shell scripts with .bat and binary executables with .exe even on Linux devices, because Linux doesn't care, but Windows does.

## Windows Process Signal Handling

**CRITICAL: Never use `os.kill(pid, signal.CTRL_C_EVENT)` or `signal.CTRL_C_EVENT` in Python tests on Windows.**

On Windows, `CTRL_C_EVENT` is broadcast to the entire console process group, including the test runner itself. This will kill your test process along with the target process.

**Instead, use HTTP shutdown endpoints when available:**
```python
# ❌ WRONG - Kills the test runner too!
os.kill(proc.pid, signal.CTRL_C_EVENT)

# ✅ CORRECT - Use HTTP shutdown endpoint
import urllib.request
req = urllib.request.Request(f"http://127.0.0.1:{port}/shutdown", method='POST')
urllib.request.urlopen(req, timeout=5)
```

**Why this happens:** Windows doesn't have Unix-style per-process signals. `CTRL_C_EVENT` is sent to all processes attached to the same console, which includes Python test scripts running the subprocess.
