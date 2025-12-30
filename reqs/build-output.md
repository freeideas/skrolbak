# Build Requirements

Requires the contents of the `./released/` directory to contain the specified files and only the specified files. Requiries (presumably by code inspection of ./code/build.py) that the correct build strategy is used (e.g. ".NET AOT STAND-ALONE" or "Rust" or "Flutter"), and that the ./released/ directory is emptied and re-written with each build.

## $REQ_BUILD_001: Build Script Produces Released Directory
**Source:** ./README.md (Section: "Build")

Running `./code/build.py` must produce output in `./released/skrolbak/`.

## $REQ_BUILD_002: Released Directory Contains Component Script
**Source:** ./README.md (Section: "Usage")

After build, `./released/skrolbak/` must contain `animated-background.js` as referenced in the usage example.

## $REQ_BUILD_003: Released Directory Contains Demo Image
**Source:** ./specs/DEMO.md (Section: "Demo Image")

After build, `./released/skrolbak/` must contain `bg.jpg` for demo/testing purposes.
