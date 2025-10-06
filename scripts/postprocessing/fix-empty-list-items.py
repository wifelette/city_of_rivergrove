#!/usr/bin/python3
"""
Fix empty list items that mdBook created when it failed to parse list content.
This specifically fixes Section 2.060 and similar cases where mdBook creates
empty <li></li> elements.

Author: Claude
Date: 2025
"""

from bs4 import BeautifulSoup, NavigableString, Tag
from pathlib import Path
import re
import sys

def find_and_fix_empty_list_items(soup):
    """Find empty list items and try to recover their content from the source."""
    changes_made = False

    # Find all empty list items
    for ul in soup.find_all('ul'):
        items = ul.find_all('li', recursive=False)

        # Check for empty items
        empty_items = []
        for item in items:
            # An item is empty if it has no text content (ignoring nested lists)
            direct_text = ''.join(str(c) for c in item.contents if isinstance(c, NavigableString)).strip()
            if not direct_text and not item.find('span', class_=['list-marker-alpha', 'list-marker-numeric']):
                empty_items.append(item)

        if empty_items:
            print(f"Found {len(empty_items)} empty list items")

            # Look for Section 2.060 specifically
            # Find the preceding heading
            prev_heading = None
            for elem in ul.previous_siblings:
                if isinstance(elem, Tag) and elem.name in ['h1', 'h2', 'h3', 'h4']:
                    prev_heading = elem
                    break

            if prev_heading and '2.060' in prev_heading.get_text():
                print("  Fixing Section 2.060 empty list items")

                # Check if items have already been fixed (avoid duplication)
                already_fixed = False
                for item in items:
                    if item.find('span', class_='list-marker-alpha'):
                        text = item.get_text()
                        if 'nonconforming' in text and 'Planning Commission' in text:
                            already_fixed = True
                            break

                if not already_fixed and len(empty_items) >= 2:
                    # Fix item (a)
                    item_a = empty_items[0]
                    item_a.clear()
                    item_a.append(BeautifulSoup('<span class="list-marker-alpha">(a)</span>', 'html.parser').span)
                    item_a.append(' A development that is nonconforming only because of a failure to comply with the Comprehensive Plan or this ordinance may be altered or extended only if the Planning Commission and the City Council find the alteration or extension will decrease the extent of noncompliance and the development is not a land division that is nonconforming because of a public facility deficiency. A land division that is nonconforming because of a public facility deficiency may not be further altered or extended before the public facility deficiency is cured.')

                    # Fix item (b)
                    item_b = empty_items[1]
                    item_b.clear()
                    item_b.append(BeautifulSoup('<span class="list-marker-alpha">(b)</span>', 'html.parser').span)
                    item_b.append(' With the approval of the City Council, under the procedure set out in Section 6.060 and Section 6.070, a nonconforming development or use may be changed provided, however, that the maximum special relief shall be as follows:')

                    # Now move the numeric sub-list to be nested under (b)
                    # Find the item with the numeric list
                    for i, item in enumerate(items):
                        nested_ul = item.find('ul', class_='numeric-list')
                        if nested_ul and i != 1:  # If it's not already in item_b
                            # Move this nested list under item (b)
                            nested_ul.extract()
                            item_b.append(nested_ul)
                            # Remove the now-empty item
                            if not item.get_text().strip():
                                item.extract()
                            break

                    changes_made = True

    return changes_made

def fix_document(html_file):
    """Fix empty list items in an HTML file."""
    path = Path(html_file)

    if not path.exists():
        print(f"File not found: {html_file}")
        return False

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    if find_and_fix_empty_list_items(soup):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"✓ Fixed empty list items in {path.name}")
        return True
    else:
        return False

def main():
    """Process specified files."""
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        # Default to known problematic file
        files = ['book/ordinances/1989-Ord-54-89C-Land-Development.html']

    for file_path in files:
        fix_document(file_path)

if __name__ == '__main__':
    main()