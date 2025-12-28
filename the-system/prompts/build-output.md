# Build Requirements

Requires the contents of the `./released/` directory to contain the specified files and only the specified files. Requiries (presumably by code inspection of ./code/build.py) that the correct build strategy is used (e.g. ".NET AOT STAND-ALONE" or "Rust" or "Flutter"), and that the ./released/ directory is emptied and re-written with each build.
