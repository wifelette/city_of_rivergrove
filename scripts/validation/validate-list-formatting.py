#!/usr/bin/env python3
"""
Validates that list formatting is properly applied in HTML output.
Checks for:
- Roman numerals are properly wrapped in list-marker-roman spans
- Numeric lists are properly wrapped in list-marker-numeric spans
- Lists aren't collapsed into single paragraphs
- Nested lists maintain proper structure
"""

import os
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from typing import List, Tuple

# ANSI color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
RESET = '\033[0m'

def check_roman_numerals(soup: BeautifulSoup, file_path: str) -> List[str]:
    """Check for improperly formatted roman numerals."""
    errors = []

    # Find all text nodes that contain roman numeral patterns
    roman_pattern = r'\([ivxlcdm]+\)'

    # Check paragraphs that might contain collapsed lists
    for p in soup.find_all('p'):
        text = p.get_text()
        # Look for multiple roman numerals in a single paragraph (indicates collapsed list)
        matches = re.findall(roman_pattern, text, re.IGNORECASE)
        if len(matches) > 1:
            errors.append(f"Multiple roman numerals in single paragraph (likely collapsed list): {text[:100]}...")

        # Check if roman numerals are not in proper list format
        if matches and not p.find('span', class_='list-marker-roman'):
            for match in matches:
                # Check if this is actually in a list item
                parent = p.parent
                if not (parent and parent.name == 'li'):
                    errors.append(f"Roman numeral '{match}' not properly formatted as list marker")

    return errors

def check_numeric_lists(soup: BeautifulSoup, file_path: str) -> List[str]:
    """Check for improperly formatted numeric lists."""
    errors = []

    # Pattern for numeric list markers
    numeric_pattern = r'\((\d+)\)'

    # Check paragraphs for collapsed numeric lists
    for p in soup.find_all('p'):
        text = p.get_text()
        matches = re.findall(numeric_pattern, text)
        if len(matches) > 1:
            errors.append(f"Multiple numeric markers in single paragraph (likely collapsed list): {text[:100]}...")

        # Check if numeric markers are properly formatted
        if matches and not p.find('span', class_='list-marker-numeric'):
            for match in matches:
                parent = p.parent
                if not (parent and parent.name == 'li'):
                    errors.append(f"Numeric marker '({match})' not properly formatted as list marker")

    return errors

def check_list_structure(soup: BeautifulSoup, file_path: str) -> List[str]:
    """Check for proper list structure and nesting."""
    errors = []

    # Check for lists with proper class attributes
    lists = soup.find_all(['ul', 'ol'])
    for lst in lists:
        # Check if numeric/roman lists have proper classes
        if lst.find('span', class_='list-marker-roman') and 'roman-list' not in lst.get('class', []):
            errors.append("List contains roman numerals but missing 'roman-list' class")
        if lst.find('span', class_='list-marker-numeric') and 'numeric-list' not in lst.get('class', []):
            errors.append("List contains numeric markers but missing 'numeric-list' class")

    # Check for orphaned list markers (not in lists)
    orphaned_markers = []
    for span in soup.find_all('span', class_=['list-marker-roman', 'list-marker-numeric']):
        # Check if this marker is actually in a list
        parent = span.parent
        in_list = False
        while parent:
            if parent.name in ['ul', 'ol']:
                in_list = True
                break
            parent = parent.parent

        if not in_list:
            marker_text = span.get_text()
            orphaned_markers.append(f"Orphaned list marker '{marker_text}' not in proper list structure")

    errors.extend(orphaned_markers)

    return errors

