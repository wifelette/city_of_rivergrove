#!/usr/bin/env python3
"""
Regression tests for list formatting in Ordinance 54.
Ensures that complex nested lists are properly structured after processing.

Run after build to verify list formatting is correct.
"""

from bs4 import BeautifulSoup
from pathlib import Path
import sys
import re

def test_section_1050_definitions(soup):
    """Test Section 1.050 definitions - item (i) Lot should have nested numeric list."""
    errors = []

    # Find item (i) "Lot"
    item_i = None
    for li in soup.find_all('li'):
        marker = li.find('span', class_='list-marker-alpha')
        if marker and marker.get_text() == '(i)':
            if '"Lot"' in li.get_text():
                item_i = li
                break

    if not item_i:
        errors.append("Section 1.050: Could not find item (i) 'Lot'")
        return errors

    # Check for nested numeric list
    nested_list = item_i.find('ul', class_='numeric-list')
    if not nested_list:
        errors.append("Section 1.050: Item (i) missing nested numeric-list")
        return errors

    # Check for three sub-items
    sub_items = nested_list.find_all('li')
    if len(sub_items) != 3:
        errors.append(f"Section 1.050: Expected 3 sub-items in (i), found {len(sub_items)}")

    # Check sub-item markers
    for idx, li in enumerate(sub_items, 1):
        marker = li.find('span', class_='list-marker-numeric')
        if not marker:
            errors.append(f"Section 1.050: Sub-item {idx} missing numeric marker")
        elif marker.get_text() != f"({idx})":
            errors.append(f"Section 1.050: Sub-item marker is '{marker.get_text()}', expected '({idx})'")

    # Also check item (w) "Street"
    item_w = None
    for li in soup.find_all('li'):
        marker = li.find('span', class_='list-marker-alpha')
        if marker and marker.get_text() == '(w)':
            if '"Street"' in li.get_text():
                item_w = li
                break

    if item_w:
        nested_list = item_w.find('ul', class_='numeric-list')
        if not nested_list:
            errors.append("Section 1.050: Item (w) missing nested numeric-list")
        else:
            sub_items = nested_list.find_all('li')
            if len(sub_items) != 4:
                errors.append(f"Section 1.050: Expected 4 sub-items in (w), found {len(sub_items)}")

    return errors

def test_section_5080_setbacks(soup):
    """Test Section 5.080 setback lists - items (a) and (c) should have nested setback lists."""
    errors = []

    # Find Section 5.080
    section_header = soup.find('h3', id='section-5080-minimum-setback-requirements')
    if not section_header:
        errors.append("Section 5.080: Could not find section header")
        return errors

    # Find the alpha list after this section
    alpha_list = None
    for sibling in section_header.find_next_siblings():
        if sibling.name == 'ul' and 'alpha-list' in sibling.get('class', []):
            alpha_list = sibling
            break

    if not alpha_list:
        errors.append("Section 5.080: Could not find alpha list")
        return errors

    # Check item (a)
    item_a = None
    for li in alpha_list.find_all('li', recursive=False):
        marker = li.find('span', class_='list-marker-alpha')
        if marker and marker.get_text() == '(a)':
            item_a = li
            break

    if not item_a:
        errors.append("Section 5.080: Could not find item (a)")
    else:
        setback_list = item_a.find('ul', class_='setback-list')
        if not setback_list:
            errors.append("Section 5.080: Item (a) missing nested setback-list")
        else:
            items = setback_list.find_all('li')
            if len(items) != 4:
                errors.append(f"Section 5.080: Expected 4 setback items in (a), found {len(items)}")

            # Check that items contain setback measurements
            expected_setbacks = ['Front Setback', 'Side Setback', 'Side Setback', 'Rear Setback']
            for idx, (li, expected) in enumerate(zip(items, expected_setbacks)):
                if expected not in li.get_text():
                    errors.append(f"Section 5.080: Setback item {idx+1} in (a) missing '{expected}'")

    # Check item (c)
    item_c = None
    for li in alpha_list.find_all('li', recursive=False):
        marker = li.find('span', class_='list-marker-alpha')
        if marker and marker.get_text() == '(c)':
            item_c = li
            break

    if not item_c:
        errors.append("Section 5.080: Could not find item (c)")
    else:
        setback_list = item_c.find('ul', class_='setback-list')
        if not setback_list:
            errors.append("Section 5.080: Item (c) missing nested setback-list")
        else:
            items = setback_list.find_all('li')
            if len(items) != 4:
                errors.append(f"Section 5.080: Expected 4 setback items in (c), found {len(items)}")

    return errors

