# Download Compiler and Build Tools

Ensure the required compiler and build tools are available for building the project.

**First:** Read `./README.md` to determine which compiler/language the project uses. If it isn't obvious, then try reading `./specs/*.md` documents.

## Process

1. **Determine compiler and build tools** -- From README/specs, identify the required compiler/language, version, and any build tools (e.g., NSIS for installers)
2. **Always provision portable compiler** -- Download a portable/standalone build into `./tools/compiler/` even if one is already on PATH
3. **Verify the downloaded compiler** -- Run its version command from the downloaded location

## Requirements

- Do **not** rely on PATH; use the downloaded portable compiler
- Only if the WRONG compiler is in `./tools/compiler/`, delete that directory and replace it
- Download portable/standalone builds (not installers)
- Extract to `./tools/compiler/` directory
- Use the compiler from `./tools/compiler/` in build scripts
- The `./tools/` directory is gitignored

## Compiler Location

The compiler is always at `./tools/compiler/` (relative to the project root).

## Notes

- **C/C++ projects:** Use Zig as the compiler (`zig cc` / `zig c++`). Zig includes a drop-in C/C++ compiler that works cross-platform without additional setup.

## Examples

These are some of the compilers you may need to download portably:

| Tool     | Test Command       | Portable Location                      |
| -------- | ------------------ | -------------------------------------- |
| Rust     | `rustc --version`  | `./tools/compiler/cargo/bin/rustc.exe` |
| Zig      | `zig version`      | `./tools/compiler/zig/zig.exe`         |
| C#       | `dotnet --version` | `./tools/compiler/dotnet/dotnet.exe`   |
| Go       | `go version`       | `./tools/compiler/go/bin/go.exe`       |
| Java     | `javac -version`   | `./tools/compiler/jdk/bin/javac.exe`   |
| NSIS     | `makensis /VERSION`| `./tools/nsis/makensis.exe`            |
