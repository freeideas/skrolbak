# Run via: ./bin/uv.exe run --script this_file.py
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///

import sys
# Fix Windows console encoding for Unicode characters
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import os
import sqlite3
import re
from pathlib import Path

# Change to project root (two levels up from this script)
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
os.chdir(project_root)

DB_PATH = './tmp/reqs.sqlite'


def ensure_database_exists():
    """Create the database and schema if it doesn't exist."""
    os.makedirs('./tmp', exist_ok=True)

    if os.path.exists(DB_PATH):
        return  # Already exists

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE req_definitions (
            req_id TEXT PRIMARY KEY,
            req_text TEXT,
            source_attribution TEXT,
            flow_file TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE req_locations (
            req_id TEXT,
            filespec TEXT,
            line_num INTEGER,
            category TEXT
        )
    ''')

    cursor.execute('CREATE INDEX idx_req_locations_id ON req_locations(req_id)')

    conn.commit()
    conn.close()


def scan_reqs_files():
    """Scan ./reqs/*.md files for requirement definitions and locations.

    Returns: (definitions_dict, locations_list)
    """
    definitions = {}  # req_id -> (req_text, source_attribution, flow_file)
    locations = []    # [(req_id, filespec, line_num, category), ...]

    reqs_dir = Path('./reqs')
    if not reqs_dir.exists():
        return definitions, locations

    for req_file in sorted(reqs_dir.glob('*.md')):
        try:
            with open(req_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (IOError, UnicodeDecodeError):
            continue

        for line_num, line in enumerate(lines, start=1):
            req_ids = re.findall(r'\$REQ_[A-Z0-9_]+', line)

            for req_id in req_ids:
                # Check if this is a definition header (## $REQ_ID: Title)
                is_definition_header = line.strip().startswith('##') and ':' in line

                if is_definition_header and req_id not in definitions:
                    # Extract requirement text (title after the colon)
                    text_after_id = line.split(req_id, 1)[1] if req_id in line else ""
                    req_text = text_after_id.strip()

                    # Look for source attribution on the next line
                    source_attribution = None
                    if line_num < len(lines):
                        next_line = lines[line_num].strip()
                        if next_line.startswith('**Source:**'):
                            source_attribution = next_line.replace('**Source:**', '').strip()

                    definitions[req_id] = (req_text, source_attribution, str(req_file))

                # Store location for all occurrences
                locations.append((req_id, str(req_file), line_num, 'reqs'))

    return definitions, locations


def scan_test_files():
    """Scan ./tests/**/*.py files for requirement references.

    Returns: locations_list
    """
    locations = []
    tests_dir = Path('./tests')

    if not tests_dir.exists():
        return locations

    for test_file in tests_dir.rglob('*.py'):
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (IOError, UnicodeDecodeError):
            continue

        for line_num, line in enumerate(lines, start=1):
            req_ids = re.findall(r'\$REQ_[A-Z0-9_]+', line)
            for req_id in req_ids:
                locations.append((req_id, str(test_file), line_num, 'tests'))

    return locations


def scan_code_files():
    """Scan ./code/**/* files for requirement references.

    Returns: locations_list
    """
    locations = []
    code_dir = Path('./code')

    if not code_dir.exists():
        return locations

    binary_extensions = {'.exe', '.dll', '.so', '.dylib', '.bin', '.obj', '.o', '.a', '.lib', '.pyc', '.pyo'}

    for code_file in code_dir.rglob('*'):
        if code_file.is_dir():
            continue
        if code_file.suffix.lower() in binary_extensions:
            continue

        try:
            with open(code_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (IOError, UnicodeDecodeError):
            continue

        for line_num, line in enumerate(lines, start=1):
            req_ids = re.findall(r'\$REQ_[A-Z0-9_]+', line)
            for req_id in req_ids:
                locations.append((req_id, str(code_file), line_num, 'code'))

    return locations


def update_database(definitions, locations):
    """Atomically update the database with new data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Start transaction (implicit with execute, explicit commit at end)
        cursor.execute("BEGIN IMMEDIATE")

        # Clear old data
        cursor.execute("DELETE FROM req_definitions")
        cursor.execute("DELETE FROM req_locations")

        # Insert new definitions
        for req_id, (req_text, source_attribution, flow_file) in definitions.items():
            cursor.execute(
                "INSERT INTO req_definitions (req_id, req_text, source_attribution, flow_file) VALUES (?, ?, ?, ?)",
                (req_id, req_text, source_attribution, flow_file)
            )

        # Insert new locations
        cursor.executemany(
            "INSERT INTO req_locations (req_id, filespec, line_num, category) VALUES (?, ?, ?, ?)",
            locations
        )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def print_summary():
    """Print a summary of the database contents."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM req_definitions")
    num_definitions = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT req_id) FROM req_locations")
    num_referenced = cursor.fetchone()[0]

    cursor.execute("SELECT category, COUNT(*) FROM req_locations GROUP BY category")
    category_counts = cursor.fetchall()

    conn.close()

    print(f"OK Requirements index updated")
    print(f"  Database: {DB_PATH}")
    print(f"  Definitions: {num_definitions}")
    print(f"  Referenced: {num_referenced}")

    if category_counts:
        print(f"  Locations:")
        for category, count in category_counts:
            print(f"    {category}: {count}")


def main():
    print("Updating requirements index...")

    # Ensure database exists
    ensure_database_exists()

    # Scan all directories (in memory)
    definitions, reqs_locations = scan_reqs_files()
    test_locations = scan_test_files()
    code_locations = scan_code_files()

    # Combine all locations
    all_locations = reqs_locations + test_locations + code_locations

    # Atomic update
    update_database(definitions, all_locations)

    # Print summary
    print_summary()


if __name__ == '__main__':
    main()
