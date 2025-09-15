#!/usr/bin/env python3
"""
Check List Nesting Validation Script
Ensures proper indentation for nested list items in markdown files.
Specifically checks for roman numerals that should be nested under numeric items.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# ANSI color codes
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def check_file_nesting(filepath: Path) -> List[Tuple[int, str, str]]:
    """
    Check a markdown file for improper list nesting.
    Returns a list of (line_number, issue, line_content) tuples.
    """
    issues = []

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_numbered_list = False
    expecting_nested = False
    in_blockquote = False
    prev_line = ""

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Check if we're in a blockquote (starts with >)
        if stripped.startswith('>'):
            in_blockquote = True
        elif stripped and not stripped.startswith('>'):
            in_blockquote = False

        # Skip checks if we're in a quoted section or code block
        if in_blockquote or stripped.startswith('**"') or stripped.startswith('"'):
            prev_line = line
            continue

        # Check if we're starting a numbered list item
        if re.match(r'^\d+\.\s', stripped):
            in_numbered_list = True
            # Check if the line ends with a colon (suggesting nested items follow)
            if stripped.rstrip().endswith(':'):
                expecting_nested = True
            else:
                expecting_nested = False

        # Check for roman numerals that should be nested
        elif re.match(r'^\([ivxlcdm]+\)', stripped, re.IGNORECASE):
            # This is a roman numeral list marker
            # Only flag if previous line ended with colon (indicating a list context)
            if in_numbered_list and expecting_nested and not line.startswith('   '):
                issues.append((
                    i,
                    "Roman numeral list item not properly indented (needs 3 spaces)",
                    line.rstrip()
                ))
            elif prev_line.strip().endswith(':') and not line.startswith('   '):
                # Check if previous line suggests this should be nested
                if not any(skip in prev_line for skip in ['**"', '""', 'follows:']):
                    issues.append((
                        i,
                        "Roman numeral list item not properly indented (needs 3 spaces)",
                        line.rstrip()
                    ))

        # Check for lettered items that should be nested
        elif re.match(r'^\([a-z]\)', stripped, re.IGNORECASE):
            # This is a lettered list marker
            # Only flag if previous line ended with colon (indicating a list context)
            if in_numbered_list and expecting_nested and not line.startswith('   '):
                issues.append((
                    i,
                    "Lettered list item not properly indented (needs 3 spaces)",
                    line.rstrip()
                ))
            elif prev_line.strip().endswith(':') and not line.startswith('   '):
                # Check if previous line suggests this should be nested
                if not any(skip in prev_line for skip in ['**"', '""', 'follows:']):
                    issues.append((
                        i,
                        "Lettered list item not properly indented (needs 3 spaces)",
                        line.rstrip()
                    ))

        # Reset state if we hit a non-list line
        elif stripped and not stripped.startswith('(') and not re.match(r'^\d+\.\s', stripped):
            # Check if it's not a continuation of the previous line
            if not expecting_nested:
                in_numbered_list = False

        prev_line = line

    return issues

def check_all_files(directory: Path, pattern: str = "*.md") -> dict:
    """
    Check all markdown files in a directory for nesting issues.
    """
    results = {}

    for filepath in directory.rglob(pattern):
        # Skip certain directories
        if any(skip in str(filepath) for skip in ['.git', 'node_modules', 'book/']):
            continue

        issues = check_file_nesting(filepath)
        if issues:
            results[filepath] = issues

    return results

def main():
    """Main function to run the nesting check."""
    import argparse

    parser = argparse.ArgumentParser(description='Check markdown files for proper list nesting')
    parser.add_argument('path', nargs='?', default='.',
                       help='Path to file or directory to check (default: current directory)')
    parser.add_argument('--fix', action='store_true',
                       help='Attempt to fix nesting issues automatically')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Show all files checked, not just those with issues')

    args = parser.parse_args()

    path = Path(args.path)

    if path.is_file():
        # Check single file
        issues = check_file_nesting(path)
        if issues:
            print(f"{RED}✗{NC} {path.name} has nesting issues:")
            for line_num, issue, content in issues:
                print(f"  Line {line_num}: {issue}")
                print(f"    {YELLOW}{content}{NC}")

            if args.fix:
                print(f"\n{BLUE}Fixing nesting issues...{NC}")
                fix_file_nesting(path)
                print(f"{GREEN}✓{NC} Fixed {len(issues)} issue(s)")

            return 1
        else:
            if args.verbose:
                print(f"{GREEN}✓{NC} {path.name} - No nesting issues found")
            return 0

    elif path.is_dir():
        # Check directory
        results = check_all_files(path)

        if results:
            total_issues = sum(len(issues) for issues in results.values())
            print(f"{RED}✗{NC} Found {total_issues} nesting issue(s) in {len(results)} file(s):\n")

            for filepath, issues in results.items():
                rel_path = filepath.relative_to(path) if path != Path('.') else filepath
                print(f"{YELLOW}{rel_path}{NC}:")
                for line_num, issue, content in issues[:3]:  # Show first 3 issues per file
                    print(f"  Line {line_num}: {issue}")
                if len(issues) > 3:
                    print(f"  ... and {len(issues) - 3} more issue(s)")
                print()

            if args.fix:
                print(f"{BLUE}Fixing nesting issues in all files...{NC}")
                for filepath in results.keys():
                    fix_file_nesting(filepath)
                print(f"{GREEN}✓{NC} Fixed issues in {len(results)} file(s)")

            return 1
        else:
            print(f"{GREEN}✓{NC} No nesting issues found in {path}")
            return 0

    else:
        print(f"{RED}Error: {path} is not a file or directory{NC}")
        return 1

def fix_file_nesting(filepath: Path):
    """
    Fix nesting issues in a file by adding proper indentation.
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixed_lines = []
    in_numbered_list = False

    for line in lines:
        stripped = line.strip()

        # Check if we're starting a numbered list item
        if re.match(r'^\d+\.\s', stripped):
            in_numbered_list = True
            fixed_lines.append(line)

        # Check for roman numerals that need indentation
        elif re.match(r'^\([ivxlcdm]+\)', stripped, re.IGNORECASE):
            if in_numbered_list and not line.startswith('   '):
                # Add 3 spaces of indentation
                fixed_lines.append('   ' + stripped + '\n')
            else:
                fixed_lines.append(line)

        # Check for lettered items that need indentation
        elif re.match(r'^\([a-z]\)', stripped, re.IGNORECASE):
            if in_numbered_list and not line.startswith('   '):
                # Add 3 spaces of indentation
                fixed_lines.append('   ' + stripped + '\n')
            else:
                fixed_lines.append(line)

        else:
            # Reset state if we hit a non-list line (unless it's empty)
            if stripped and not stripped.startswith('(') and not re.match(r'^\d+\.\s', stripped):
                in_numbered_list = False
            fixed_lines.append(line)

    # Write the fixed content back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)

if __name__ == '__main__':
    sys.exit(main())