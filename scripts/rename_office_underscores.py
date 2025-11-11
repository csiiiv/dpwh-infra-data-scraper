#!/usr/bin/env python3
"""
Rename DPWH HTML files: convert underscores in office names to dashes.
Example: table_Central_Office_2016_20251111_155202.html -> table_Central-Office_2016_20251111_155202.html
"""
import re
from pathlib import Path

def rename_html_files(directory='html'):
    pattern = re.compile(r'^(table_)(.+?)(_20\d{2}_\d{8}_\d{6}\.html)$')
    html_dir = Path(directory)
    for file in html_dir.glob('table_*.html'):
        match = pattern.match(file.name)
        if match:
            prefix, office, suffix = match.groups()
            new_office = office.replace('_', '-')
            new_name = f"{prefix}{new_office}{suffix}"
            new_path = file.with_name(new_name)
            print(f"Renaming: {file.name} -> {new_name}")
            file.rename(new_path)

if __name__ == '__main__':
    rename_html_files()
