#!/usr/bin/python3
"""
Fix mixed list format in markdown files where some items are plain text
and others are markdown list items.

This preprocessor ensures consistent list formatting so mdBook can parse correctly.
Specifically handles cases like Section 2.060 in Ord 54 where:
- Items (a), (b), (c) are plain text
- Items (1), (2), (3) are markdown list items with `-`

Author: Claude
Date: 2025
"""

import re
import sys
from pathlib import Path

def fix_mixed_lists_in_file(file_path):
    """Fix mixed list formats in a single markdown file."""
    path = Path(file_path)

    if not path.exists():
        print(f"File not found: {file_path}")
        return False

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this line starts with (a), (b), (c), etc. at the beginning
        alpha_match = re.match(r'^(\([a-z]\))\s+(.+)', line, re.IGNORECASE)

        if alpha_match:
            marker = alpha_match.group(1)
            content = alpha_match.group(2)

            # Check if we're in a section that has other items already converted
            # or if the next item in sequence is a list item
            j = i + 1
            has_markdown_lists_nearby = False

            # Look ahead for markdown lists or other alpha items
            while j < len(lines) and j < i + 10:  # Check next 10 lines
                if lines[j].strip().startswith('- ('):
                    has_markdown_lists_nearby = True
                    break
                # Also check if next alpha item will be converted
                if re.match(r'^(\([a-z]\))\s+', lines[j], re.IGNORECASE):
                    # Check if THAT item has markdown sub-items
                    k = j + 1
                    while k < len(lines) and not re.match(r'^(\([a-z]\)|\#{2,3})', lines[k], re.IGNORECASE):
                        if lines[k].strip().startswith('- ('):
                            has_markdown_lists_nearby = True
                            break
                        k += 1
                    if has_markdown_lists_nearby:
                        break
                j += 1

            if has_markdown_lists_nearby:
                # Convert this to markdown list format for consistency
                new_lines.append(f"- {marker} {content}")
                modified = True
                print(f"  Fixed mixed list at line {i+1}: {marker}")
            else:
                # Keep as-is if no markdown lists nearby
                new_lines.append(line)
        else:
            new_lines.append(line)

        i += 1

    if modified:
        with open(path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"✓ Fixed mixed list formats in {path.name}")
        return True
    else:
        return False

def main():
    """Process specified files or all ordinance files."""
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        # Process all ordinance files by default
        files = list(Path('src/ordinances').glob('*.md'))

    fixed_count = 0
    for file_path in files:
        if fix_mixed_lists_in_file(file_path):
            fixed_count += 1

    if fixed_count > 0:
        print(f"\n✅ Fixed mixed lists in {fixed_count} file(s)")
    else:
        print("\n No mixed list issues found")

if __name__ == '__main__':
    main()