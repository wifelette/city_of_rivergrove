#!/usr/bin/python3
"""
Fix specific list issues in Ordinance 54.
Handles:
1. Nested numeric definitions under alphabetic items (i) "Lot" and (w) "Street"
2. Separation of incorrectly merged lists from different sections
3. Proper placement of item (w) in the Section 1.050 definitions list
"""

from bs4 import BeautifulSoup, NavigableString
from pathlib import Path
import re

def fix_ord54_lists():
    """Fix list issues in Ordinance 54"""
    html_file = Path('book/ordinances/1989-Ord-54-89C-Land-Development.html')

    if not html_file.exists():
        print(f"File not found: {html_file}")
        return False

    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    changes_made = False

    # Find Section 1.050 Definitions heading
    section_1050 = soup.find('h3', id='section-1050-definitions')
    if not section_1050:
        print("Could not find Section 1.050 Definitions")
        return False

    # Find Article 2 heading
    article_2 = soup.find('h2', id='article-2---scope-and-compliance')
    if not article_2:
        print("Could not find Article 2 heading")
        return False

    # Get all elements between Section 1.050 and Article 2
    current = section_1050.next_sibling
    definitions_lists = []
    while current and current != article_2:
        if hasattr(current, 'name') and current.name == 'ul' and 'alpha-list' in current.get('class', []):
            definitions_lists.append(current)
        current = current.next_sibling

    if len(definitions_lists) >= 1:
        main_list = definitions_lists[0]

        # Check if item (w) is missing from the main list
        has_w = False
        items = main_list.find_all('li', recursive=False)
        for item in items:
            text = item.get_text()
            if '(w)' in text[:10] and 'Street' in text:
                has_w = True
                break

        # If there's a second list with item (w), merge it
        if not has_w and len(definitions_lists) >= 2:
            second_list = definitions_lists[1]
            # Find item (w) in the second list
            for item in second_list.find_all('li', recursive=False):
                text = item.get_text()
                if '(w)' in text[:10] and 'Street' in text:
                    print("Moving item (w) to main definitions list")
                    # Find where to insert it (after item v)
                    items = main_list.find_all('li', recursive=False)
                    insert_after = None
                    for idx, existing_item in enumerate(items):
                        existing_text = existing_item.get_text()
                        if '(v)' in existing_text[:10]:
                            insert_after = existing_item
                            break

                    if insert_after:
                        # Insert item (w) after item (v)
                        insert_after.insert_after(item.extract())
                        changes_made = True

            # Remove the now-empty second list if it exists
            if second_list and not second_list.find_all('li', recursive=False):
                second_list.decompose()

        # Now clean up the main list - remove items that belong to other sections
        items_to_remove = []
        items = main_list.find_all('li', recursive=False)

        # The definitions list should end at item (y) "Subdivision"
        found_y = False
        for idx, item in enumerate(items):
            text = item.get_text()
            if found_y:
                # Everything after (y) should be removed
                items_to_remove.append(item)
            elif '(y)' in text[:10] and 'Subdivision' in text:
                found_y = True

        # Remove items that don't belong
        if items_to_remove:
            print(f"Removing {len(items_to_remove)} items that belong to other sections")
            for item in items_to_remove:
                item.extract()
            changes_made = True

        # Now handle the nested items under (i) and (w)
        items = main_list.find_all('li', recursive=False)

        # Fix (i) "Lot" with its numeric sub-definitions
        item_i = None
        lot_items = []

        for idx, item in enumerate(items):
            text = item.get_text()
            if '(i)' in text[:10] and 'Lot' in text and 'means a unit' in text:
                item_i = (idx, item)
            elif '(1)' in text[:10] and 'Corner Lot' in text:
                lot_items.append((1, idx, item))
            elif '(2)' in text[:10] and 'Reversed Corner Lot' in text:
                lot_items.append((2, idx, item))
            elif '(3)' in text[:10] and 'Through Lot' in text:
                lot_items.append((3, idx, item))

        # If we found item (i) and its sub-items, nest them
        if item_i and lot_items:
            # Check if not already nested
            if not item_i[1].find('ul'):
                print(f"Nesting {len(lot_items)} lot type definitions under (i)")

                # Sort by number
                lot_items.sort(key=lambda x: x[0])

                # Create nested ul
                nested_ul = soup.new_tag('ul')
                nested_ul['class'] = ['numeric-list']

                # Move items to nested list
                for _, _, item in lot_items:
                    nested_ul.append(item.extract())

                # Add nested list to item (i)
                item_i[1].append(nested_ul)
                changes_made = True

        # Fix (w) "Street" with its numeric sub-definitions
        item_w = None
        street_items = []

        # Re-get items since we may have modified the structure
        items = main_list.find_all('li', recursive=False)

        for idx, item in enumerate(items):
            text = item.get_text()
            if '(w)' in text[:10] and 'Street' in text and 'public or private way' in text:
                item_w = (idx, item)
            elif '(1)' in text[:10] and 'Alley' in text:
                street_items.append((1, idx, item))
            elif '(2)' in text[:10] and 'Arterial' in text:
                street_items.append((2, idx, item))
            elif '(3)' in text[:10] and 'Collector' in text:
                street_items.append((3, idx, item))
            elif '(4)' in text[:10] and 'Cul-de-sac' in text:
                street_items.append((4, idx, item))

        # If we found item (w) and its sub-items, nest them
        if item_w and street_items:
            # Check if not already nested
            if not item_w[1].find('ul'):
                print(f"Nesting {len(street_items)} street type definitions under (w)")

                # Sort by number
                street_items.sort(key=lambda x: x[0])

                # Create nested ul
                nested_ul = soup.new_tag('ul')
                nested_ul['class'] = ['numeric-list']

                # Move items to nested list
                for _, _, item in street_items:
                    nested_ul.append(item.extract())

                # Add nested list to item (w)
                item_w[1].append(nested_ul)
                changes_made = True

    # Save if changes were made
    if changes_made:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"✓ Saved changes to {html_file}")
        return True
    else:
        print("No changes needed")
        return False

if __name__ == '__main__':
    fix_ord54_lists()