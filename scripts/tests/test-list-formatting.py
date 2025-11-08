#!/usr/bin/env python3
"""
Regression tests for list formatting in City of Rivergrove documents.

This test suite checks for known list formatting issues to prevent regressions:
- Alpha items (a), (b), (c) appearing as paragraphs instead of list items
- Numeric items concatenated in single list elements
- Lists appearing as code blocks
- Proper nesting of sub-items
- Correct CSS classes for different list types

Run manually: python3 scripts/tests/test-list-formatting.py
Run specific file: python3 scripts/tests/test-list-formatting.py book/ordinances/1989-Ord-54-89C-Land-Development.html
"""

import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup
import json

class ListFormattingTester:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.failures = []

    def test_file(self, file_path):
        """Test a single HTML file for list formatting issues."""
        print(f"\n📋 Testing: {file_path}")

        if not Path(file_path).exists():
            print(f"  ❌ File not found: {file_path}")
            return False

        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Run all tests
        all_passed = True
        all_passed &= self.test_no_orphaned_alpha_paragraphs(soup, file_path)
        all_passed &= self.test_no_concatenated_numeric_items(soup, file_path)
        all_passed &= self.test_no_list_code_blocks(soup, file_path)
        all_passed &= self.test_no_orphaned_paragraphs_after_lists(soup, file_path)
        all_passed &= self.test_proper_list_nesting(soup, file_path)
        all_passed &= self.test_css_classes(soup, file_path)

        # Additional comprehensive tests to catch visual regressions
        all_passed &= self.test_inline_numeric_references(soup, file_path)
        all_passed &= self.test_paragraph_references(soup, file_path)
        all_passed &= self.test_section_2060_nested_list(soup, file_path)
        all_passed &= self.test_section_2080_single_item(soup, file_path)
        all_passed &= self.test_section_4120_complete_list(soup, file_path)
        all_passed &= self.test_no_empty_list_items(soup, file_path)
        all_passed &= self.test_proper_marker_spacing(soup, file_path)
        all_passed &= self.test_no_duplicate_list_items(soup, file_path)
        all_passed &= self.test_no_broken_nested_structure(soup, file_path)
        all_passed &= self.test_consistent_marker_styles(soup, file_path)
        all_passed &= self.test_proper_definition_nesting(soup, file_path)

        # Special tests for known problem areas
        if '1989-Ord-54' in file_path:
            all_passed &= self.test_section_1050_formatting(soup, file_path)
            all_passed &= self.test_section_2060_formatting(soup, file_path)
            all_passed &= self.test_section_5080_formatting(soup, file_path)
            all_passed &= self.test_section_5110_formatting(soup, file_path)
            all_passed &= self.test_section_5120_formatting(soup, file_path)

        if '1999-Ord-65' in file_path or 'Sewer-Services' in file_path:
            all_passed &= self.test_ord_65_section_2_formatting(soup, file_path)

        return all_passed

    def test_no_orphaned_alpha_paragraphs(self, soup, file_path):
        """Check that alpha-marked items (a), (b), etc. are not paragraphs."""
        self.tests_run += 1

        # Find paragraphs that start with alpha markers
        orphaned = []
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if re.match(r'^\([a-z]\)\s+', text):
                orphaned.append(text[:50] + '...' if len(text) > 50 else text)

        if orphaned:
            self.failures.append({
                'file': file_path,
                'test': 'no_orphaned_alpha_paragraphs',
                'issue': f'Found {len(orphaned)} alpha items as paragraphs instead of list items',
                'examples': orphaned[:3]
            })
            print(f"  ❌ Found {len(orphaned)} orphaned alpha paragraphs")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ No orphaned alpha paragraphs")
            return True

    def test_no_concatenated_numeric_items(self, soup, file_path):
        """Check that numeric sub-items are not concatenated in single list elements."""
        self.tests_run += 1

        concatenated = []
        for li in soup.find_all('li'):
            text = li.get_text()
            # Look for patterns like "1. ... 2. ..." or "(1) ... (2) ..."
            if re.findall(r'\b2[\.\)]\s+(?:"|[A-Z])', text):
                # Check if it's actually multiple items in one
                if re.findall(r'\b[2-9][\.\)]\s+(?:"|[A-Z])', text):
                    concatenated.append(text[:100] + '...' if len(text) > 100 else text)

        if concatenated:
            self.failures.append({
                'file': file_path,
                'test': 'no_concatenated_numeric_items',
                'issue': f'Found {len(concatenated)} list items with concatenated numeric sub-items',
                'examples': concatenated[:3]
            })
            print(f"  ❌ Found {len(concatenated)} concatenated numeric items")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ No concatenated numeric items")
            return True

    def test_no_list_code_blocks(self, soup, file_path):
        """Check that lists are not appearing as code blocks."""
        self.tests_run += 1

        code_block_lists = []
        for pre in soup.find_all('pre'):
            code = pre.find('code')
            if code:
                text = code.get_text()
                # Check if this looks like list items
                if re.match(r'^\s*(\()?([1-9a-z]|[ivx]+)[\)\.]\s', text, re.IGNORECASE):
                    code_block_lists.append(text[:100] + '...' if len(text) > 100 else text)

        if code_block_lists:
            self.failures.append({
                'file': file_path,
                'test': 'no_list_code_blocks',
                'issue': f'Found {len(code_block_lists)} lists appearing as code blocks',
                'examples': code_block_lists[:3]
            })
            print(f"  ❌ Found {len(code_block_lists)} lists as code blocks")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ No lists appearing as code blocks")
            return True

    def test_no_orphaned_paragraphs_after_lists(self, soup, file_path):
        """Check that paragraphs after list items are properly nested."""
        self.tests_run += 1

        orphaned = []
        for ul in soup.find_all('ul', class_='alpha-list'):
            # Check if there's a paragraph right after this list
            next_elem = ul.find_next_sibling()
            if next_elem and next_elem.name == 'p':
                # This paragraph should likely be inside the last list item
                last_li = ul.find_all('li', recursive=False)[-1] if ul.find_all('li', recursive=False) else None
                if last_li:
                    marker = last_li.find('span', class_='list-marker-alpha')
                    if marker:
                        orphaned.append(f"Orphaned paragraph after {marker.get_text()} - should be nested inside the list item")

        if orphaned:
            self.failures.append({
                'file': file_path,
                'test': 'no_orphaned_paragraphs_after_lists',
                'issue': f'Found {len(orphaned)} orphaned paragraphs that should be nested',
                'examples': orphaned[:3]
            })
            print(f"  ❌ Found {len(orphaned)} orphaned paragraphs after lists")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ No orphaned paragraphs after lists")
            return True

    def test_proper_list_nesting(self, soup, file_path):
        """Check that lists are properly nested."""
        self.tests_run += 1

        nesting_issues = []

        # Check for orphaned ordered lists that should be nested
        for ol in soup.find_all('ol'):
            # Check if this ol is at the root level (not nested)
            parent = ol.parent
            if parent.name in ['body', 'article', 'section', 'div', 'main']:
                # This ol is not nested - check if it should be
                prev = ol.find_previous_sibling()
                if prev:
                    # If previous is an alpha list, this ol should likely be nested
                    if prev.name == 'ul' and 'alpha-list' in prev.get('class', []):
                        nesting_issues.append(f"Orphaned <ol> found after alpha list - should be nested under the last alpha item")
                    # If previous is a paragraph with just (a) or (b) etc, also problematic
                    elif prev.name == 'p' and re.match(r'^\([a-z]\)', prev.get_text().strip()):
                        nesting_issues.append(f"Orphaned <ol> found after alpha paragraph - both should be properly formatted")

        # Check for alpha lists with numeric sub-lists
        for ul in soup.find_all('ul', class_='alpha-list'):
            for li in ul.find_all('li', recursive=False):
                # Check if this item should have nested content
                text = li.get_text()
                if 'means' in text and ':' in text:
                    # Should have a nested list
                    nested = li.find('ul')
                    if not nested:
                        marker = li.find('span', class_='list-marker-alpha')
                        if marker:
                            nesting_issues.append(f"Item {marker.get_text()} missing nested list")

        if nesting_issues:
            self.failures.append({
                'file': file_path,
                'test': 'proper_list_nesting',
                'issue': f'Found {len(nesting_issues)} nesting issues',
                'examples': nesting_issues[:3]
            })
            print(f"  ❌ Found {len(nesting_issues)} nesting issues")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Proper list nesting")
            return True

    def test_css_classes(self, soup, file_path):
        """Check that lists have proper CSS classes."""
        self.tests_run += 1

        missing_classes = []
        for ul in soup.find_all('ul'):
            if not ul.get('class'):
                # Check what type of list this should be
                first_li = ul.find('li')
                if first_li:
                    marker = first_li.find('span')
                    if marker and marker.get_text():
                        missing_classes.append(f"List starting with {marker.get_text()} missing CSS class")

        if missing_classes:
            self.failures.append({
                'file': file_path,
                'test': 'css_classes',
                'issue': f'Found {len(missing_classes)} lists missing CSS classes',
                'examples': missing_classes[:3]
            })
            print(f"  ❌ Found {len(missing_classes)} lists missing CSS classes")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ All lists have proper CSS classes")
            return True

    def test_section_1050_formatting(self, soup, file_path):
        """Specific test for Section 1.050 definitions."""
        self.tests_run += 1

        issues = []

        # Find Section 1.050
        section = None
        for h3 in soup.find_all('h3'):
            if 'Section 1.050' in h3.get_text():
                section = h3
                break

        if not section:
            print(f"  ⚠️  Section 1.050 not found")
            return True

        # Check that items (h), (i), (j), (k), (l) are list items
        expected_items = ['(h)', '(i)', '(j)', '(k)', '(l)']
        found_items = []

        # Look for the list after Section 1.050
        current = section.find_next_sibling()
        while current and current.name != 'h3':
            if current.name == 'ul' and 'alpha-list' in current.get('class', []):
                for li in current.find_all('li', recursive=False):
                    marker = li.find('span', class_='list-marker-alpha')
                    if marker and marker.get_text() in expected_items:
                        found_items.append(marker.get_text())
            current = current.find_next_sibling()

        missing = set(expected_items) - set(found_items)
        if missing:
            issues.append(f"Missing list items: {', '.join(sorted(missing))}")

        # Check that (i) "Lot" has proper nested items
        for ul in soup.find_all('ul', class_='alpha-list'):
            for li in ul.find_all('li', recursive=False):
                marker = li.find('span', class_='list-marker-alpha')
                if marker and marker.get_text() == '(i)' and '"Lot"' in li.get_text():
                    nested = li.find('ul', class_='numeric-list')
                    if not nested:
                        issues.append("Item (i) 'Lot' missing nested numeric list")
                    else:
                        nested_items = nested.find_all('li', recursive=False)
                        if len(nested_items) < 3:
                            issues.append(f"Item (i) 'Lot' has only {len(nested_items)} nested items, expected 3")

        if issues:
            self.failures.append({
                'file': file_path,
                'test': 'section_1050_formatting',
                'issue': 'Section 1.050 formatting issues',
                'examples': issues
            })
            print(f"  ❌ Section 1.050 has {len(issues)} issues")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Section 1.050 properly formatted")
            return True

    def test_section_2060_formatting(self, soup, file_path):
        """Specific test for Section 2.060 to ensure no code blocks."""
        self.tests_run += 1

        # Find Section 2.060
        section = None
        for h3 in soup.find_all('h3'):
            if 'Section 2.060' in h3.get_text():
                section = h3
                break

        if not section:
            print(f"  ⚠️  Section 2.060 not found")
            return True

        # Check for code blocks near this section
        current = section
        for _ in range(10):  # Check next 10 elements
            current = current.find_next_sibling()
            if not current:
                break
            if current.name == 'pre':
                code = current.find('code')
                if code and 'floor area' in code.get_text():
                    self.failures.append({
                        'file': file_path,
                        'test': 'section_2060_formatting',
                        'issue': 'Section 2.060(b) items appearing as code block',
                        'examples': [code.get_text()[:100]]
                    })
                    print(f"  ❌ Section 2.060(b) has code block issue")
                    return False

        self.tests_passed += 1
        print(f"  ✅ Section 2.060 properly formatted")
        return True

    def test_section_5080_formatting(self, soup, file_path):
        """Specific test for Section 5.080 setback formatting with special div structure."""
        self.tests_run += 1

        # Find Section 5.080
        section = None
        for h3 in soup.find_all('h3'):
            if 'Section 5.080' in h3.get_text() and 'Building Setbacks' in h3.get_text():
                section = h3
                break

        if not section:
            print(f"  ⚠️  Section 5.080 not found")
            return True

        issues = []

        # Look for the alpha list after Section 5.080
        current = section.find_next_sibling()
        found_setback_divs = 0

        while current and current.name != 'h3':
            if current.name == 'ul' and 'alpha-list' in current.get('class', []):
                # Check items (a) and (c) for setback specifications
                for li in current.find_all('li', recursive=False):
                    marker = li.find('span', class_='list-marker-alpha')
                    if marker and marker.get_text() in ['(a)', '(c)']:
                        # These should have setback-specifications divs
                        setback_div = li.find('div', class_='setback-specifications')
                        if not setback_div:
                            issues.append(f"Item {marker.get_text()} missing setback-specifications div")
                        else:
                            found_setback_divs += 1
                            # Check that we have separate p elements for each setback
                            setback_ps = setback_div.find_all('p', class_='setback-spec')
                            if marker.get_text() == '(a)':
                                if len(setback_ps) != 4:
                                    issues.append(f"Item (a) has {len(setback_ps)} setback specs, expected 4")
                                else:
                                    # Check that each spec is on its own line
                                    for p in setback_ps:
                                        text = p.get_text()
                                        # Each spec should be just one line (Front/Side/Rear Setback - X feet)
                                        if text.count('Setback') > 1:
                                            issues.append(f"Setback specs not properly separated: {text[:50]}...")
                            elif marker.get_text() == '(c)':
                                if len(setback_ps) != 4:
                                    issues.append(f"Item (c) has {len(setback_ps)} setback specs, expected 4")
            current = current.find_next_sibling()

        if found_setback_divs == 0:
            issues.append("No setback-specifications divs found in Section 5.080")
        elif found_setback_divs != 2:
            issues.append(f"Found {found_setback_divs} setback-specifications divs, expected 2")

        if issues:
            self.failures.append({
                'file': file_path,
                'test': 'section_5080_formatting',
                'issue': 'Section 5.080 special formatting issues',
                'examples': issues
            })
            print(f"  ❌ Section 5.080 has {len(issues)} issues")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Section 5.080 properly formatted with special setback divs")
            return True

    def test_section_5110_formatting(self, soup, file_path):
        """Test that Section 5.110 items (a) through (e) are combined into a single alpha list."""
        self.tests_run += 1

        # Find Section 5.110
        section = None
        for h3 in soup.find_all('h3'):
            if 'Section 5.110' in h3.get_text() and 'Houses Moved' in h3.get_text():
                section = h3
                break

        if not section:
            print(f"  ⚠️  Section 5.110 not found")
            return True

        issues = []

        # Look for the alpha list after Section 5.110
        current = section.find_next_sibling()
        found_list = False
        orphaned_items = []

        while current and current.name not in ['h2', 'h3', 'hr']:
            if current.name == 'ul' and 'alpha-list' in current.get('class', []):
                found_list = True
                items = current.find_all('li', recursive=False)
                markers = []
                for li in items:
                    marker = li.find('span', class_='list-marker-alpha')
                    if marker:
                        markers.append(marker.get_text())

                # Check that we have all 5 items in ONE list
                expected = ['(a)', '(b)', '(c)', '(d)', '(e)']
                if markers != expected:
                    issues.append(f"Section 5.110 has items {markers}, expected {expected}")
                    missing = set(expected) - set(markers)
                    if missing:
                        issues.append(f"Missing items: {', '.join(sorted(missing))}")
                break
            elif current.name == 'p':
                # Check for orphaned items that should be in the list
                text = current.get_text().strip()
                if text.startswith('(a)') or text.startswith('(b)') or text.startswith('(e)'):
                    orphaned_items.append(text[:50] + '...' if len(text) > 50 else text)
            current = current.find_next_sibling()

        if orphaned_items:
            issues.append(f"Found {len(orphaned_items)} orphaned items as paragraphs")

        if not found_list:
            issues.append("Section 5.110 alpha list not found")

        if issues:
            self.failures.append({
                'file': file_path,
                'test': 'section_5110_formatting',
                'issue': 'Section 5.110 list not properly combined',
                'examples': issues
            })
            print(f"  ❌ Section 5.110 has {len(issues)} issues")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Section 5.110 properly formatted with all 5 items in single list")
            return True

    def test_section_5120_formatting(self, soup, file_path):
        """Specific test for Section 5.120 Home Occupations formatting."""
        self.tests_run += 1

        # Find Section 5.120
        section = None
        for h3 in soup.find_all('h3'):
            if 'Section 5.120' in h3.get_text():
                section = h3
                break

        if not section:
            print(f"  ⚠️  Section 5.120 not found")
            return True

        issues = []

        # Check that numbered items are nested under alpha items, not orphaned
        current = section.find_next_sibling()
        while current and current.name != 'h3':
            if current.name == 'ol':
                # This is an orphaned ordered list - it should be nested!
                prev = current.find_previous_sibling()
                if prev and prev.name == 'ul' and 'alpha-list' in prev.get('class', []):
                    # The ol should be nested inside the last li of the ul
                    issues.append(f"Orphaned ordered list found after alpha list - should be nested")
                else:
                    issues.append(f"Orphaned ordered list found - should be nested under parent item")
            elif current.name == 'ul' and 'alpha-list' in current.get('class', []):
                # Check if alpha items have proper nested lists
                for li in current.find_all('li', recursive=False):
                    marker = li.find('span', class_='list-marker-alpha')
                    if marker:
                        marker_text = marker.get_text()
                        # Check if this item should have nested content
                        li_text = li.get_text()
                        if marker_text in ['(a)', '(b)'] and 'DEFINITION' in li_text or 'PURPOSE' in li_text:
                            # These should have nested numeric lists
                            nested = li.find('ol') or li.find('ul', class_='numeric-list')
                            if not nested:
                                # Check if there's an orphaned ol after this ul
                                next_elem = current.find_next_sibling()
                                if next_elem and next_elem.name == 'ol':
                                    issues.append(f"Item {marker_text} missing nested list - found orphaned ol instead")
            current = current.find_next_sibling()

        if issues:
            self.failures.append({
                'file': file_path,
                'test': 'section_5120_formatting',
                'issue': 'Section 5.120 formatting issues - numbered items not properly nested',
                'examples': issues
            })
            print(f"  ❌ Section 5.120 has {len(issues)} issues")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Section 5.120 properly formatted")
            return True

    def test_no_empty_list_items(self, soup, file_path):
        """Check for empty or nearly empty list items."""
        self.tests_run += 1

        empty_items = []
        for li in soup.find_all('li'):
            text = li.get_text().strip()
            # Remove marker text to check actual content
            marker = li.find('span', class_=['list-marker-alpha', 'list-marker-numeric', 'list-marker-roman'])
            if marker:
                marker_text = marker.get_text()
                content = text.replace(marker_text, '').strip()
                if not content or len(content) < 3:
                    empty_items.append(f"Item {marker_text} is empty or too short: '{content}'")

        if empty_items:
            self.failures.append({
                'file': file_path,
                'test': 'no_empty_list_items',
                'issue': f'Found {len(empty_items)} empty or nearly empty list items',
                'examples': empty_items[:3]
            })
            print(f"  ❌ Found {len(empty_items)} empty list items")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ No empty list items")
            return True

    def test_proper_marker_spacing(self, soup, file_path):
        """Check that list markers have proper spacing."""
        self.tests_run += 1

        spacing_issues = []
        for li in soup.find_all('li'):
            marker = li.find('span', class_=['list-marker-alpha', 'list-marker-numeric', 'list-marker-roman'])
            if marker:
                # Check if there's proper spacing after marker
                next_sibling = marker.next_sibling
                if next_sibling and isinstance(next_sibling, str):
                    if not next_sibling.startswith(' '):
                        spacing_issues.append(f"No space after marker {marker.get_text()}")
                elif not next_sibling or (hasattr(next_sibling, 'name') and next_sibling.name):
                    # Marker followed directly by a tag or nothing
                    spacing_issues.append(f"Missing space after marker {marker.get_text()}")

        if spacing_issues:
            self.failures.append({
                'file': file_path,
                'test': 'proper_marker_spacing',
                'issue': f'Found {len(spacing_issues)} marker spacing issues',
                'examples': spacing_issues[:3]
            })
            print(f"  ❌ Found {len(spacing_issues)} spacing issues")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Proper marker spacing")
            return True

    def test_no_duplicate_list_items(self, soup, file_path):
        """Check for duplicate list items that might indicate processing errors."""
        self.tests_run += 1

        duplicates = []
        seen_items = {}

        for ul in soup.find_all('ul'):
            ul_class = ul.get('class', [])
            if any(cls in ul_class for cls in ['alpha-list', 'numeric-list', 'roman-list']):
                for li in ul.find_all('li', recursive=False):
                    marker = li.find('span', class_=['list-marker-alpha', 'list-marker-numeric', 'list-marker-roman'])
                    if marker:
                        marker_text = marker.get_text()
                        text_content = li.get_text()[:100]  # First 100 chars for comparison

                        key = (str(ul_class), marker_text, text_content)
                        if key in seen_items:
                            duplicates.append(f"Duplicate item {marker_text} in {ul_class}")
                        else:
                            seen_items[key] = True

        if duplicates:
            self.failures.append({
                'file': file_path,
                'test': 'no_duplicate_list_items',
                'issue': f'Found {len(duplicates)} duplicate list items',
                'examples': duplicates[:3]
            })
            print(f"  ❌ Found {len(duplicates)} duplicate items")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ No duplicate list items")
            return True

    def test_no_broken_nested_structure(self, soup, file_path):
        """Check for broken nested list structures."""
        self.tests_run += 1

        broken_structures = []

        for ul in soup.find_all('ul', class_='alpha-list'):
            for li in ul.find_all('li', recursive=False):
                marker = li.find('span', class_='list-marker-alpha')
                if marker:
                    marker_text = marker.get_text()

                    # Check for nested lists
                    nested_lists = li.find_all('ul', recursive=False)
                    for nested in nested_lists:
                        # Check if nested list has proper items
                        nested_items = nested.find_all('li', recursive=False)
                        if not nested_items:
                            broken_structures.append(f"Item {marker_text} has empty nested list")
                        else:
                            # Check if nested items have proper markers
                            for nested_li in nested_items:
                                nested_marker = nested_li.find('span')
                                if not nested_marker:
                                    broken_structures.append(f"Item {marker_text} has nested item without marker")

        if broken_structures:
            self.failures.append({
                'file': file_path,
                'test': 'no_broken_nested_structure',
                'issue': f'Found {len(broken_structures)} broken nested structures',
                'examples': broken_structures[:3]
            })
            print(f"  ❌ Found {len(broken_structures)} broken structures")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ No broken nested structures")
            return True

    def test_consistent_marker_styles(self, soup, file_path):
        """Check that marker styles are consistent within list types."""
        self.tests_run += 1

        inconsistencies = []

        # Check alpha lists
        for ul in soup.find_all('ul', class_='alpha-list'):
            markers = []
            for li in ul.find_all('li', recursive=False):
                marker = li.find('span', class_='list-marker-alpha')
                if marker:
                    markers.append(marker.get_text())

            # Check for consistent format - should all be (a), (b), (c) format
            for marker in markers:
                if not re.match(r'^\([a-z]\)$', marker):
                    inconsistencies.append(f"Alpha marker '{marker}' not in (x) format")

        # Check numeric lists
        for ul in soup.find_all('ul', class_='numeric-list'):
            markers = []
            for li in ul.find_all('li', recursive=False):
                marker = li.find('span', class_='list-marker-numeric')
                if marker:
                    markers.append(marker.get_text())

            # Check for consistent format - should all be (1), (2), (3) format
            for marker in markers:
                if not re.match(r'^\(\d+\)$', marker):
                    inconsistencies.append(f"Numeric marker '{marker}' not in (x) format")

        if inconsistencies:
            self.failures.append({
                'file': file_path,
                'test': 'consistent_marker_styles',
                'issue': f'Found {len(inconsistencies)} marker style inconsistencies',
                'examples': inconsistencies[:3]
            })
            print(f"  ❌ Found {len(inconsistencies)} style inconsistencies")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Consistent marker styles")
            return True

    def test_proper_definition_nesting(self, soup, file_path):
        """Check that definition items have proper nested sub-definitions."""
        self.tests_run += 1

        definition_issues = []

        # Look for definition patterns that should have nested items
        for ul in soup.find_all('ul', class_='alpha-list'):
            for li in ul.find_all('li', recursive=False):
                marker = li.find('span', class_='list-marker-alpha')
                if marker:
                    marker_text = marker.get_text()
                    li_text = li.get_text()

                    # Known patterns that should have nested definitions
                    should_have_nested = False
                    expected_nested = []

                    if '"Lot"' in li_text and 'means' in li_text:
                        should_have_nested = True
                        expected_nested = ['Corner Lot', 'Reversed Corner Lot', 'Through Lot']

                    elif '"Street"' in li_text and 'including' in li_text:
                        should_have_nested = True
                        expected_nested = ['Alley', 'Arterial', 'Collector', 'Cul-de-sac']

                    if should_have_nested:
                        nested_list = li.find('ul', class_='numeric-list')
                        if not nested_list:
                            definition_issues.append(f"Item {marker_text} should have nested definitions but has none")
                        else:
                            # Check if expected definitions are present
                            nested_items = nested_list.find_all('li', recursive=False)
                            found_definitions = []
                            for nested_li in nested_items:
                                nested_text = nested_li.get_text()
                                for expected in expected_nested:
                                    if expected in nested_text:
                                        found_definitions.append(expected)

                            missing = set(expected_nested) - set(found_definitions)
                            if missing:
                                definition_issues.append(f"Item {marker_text} missing nested definitions: {', '.join(missing)}")

        if definition_issues:
            self.failures.append({
                'file': file_path,
                'test': 'proper_definition_nesting',
                'issue': f'Found {len(definition_issues)} definition nesting issues',
                'examples': definition_issues[:3]
            })
            print(f"  ❌ Found {len(definition_issues)} definition nesting issues")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Proper definition nesting")
            return True

    def print_summary(self):
        """Print test summary and save results."""
        print("\n" + "="*60)
        print(f"📊 TEST SUMMARY")
        print("="*60)
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_run - self.tests_passed}")

        if self.failures:
            print(f"\n❌ FAILURES ({len(self.failures)}):")
            for failure in self.failures:
                print(f"\n  File: {failure['file']}")
                print(f"  Test: {failure['test']}")
                print(f"  Issue: {failure['issue']}")
                if failure['examples']:
                    print(f"  Examples:")
                    for ex in failure['examples']:
                        print(f"    - {ex}")
        else:
            print("\n✅ All tests passed!")

        # Save results to JSON for potential automation
        results = {
            'tests_run': self.tests_run,
            'tests_passed': self.tests_passed,
            'failures': self.failures
        }

        results_file = Path('scripts/tests/list-test-results.json')
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {results_file}")

        return len(self.failures) == 0

    def test_inline_numeric_references(self, soup, file_path):
        """Test that inline numeric references like (10) days are not converted to lists."""
        self.tests_run += 1

        issues = []

        # Check for improperly converted inline references
        for ul in soup.find_all('ul'):
            for li in ul.find_all('li', recursive=False):
                marker = li.find('span', class_='list-marker-numeric')
                if marker:
                    marker_text = marker.get_text()
                    li_text = li.get_text()
                    # Check for common inline reference patterns
                    if marker_text == '(10)' and 'days' in li_text[:20]:
                        issues.append(f"Inline reference '{marker_text} days' incorrectly converted to list item")
                    elif marker_text == '(20)' and 'percent' in li_text[:30]:
                        issues.append(f"Inline reference '{marker_text} percent' incorrectly converted to list item")

        if issues:
            self.failures.append({
                'file': file_path,
                'test': 'inline_numeric_references',
                'issue': 'Inline numeric references incorrectly converted to list items',
                'examples': issues[:3]
            })
            print(f"  ❌ Found {len(issues)} inline reference issues")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Inline numeric references preserved correctly")
            return True

    def test_paragraph_references(self, soup, file_path):
        """Test that paragraph references like '(a) which' are not converted to lists."""
        self.tests_run += 1

        issues = []

        # Check for improperly converted paragraph references
        for ul in soup.find_all('ul'):
            for li in ul.find_all('li', recursive=False):
                li_text = li.get_text().strip()
                # Check for patterns that indicate a paragraph reference
                if li_text.startswith('which') or li_text.startswith('that') or li_text.startswith('as '):
                    marker = li.find('span', class_='list-marker-alpha')
                    if marker:
                        issues.append(f"Paragraph reference '{marker.get_text()} {li_text[:30]}...' incorrectly as list")

        if issues:
            self.failures.append({
                'file': file_path,
                'test': 'paragraph_references',
                'issue': 'Paragraph references incorrectly converted to list items',
                'examples': issues[:3]
            })
            print(f"  ❌ Found {len(issues)} paragraph reference issues")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Paragraph references preserved correctly")
            return True

    def test_section_2060_nested_list(self, soup, file_path):
        """Test that Section 2.060(b) has properly nested numeric list."""
        self.tests_run += 1

        # Find Section 2.060
        section = None
        for h3 in soup.find_all('h3'):
            if 'Section 2.060' in h3.get_text() and 'Nonconforming' in h3.get_text():
                section = h3
                break

        if not section:
            # Not all files have this section
            return True

        issues = []

        # Look for the list after Section 2.060
        current = section.find_next_sibling()
        found_nested = False

        while current and current.name not in ['h2', 'h3', 'hr']:
            if current.name == 'ul' and 'alpha-list' in current.get('class', []):
                # Find item (b)
                for li in current.find_all('li', recursive=False):
                    marker = li.find('span', class_='list-marker-alpha')
                    if marker and marker.get_text() == '(b)':
                        # Check for nested numeric list
                        nested = li.find('ul', class_='numeric-list')
                        if nested:
                            found_nested = True
                            nested_items = nested.find_all('li', recursive=False)
                            if len(nested_items) != 3:
                                issues.append(f"Section 2.060(b) has {len(nested_items)} nested items, expected 3")
                        else:
                            issues.append("Section 2.060(b) missing nested numeric list")
                        break
            # Also check for orphaned code blocks
            elif current.name == 'pre':
                code = current.find('code')
                if code and '(1)' in code.get_text() and '(2)' in code.get_text():
                    issues.append("Section 2.060 nested list appearing as code block")
            current = current.find_next_sibling()

        if issues:
            self.failures.append({
                'file': file_path,
                'test': 'section_2060_nested_list',
                'issue': 'Section 2.060 nested list formatting issues',
                'examples': issues
            })
            print(f"  ❌ Section 2.060 has {len(issues)} issues")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Section 2.060 nested list formatted correctly")
            return True

    def test_section_2080_single_item(self, soup, file_path):
        """Test that Section 2.080 single-item list is preserved."""
        self.tests_run += 1

        # Find Section 2.080
        section = None
        for h3 in soup.find_all('h3'):
            if 'Section 2.080' in h3.get_text() and 'Termination' in h3.get_text():
                section = h3
                break

        if not section:
            # Not all files have this section
            return True

        issues = []

        # Look for the single-item list
        current = section.find_next_sibling()
        found_list = False

        while current and current.name not in ['h2', 'h3', 'hr']:
            if current.name == 'ul' and 'alpha-list' in current.get('class', []):
                found_list = True
                items = current.find_all('li', recursive=False)
                if len(items) != 1:
                    issues.append(f"Section 2.080 has {len(items)} list items, expected 1")
                else:
                    marker = items[0].find('span', class_='list-marker-alpha')
                    if not marker or marker.get_text() != '(a)':
                        issues.append("Section 2.080 single item not marked as (a)")
                break
            elif current.name == 'p' and current.get_text().strip().startswith('(a)'):
                issues.append("Section 2.080 item (a) not converted to list")
            current = current.find_next_sibling()

        if not found_list and not issues:
            issues.append("Section 2.080 list not found")

        if issues:
            self.failures.append({
                'file': file_path,
                'test': 'section_2080_single_item',
                'issue': 'Section 2.080 single-item list issues',
                'examples': issues
            })
            print(f"  ❌ Section 2.080 has {len(issues)} issues")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Section 2.080 single-item list correct")
            return True

    def test_section_4120_complete_list(self, soup, file_path):
        """Test that Section 4.120 has all four items (a), (b), (c), (d) in the list."""
        self.tests_run += 1

        # Find Section 4.120
        section = None
        for h3 in soup.find_all('h3'):
            if 'Section 4.120' in h3.get_text() and 'Type IV' in h3.get_text():
                section = h3
                break

        if not section:
            # Not all files have this section
            return True

        issues = []

        # Look for the list after Section 4.120
        current = section.find_next_sibling()
        found_list = False
        found_items = []

        while current and current.name not in ['h2', 'hr']:
            if current.name == 'ul' and 'alpha-list' in current.get('class', []):
                found_list = True
                for li in current.find_all('li', recursive=False):
                    marker = li.find('span', class_='list-marker-alpha')
                    if marker:
                        found_items.append(marker.get_text())
                break
            # Check for orphaned (d) item
            elif current.name == 'p':
                text = current.get_text().strip()
                if text.startswith('(d)') and 'To the extent that a policy' in text:
                    issues.append("Section 4.120 item (d) not included in list")
            current = current.find_next_sibling()

        if found_list:
            expected = ['(a)', '(b)', '(c)', '(d)']
            if found_items != expected:
                issues.append(f"Section 4.120 has items {found_items}, expected {expected}")
        else:
            issues.append("Section 4.120 list not found")

        if issues:
            self.failures.append({
                'file': file_path,
                'test': 'section_4120_complete_list',
                'issue': 'Section 4.120 list completeness issues',
                'examples': issues
            })
            print(f"  ❌ Section 4.120 has {len(issues)} issues")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Section 4.120 list complete with all 4 items")
            return True

    def test_ord_65_section_2_formatting(self, soup, file_path):
        """
        Specific test for Ordinance 65-99 Section 2 to ensure "C. The parties agree:"
        is properly extracted from nested list structure.

        This tests the one-off fix for the edge case where a bold paragraph header
        appeared after nested alpha sub-items (a, b) and was being treated as
        list continuation instead of a section header.
        """
        self.tests_run += 1

        issues = []

        # Find Section 2 heading
        section = None
        for h3 in soup.find_all('h3'):
            if 'Section 2' in h3.get_text() and 'Operating Procedures' in h3.get_text():
                section = h3
                break

        if not section:
            # This section only exists in Ord 65-99
            print(f"  ⚠️  Section 2 Operating Procedures not found")
            return True

        # Find the paragraph containing "C. The parties agree:"
        c_paragraph = None
        for p in soup.find_all('p'):
            strong = p.find('strong')
            if strong and 'C. The parties agree:' in strong.get_text():
                c_paragraph = p
                break

        if not c_paragraph:
            issues.append("'C. The parties agree:' paragraph not found")
        else:
            # Check that C is NOT inside a list item
            parent_li = c_paragraph.find_parent('li')
            if parent_li:
                issues.append("'C. The parties agree:' is still inside a <li> - should be extracted")

            # Check that C is NOT inside an ordered list
            parent_ol = c_paragraph.find_parent('ol')
            if parent_ol:
                issues.append("'C. The parties agree:' is still inside an <ol> - should be outside")

            # Check that C is at the same level as "B. Lake Oswego agrees to:"
            # Find B header
            b_paragraph = None
            for p in soup.find_all('p'):
                strong = p.find('strong')
                if strong and 'B. Lake Oswego agrees to:' in strong.get_text():
                    b_paragraph = p
                    break

            if b_paragraph and c_paragraph:
                # They should have the same parent
                if b_paragraph.parent != c_paragraph.parent:
                    # Check if C is between two ols (which is correct)
                    prev_elem = c_paragraph.find_previous_sibling()
                    next_elem = c_paragraph.find_next_sibling()
                    if prev_elem and prev_elem.name == 'ol' and next_elem and next_elem.name == 'ol':
                        # This is correct - C is between B's list and C's list
                        pass
                    else:
                        issues.append("'C. The parties agree:' not at same structural level as 'B. Lake Oswego agrees to:'")

        if issues:
            self.failures.append({
                'file': file_path,
                'test': 'ord_65_section_2_formatting',
                'issue': 'Ordinance 65-99 Section 2 "C. The parties agree:" formatting issues',
                'examples': issues
            })
            print(f"  ❌ Ord 65-99 Section 2 has {len(issues)} issues")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Ord 65-99 Section 2 'C. The parties agree:' correctly positioned")
            return True

def main():
    """Run list formatting tests."""
    tester = ListFormattingTester()

    if len(sys.argv) > 1:
        # Test specific files
        files = sys.argv[1:]
        for file_path in files:
            tester.test_file(file_path)
    else:
        # Test all known problem files
        test_files = [
            'book/ordinances/1989-Ord-54-89C-Land-Development.html',
            'book/ordinances/1998-Ord-59-97A-Land-Development-Amendment.html',
            'book/ordinances/2003-Ord-73-2003A-Conditional-Use-Provisions.html',
        ]

        for file_path in test_files:
            if Path(file_path).exists():
                tester.test_file(file_path)

        # Also test a sample of other files
        book_dir = Path('book')
        if book_dir.exists():
            for subdir in ['ordinances', 'resolutions', 'interpretations']:
                subpath = book_dir / subdir
                if subpath.exists():
                    # Test first 2 files in each directory
                    for file in list(subpath.glob('*.html'))[:2]:
                        tester.test_file(str(file))

    success = tester.print_summary()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()