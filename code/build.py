#!/usr/bin/env uvrun
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
import os
import shutil
from pathlib import Path

# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def main():
    """
    Build Output Location
    Copies source files to ./released/skrolbak/
    """

    # Get the project root (parent of code directory)
    code_dir = Path(__file__).parent
    project_root = code_dir.parent

    # Define source and destination paths
    output_dir = project_root / 'released' / 'skrolbak'

    print('Skrolbak Build Script')
    print('=' * 50)

    # Create output directory
    print(f'Creating output directory: {output_dir}')
    output_dir.mkdir(parents=True, exist_ok=True)

    # JavaScript Component Output
    # Copy animated-background.js
    src_js = code_dir / 'animated-background.js'
    dst_js = output_dir / 'animated-background.js'

    if not src_js.exists():
        print(f'ERROR: Source file not found: {src_js}')
        return 1

    print(f'Copying {src_js.name} -> {dst_js}')
    shutil.copy2(src_js, dst_js)

    # Copy demo.html
    src_html = code_dir / 'demo.html'
    dst_html = output_dir / 'demo.html'

    if not src_html.exists():
        print(f'ERROR: Source file not found: {src_html}')
        return 1

    print(f'Copying {src_html.name} -> {dst_html}')
    shutil.copy2(src_html, dst_html)

    # Copy background image from extart
    src_bg = project_root / 'extart' / 'bg.jpg'
    dst_bg = output_dir / 'bg.jpg'

    if not src_bg.exists():
        print(f'ERROR: Background image not found: {src_bg}')
        return 1

    print(f'Copying {src_bg.name} -> {dst_bg}')
    shutil.copy2(src_bg, dst_bg)

    print('=' * 50)
    print('Build completed successfully!')
    print(f'Output: {output_dir}')
    print('\nFiles created:')
    print(f'  - animated-background.js')
    print(f'  - demo.html')
    print(f'  - bg.jpg')

    return 0

if __name__ == '__main__':
    sys.exit(main())