def check_specific_known_issues(soup: BeautifulSoup, file_path: str) -> List[str]:
    """Check for specific known problematic sections."""
    errors = []

    # Check Section 4.3-3 in Ord 52 specifically (known problem area)
    if '1987-Ord-52-Flood' in file_path:
        section = soup.find('h4', id='43-3-information-to-be-obtained-and-maintained')
        if section:
            # Get the next sibling which should be the list
            next_elem = section.find_next_sibling()
            if next_elem and next_elem.name == 'p':
                text = next_elem.get_text()
                if '(i)' in text and '(ii)' in text:
                    errors.append("Section 4.3-3 has collapsed roman numeral list - should be proper nested list")

    # Check for definition sections with collapsed lists
    definitions_header = soup.find(string=re.compile('DEFINITIONS'))
    if definitions_header:
        parent = definitions_header.parent
        if parent:
            # Look for the next few elements
            for sibling in parent.find_next_siblings()[:5]:
                if sibling.name == 'p':
                    text = sibling.get_text()
                    # Check for multiple list markers in definitions
                    if text.count('(1)') > 1 or text.count('(i)') > 1:
                        errors.append(f"Definitions section has collapsed list: {text[:100]}...")

    return errors

def validate_file(file_path: str) -> Tuple[List[str], List[str]]:
    """Validate a single HTML file for list formatting issues."""
    errors = []
    warnings = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')

        # Run all checks
        errors.extend(check_roman_numerals(soup, file_path))
        errors.extend(check_numeric_lists(soup, file_path))
        errors.extend(check_list_structure(soup, file_path))
        errors.extend(check_specific_known_issues(soup, file_path))

        # Warnings for potential issues
        # Check if file has any lists at all (might indicate processing didn't run)
        lists = soup.find_all(['ul', 'ol'])
        if not lists and ('ordinances' in file_path or 'resolutions' in file_path):
            # Check if there are patterns that should be lists
            text = soup.get_text()
            if re.search(r'\(\d+\)|\([ivxlcdm]+\)', text, re.IGNORECASE):
                warnings.append("File contains list patterns but no actual list elements - postprocessing may have failed")

    except Exception as e:
        errors.append(f"Error reading file: {str(e)}")

    return errors, warnings

def main():
    """Main validation function."""
    book_dir = Path('book')

    if not book_dir.exists():
        print(f"{RED}✗ book/ directory not found. Run build first.{RESET}")
        sys.exit(1)

    print(f"{BLUE}🔍 Validating list formatting in HTML files...{RESET}\n")

    total_errors = []
    total_warnings = []
    files_checked = 0

    # Check specific files that commonly have lists
    target_files = [
        'ordinances/1987-Ord-52-Flood.html',
        'ordinances/1989-Ord-54-89C-Land-Development.html',
        'ordinances/2001-Ord-70-2001-WQRA.html',
        'resolutions/1984-Res-72-Municipal-Services.html'
    ]

    # Add all ordinance and resolution files
    for pattern in ['ordinances/*.html', 'resolutions/*.html', 'interpretations/*.html']:
        for file_path in book_dir.glob(pattern):
            relative_path = file_path.relative_to(book_dir)
            if str(relative_path) not in target_files:
                target_files.append(str(relative_path))

    for relative_path in target_files:
        file_path = book_dir / relative_path
        if file_path.exists():
            files_checked += 1
            errors, warnings = validate_file(str(file_path))

            if errors:
                total_errors.append((str(relative_path), errors))
            if warnings:
                total_warnings.append((str(relative_path), warnings))

    # Print results
    print(f"📊 Checked {files_checked} file(s)\n")

    if total_errors:
        print(f"{RED}✗ Found list formatting errors:{RESET}\n")
        for file_path, errors in total_errors:
            print(f"  {file_path}:")
            for error in errors:
                print(f"    • {error}")
            print()

    if total_warnings:
        print(f"{YELLOW}⚠️  Warnings:{RESET}\n")
        for file_path, warnings in total_warnings:
            print(f"  {file_path}:")
            for warning in warnings:
                print(f"    • {warning}")
            print()

    if not total_errors and not total_warnings:
        print(f"{GREEN}✓ All list formatting looks correct!{RESET}")
        return 0
    elif total_errors:
        print(f"{RED}✗ List formatting validation failed{RESET}")
        print(f"\nTo fix these issues:")
        print(f"  1. Check that unified-list-processor.py is running during builds")
        print(f"  2. Run: python3 scripts/postprocessing/unified-list-processor.py")
        print(f"  3. For persistent issues, check the source markdown files")
        return 1
    else:
        print(f"{YELLOW}⚠️  List formatting validation passed with warnings{RESET}")
        return 0

if __name__ == '__main__':
    sys.exit(main())