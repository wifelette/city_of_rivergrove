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

        # Special tests for known problem areas
        if '1989-Ord-54' in file_path:
            all_passed &= self.test_section_1050_formatting(soup, file_path)
            all_passed &= self.test_section_2060_formatting(soup, file_path)
            all_passed &= self.test_section_5080_formatting(soup, file_path)
            all_passed &= self.test_section_5120_formatting(soup, file_path)

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
        """Specific test for Section 5.080 setback formatting."""
        self.tests_run += 1

        # Find Section 5.080
        section = None
        for h3 in soup.find_all('h3'):
            if 'Section 5.080' in h3.get_text():
                section = h3
                break

        if not section:
            print(f"  ⚠️  Section 5.080 not found")
            return True

        # Check for setback lists
        issues = []
        current = section.find_next_sibling()
        found_setback_list = False

        while current and current.name != 'h3':
            if current.name == 'ul':
                for li in current.find_all('li'):
                    if 'Front Setback' in li.get_text():
                        found_setback_list = True
                        # Check if it's properly formatted
                        parent_ul = li.find_parent('ul')
                        if 'setback-list' not in parent_ul.get('class', []):
                            issues.append("Setback list missing 'setback-list' CSS class")
            current = current.find_next_sibling()

        if not found_setback_list:
            issues.append("No setback lists found in Section 5.080")

        if issues:
            self.failures.append({
                'file': file_path,
                'test': 'section_5080_formatting',
                'issue': 'Section 5.080 formatting issues',
                'examples': issues
            })
            print(f"  ❌ Section 5.080 has {len(issues)} issues")
            return False
        else:
            self.tests_passed += 1
            print(f"  ✅ Section 5.080 properly formatted")
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