def test_section_5100_definitions(soup):
    """Test Section 5.100 - item (a) DEFINITIONS should have nested numeric list."""
    errors = []

    # Find Section 5.100
    section_header = soup.find('h3', id='section-5100-tree-cutting')
    if not section_header:
        errors.append("Section 5.100: Could not find section header")
        return errors

    # Find item (a) DEFINITIONS
    item_a = None
    for sibling in section_header.find_next_siblings():
        if sibling.name == 'ul' and 'alpha-list' in sibling.get('class', []):
            for li in sibling.find_all('li'):
                marker = li.find('span', class_='list-marker-alpha')
                if marker and marker.get_text() == '(a)' and 'DEFINITIONS' in li.get_text():
                    item_a = li
                    break
            break

    if not item_a:
        errors.append("Section 5.100: Could not find item (a) DEFINITIONS")
        return errors

    # Check for nested numeric list
    nested_list = item_a.find('ul', class_='numeric-list')
    if not nested_list:
        errors.append("Section 5.100: Item (a) missing nested numeric-list")
        return errors

    # Check for two sub-items
    sub_items = nested_list.find_all('li')
    if len(sub_items) != 2:
        errors.append(f"Section 5.100: Expected 2 sub-items in (a), found {len(sub_items)}")

    # Check content
    if sub_items:
        if '"Tree"' not in sub_items[0].get_text():
            errors.append("Section 5.100: First definition should be 'Tree'")
        if '"Cutting"' not in sub_items[1].get_text():
            errors.append("Section 5.100: Second definition should be 'Cutting'")

    return errors

def test_section_2060(soup):
    """Test Section 2.060 - ensure it's not broken."""
    errors = []

    # Find Section 2.060
    section_header = soup.find('h3', id=re.compile('section-2060'))
    if not section_header:
        # Section 2.060 might not exist, which is fine
        return errors

    # Just check that alpha lists exist and have proper structure
    for sibling in section_header.find_next_siblings():
        if sibling.name == 'ul' and 'alpha-list' in sibling.get('class', []):
            items = sibling.find_all('li', recursive=False)
            for li in items:
                marker = li.find('span', class_='list-marker-alpha')
                if not marker:
                    errors.append("Section 2.060: List item missing alpha marker")
            break

    return errors

def main():
    """Run all tests on the built HTML file."""
    file_path = Path('book/ordinances/1989-Ord-54-89C-Land-Development.html')

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        print("   Run 'mdbook build' first")
        return 1

    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    all_errors = []

    # Run all tests
    print("🔍 Testing list formatting in Ordinance 54...")

    errors = test_section_1050_definitions(soup)
    if errors:
        all_errors.extend(errors)
    else:
        print("  ✅ Section 1.050 definitions: PASS")

    errors = test_section_5080_setbacks(soup)
    if errors:
        all_errors.extend(errors)
    else:
        print("  ✅ Section 5.080 setbacks: PASS")

    errors = test_section_5100_definitions(soup)
    if errors:
        all_errors.extend(errors)
    else:
        print("  ✅ Section 5.100 definitions: PASS")

    errors = test_section_2060(soup)
    if errors:
        all_errors.extend(errors)
    else:
        print("  ✅ Section 2.060: PASS")

    # Report results
    if all_errors:
        print("\n❌ FAILED - Found issues:")
        for error in all_errors:
            print(f"  • {error}")
        return 1
    else:
        print("\n✅ All list formatting tests passed!")
        return 0

if __name__ == '__main__':
    sys.exit(main())