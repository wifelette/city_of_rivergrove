#!/usr/bin/env python3
"""
Unified List Processor v2 - Single source of truth for all list processing.
Handles all list transformations in one pass to avoid order-of-operations issues.

This replaces:
- fix-indented-lists.py
- custom-list-processor.py
- Parts of enhanced-custom-processor.py related to lists

Author: Claude
Date: 2025
"""

from bs4 import BeautifulSoup, NavigableString, Tag
from pathlib import Path
import re
import sys

class UnifiedListProcessor:
    """Handles all list processing in a single, coordinated pass."""

    def __init__(self, soup):
        self.soup = soup
        self.changes_made = False

    def process_all(self):
        """Main entry point - processes all list types in correct order."""

        # Phase 1: Convert raw text patterns to proper list structures
        self._convert_text_to_lists()

        # Phase 2: Fix mdBook's interpretation issues
        self._fix_mdbook_issues()

        # Phase 3: Handle special cases
        self._process_special_lists()

        # Phase 4: Apply consistent styling
        self._apply_list_styling()

        return self.changes_made

    def _convert_text_to_lists(self):
        """Phase 1: Find and convert text patterns that should be lists."""

        # Convert paragraphs with (a), (b), (c) patterns
        for p in self.soup.find_all('p'):
            text = p.get_text()

            # Check for alpha markers: (a), (b), (c)
            if re.match(r'^\([a-z]\)', text):
                self._convert_alpha_paragraph(p)

            # Check for numeric patterns in paragraphs
            elif re.search(r'\(\d+\)', text) or re.search(r'\d+\)', text):
                self._check_numeric_patterns(p)

    def _convert_alpha_paragraph(self, p):
        """Convert a paragraph starting with (a), (b), etc. to proper list."""
        text = p.get_text()
        match = re.match(r'^(\([a-z]\))\s*(.*)$', text, re.DOTALL)

        if not match:
            return

        marker = match.group(1)
        content = match.group(2)

        # Find or create parent list
        parent_ul = self._find_or_create_parent_list(p, 'alpha-list')

        # Create list item
        li = self.soup.new_tag('li')
        span = self.soup.new_tag('span', **{'class': 'list-marker-alpha'})
        span.string = marker
        li.append(span)
        li.append(' ')

        # Check for embedded sub-lists
        self._process_embedded_items(li, content)

        parent_ul.append(li)
        p.extract()
        self.changes_made = True
        print(f"  Converted paragraph {marker} to list item")

    def _process_embedded_items(self, li, content):
        """Check for and process sub-items embedded in content."""

        # Check for numeric sub-items: (1), (2), (3) or 1), 2), 3)
        numeric_pattern = r'\n?\(?\d+\)(?:\s+|\.)'
        if re.search(numeric_pattern, content):
            self._extract_numeric_subitems(li, content)

        # Check for roman numerals: (i), (ii), (iii)
        elif re.search(r'\([ivx]+\)', content):
            self._extract_roman_subitems(li, content)

        # Check for setback patterns
        elif 'Setback' in content and ' - ' in content:
            self._extract_setback_items(li, content)

        else:
            # No sub-items, just add the content
            li.append(content)

    def _extract_numeric_subitems(self, li, content):
        """Extract numeric sub-items from content."""
        # Split content into main text and sub-items
        parts = re.split(r'\n(?=\(?\d+[\)\.]\s)', content)

        if parts[0].strip():
            li.append(parts[0].strip())

        if len(parts) > 1:
            nested_ul = self.soup.new_tag('ul', **{'class': 'numeric-list'})

            for part in parts[1:]:
                part = part.strip()
                # Extract marker and content
                match = re.match(r'^(\(?)(\d+)([\)\.])?\s*(.*)$', part, re.DOTALL)
                if match:
                    num = match.group(2)
                    content_text = match.group(4)

                    # Normalize marker to (1) format
                    marker = f"({num})"

                    nested_li = self.soup.new_tag('li')
                    marker_span = self.soup.new_tag('span', **{'class': 'list-marker-numeric'})
                    marker_span.string = marker
                    nested_li.append(marker_span)
                    nested_li.append(' ' + content_text)
                    nested_ul.append(nested_li)

            li.append(nested_ul)
            print(f"  Created nested numeric list with {len(nested_ul.find_all('li'))} items")

    def _extract_roman_subitems(self, li, content):
        """Extract roman numeral sub-items from content."""
        parts = re.split(r'\n(?=\([ivx]+\))', content)

        if parts[0].strip():
            li.append(parts[0].strip())

        if len(parts) > 1:
            nested_ul = self.soup.new_tag('ul', **{'class': 'roman-list'})

            for part in parts[1:]:
                part = part.strip()
                match = re.match(r'^(\([ivx]+\))\s*(.*)$', part, re.IGNORECASE | re.DOTALL)
                if match:
                    marker = match.group(1)
                    content_text = match.group(2)

                    nested_li = self.soup.new_tag('li')
                    marker_span = self.soup.new_tag('span', **{'class': 'list-marker-roman'})
                    marker_span.string = marker
                    nested_li.append(marker_span)
                    nested_li.append(' ' + content_text)
                    nested_ul.append(nested_li)

            li.append(nested_ul)
            print(f"  Created nested roman list with {len(nested_ul.find_all('li'))} items")

    def _extract_setback_items(self, li, content):
        """Extract setback measurements into a nested list."""
        lines = content.split('\n')
        main_text = ''
        setback_lines = []

        for line in lines:
            line = line.strip()
            if line and ('Setback' in line and ' - ' in line):
                setback_lines.append(line)
            elif line and not setback_lines:
                if main_text:
                    main_text += ' '
                main_text += line

        if main_text:
            li.append(main_text)

        if setback_lines:
            nested_ul = self.soup.new_tag('ul', **{'class': 'setback-list'})
            for setback in setback_lines:
                nested_li = self.soup.new_tag('li')
                nested_li.string = setback
                nested_ul.append(nested_li)
            li.append(nested_ul)
            print(f"  Created setback list with {len(setback_lines)} items")

    def _fix_mdbook_issues(self):
        """Phase 2: Fix issues created by mdBook's interpretation."""

        # Fix code blocks that should be lists
        self._fix_code_block_lists()

        # Fix orphaned ordered lists
        self._fix_orphaned_ordered_lists()

        # Fix misplaced list items
        self._fix_misplaced_items()

    def _fix_code_block_lists(self):
        """Convert code blocks that are actually lists back to proper format."""
        for pre in self.soup.find_all('pre'):
            code = pre.find('code')
            if not code:
                continue

            text = code.get_text()

            # Check if this looks like list items
            # Match patterns like (1), (2), (3) or 1., 2., 3. or (i), (ii), (iii)
            if re.match(r'^\s*(\()?([1-9]|[ivx]+)[\)\.]\s', text):
                self._convert_code_block_to_list(pre, text)

    def _convert_code_block_to_list(self, pre, text):
        """Convert a code block to a proper list."""
        lines = text.split('\n')

        # Determine list type
        is_roman = bool(re.match(r'^\s*(\()?[ivx]+[\)\.]\s', text))
        list_class = 'roman-list' if is_roman else 'numeric-list'
        marker_class = 'list-marker-roman' if is_roman else 'list-marker-numeric'

        new_ul = self.soup.new_tag('ul', **{'class': list_class})

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Match both (1) and 1. formats
            match = re.match(r'^(\()?([0-9ivx]+)([\)\.]+)\s*(.*)$', line, re.IGNORECASE)
            if match:
                # Normalize marker to (1) format
                num = match.group(2)
                marker = f"({num})"
                content = match.group(4)

                li = self.soup.new_tag('li')
                span = self.soup.new_tag('span', **{'class': marker_class})
                span.string = marker
                li.append(span)
                li.append(' ' + content)
                new_ul.append(li)

        # Check if this should be nested under a previous item
        prev = pre.find_previous_sibling()
        if prev and prev.name == 'ul' and 'alpha-list' in prev.get('class', []):
            # Find the last item in the alpha list - that's where this should be nested
            last_li = prev.find_all('li', recursive=False)[-1]
            if last_li:
                last_li.append(new_ul)
                pre.extract()
                self.changes_made = True
                print(f"  Fixed code block with {len(new_ul.find_all('li'))} items, nested under alpha item")
                return
        elif prev and prev.name == 'p' and re.match(r'^\([a-z]\)', prev.get_text()):
            # This should be nested
            self._nest_list_under_previous(prev, new_ul)
            pre.extract()
        else:
            pre.replace_with(new_ul)

        self.changes_made = True
        print(f"  Fixed code block with {len(new_ul.find_all('li'))} items")

    def _nest_list_under_previous(self, prev_p, new_ul):
        """Helper to convert paragraph to list item and nest the list under it."""
        # Convert the paragraph to a list item
        text = prev_p.get_text()
        match = re.match(r'^(\([a-z]\))\s*(.*)$', text, re.DOTALL)

        if not match:
            return

        marker = match.group(1)
        content = match.group(2)

        # Find or create parent list
        parent_ul = self._find_or_create_parent_list(prev_p, 'alpha-list')

        # Create list item
        li = self.soup.new_tag('li')
        span = self.soup.new_tag('span', **{'class': 'list-marker-alpha'})
        span.string = marker
        li.append(span)
        li.append(' ')

        if content.strip():
            li.append(content.strip())

        # Nest the new list under this item
        li.append(new_ul)

        parent_ul.append(li)
        prev_p.extract()

    def _fix_orphaned_ordered_lists(self):
        """Fix <ol> elements that should be nested under alpha items."""
        for ul in self.soup.find_all('ul', class_='alpha-list'):
            for li in ul.find_all('li', recursive=False):
                text = li.get_text().strip()
                if text.endswith(':'):
                    # Check for an orphaned <ol> after the parent ul
                    next_sibling = ul.find_next_sibling()
                    if next_sibling and next_sibling.name == 'ol':
                        self._nest_ordered_list(li, next_sibling)

    def _nest_ordered_list(self, li, ol):
        """Nest an ordered list inside a list item."""
        new_ul = self.soup.new_tag('ul', **{'class': 'numeric-list'})

        for idx, ol_li in enumerate(ol.find_all('li'), 1):
            new_li = self.soup.new_tag('li')
            marker = f"({idx})"
            marker_span = self.soup.new_tag('span', **{'class': 'list-marker-numeric'})
            marker_span.string = marker
            new_li.append(marker_span)
            new_li.append(' ')

            # Add content
            for child in ol_li.children:
                if child.name == 'p':
                    new_li.append(child.get_text().strip())
                elif isinstance(child, str) and child.strip():
                    new_li.append(child.strip())

            new_ul.append(new_li)

        li.append(new_ul)
        ol.extract()
        self.changes_made = True
        print(f"  Fixed orphaned ordered list with {len(new_ul.find_all('li'))} items")

    def _fix_misplaced_items(self):
        """Fix list items that are in the wrong place."""
        for ul in self.soup.find_all('ul', class_='alpha-list'):
            items = ul.find_all('li', recursive=False)

            i = 0
            while i < len(items):
                li = items[i]

                # Check for concatenated numeric items in this li
                self._fix_concatenated_numeric_items(li)

                # Check if next item should be nested under this one
                if i + 1 < len(items):
                    next_li = items[i + 1]
                    if self._should_be_nested(li, next_li):
                        self._nest_item(li, next_li)
                        items = ul.find_all('li', recursive=False)
                        continue

                i += 1

    def _fix_concatenated_numeric_items(self, li):
        """Fix list items that have multiple numeric items concatenated together."""
        # Check if this li has a nested numeric list
        nested_list = li.find('ul', class_='numeric-list')
        if not nested_list:
            return

        # Check the nested items for concatenation
        for nested_li in list(nested_list.find_all('li', recursive=False)):
            text_content = nested_li.get_text()

            # Check if we have multiple numeric markers (2. 3. 4.)
            if re.findall(r'\b[2-9]\.\s*"', text_content):
                # Split on numeric patterns
                parts = re.split(r'(\b[1-9]\.)\s*(".*?"[^"]*?)(?=\b[1-9]\.|$)', text_content)

                if len(parts) > 3:  # We have multiple items
                    # Get all numeric items
                    numeric_items = []
                    i = 0
                    while i < len(parts) - 1:
                        if re.match(r'\b[1-9]\.', parts[i]):
                            num = parts[i].rstrip('.')
                            content = parts[i + 1] if i + 1 < len(parts) else ""
                            numeric_items.append((num, content.strip()))
                            i += 2
                        else:
                            i += 1

                    if numeric_items:
                        # Replace the first item with its proper content
                        first_item = numeric_items[0]

                        # Clear nested_li content but keep the marker
                        marker = nested_li.find('span', class_='list-marker-numeric')
                        for child in list(nested_li.children):
                            if child != marker:
                                if hasattr(child, 'extract'):
                                    child.extract()
                                else:
                                    child.replace_with('')

                        # Add back just the first item's content
                        nested_li.append(' ' + first_item[1])

                        # Create new list items for the rest
                        for num, content in numeric_items[1:]:
                            new_li = self.soup.new_tag('li')
                            marker_span = self.soup.new_tag('span', **{'class': 'list-marker-numeric'})
                            marker_span.string = f"({num})"
                            new_li.append(marker_span)
                            new_li.append(' ' + content)
                            # Insert after the current item
                            nested_li.insert_after(new_li)
                            nested_li = new_li  # Update reference for next insertion

                        self.changes_made = True
                        alpha_marker = li.find('span', class_='list-marker-alpha')
                        if alpha_marker:
                            print(f"  Split concatenated numeric items under {alpha_marker.get_text()}")

    def _should_be_nested(self, parent_li, next_li):
        """Determine if next_li should be nested under parent_li."""
        parent_marker = parent_li.find('span', class_='list-marker-alpha')
        next_marker = next_li.find('span')

        if not parent_marker or not next_marker:
            return False

        # Check if next item is numeric and parent ends with colon or means clause
        if 'list-marker-numeric' in next_marker.get('class', []):
            parent_text = parent_li.get_text()
            # Items that end with colon or have "means...:" pattern should have nested items
            if parent_text.endswith(':') or 'means' in parent_text and ':' in parent_text:
                return True

        return False

    def _nest_item(self, parent_li, child_li):
        """Nest child_li under parent_li and collect all consecutive numeric items."""
        # Check if parent already has a nested list
        existing_nested = parent_li.find('ul', class_='numeric-list')
        if not existing_nested:
            # Create new nested list
            nested_ul = self.soup.new_tag('ul', **{'class': 'numeric-list'})
            parent_li.append(nested_ul)
        else:
            nested_ul = existing_nested

        # Collect this numeric item and any consecutive numeric siblings
        items_to_nest = []
        current = child_li

        while current:
            # Check if this is a numeric item
            marker = current.find('span', class_='list-marker-numeric')
            if marker:
                items_to_nest.append(current)
                # Get next sibling
                next_sib = current.find_next_sibling('li')
                if next_sib:
                    next_marker = next_sib.find('span')
                    # Continue if it's also numeric
                    if next_marker and 'list-marker-numeric' in next_marker.get('class', []):
                        current = next_sib
                    else:
                        break
                else:
                    break
            else:
                break

        # Now nest all collected items
        for item in items_to_nest:
            # Get the marker and content
            marker = item.find('span', class_='list-marker-numeric')
            if marker:
                # Get the number from the marker
                marker_text = marker.get_text()
                # Normalize to (1) format
                if '.' in marker_text:
                    num = marker_text.rstrip('.')
                    new_marker = f"({num})"
                else:
                    new_marker = marker_text

                # Create new nested li
                new_li = self.soup.new_tag('li')
                new_span = self.soup.new_tag('span', **{'class': 'list-marker-numeric'})
                new_span.string = new_marker
                new_li.append(new_span)

                # Add the content (everything except the marker)
                for child in item.children:
                    if child != marker:
                        if isinstance(child, str):
                            new_li.append(child)
                        elif hasattr(child, 'clone'):
                            new_li.append(child.clone())
                        else:
                            new_li.append(str(child))

                nested_ul.append(new_li)

            # Remove the original item
            item.extract()

        if items_to_nest:
            self.changes_made = True
            parent_marker = parent_li.find('span', class_='list-marker-alpha')
            if parent_marker:
                print(f"  Nested {len(items_to_nest)} numeric items under {parent_marker.get_text()}")

    def _process_special_lists(self):
        """Phase 3: Handle special list types."""
        # This is where we'd add handling for any other special cases
        pass

    def _apply_list_styling(self):
        """Phase 4: Ensure all lists have proper CSS classes."""
        # Ensure all manual lists have proper classes
        for ul in self.soup.find_all('ul'):
            if not ul.get('class'):
                # Determine appropriate class based on content
                first_li = ul.find('li')
                if first_li:
                    marker = first_li.find('span')
                    if marker:
                        marker_text = marker.get_text()
                        if re.match(r'^\([a-z]\)$', marker_text):
                            ul['class'] = 'alpha-list'
                        elif re.match(r'^\(\d+\)$', marker_text):
                            ul['class'] = 'numeric-list'
                        elif re.match(r'^\([ivx]+\)$', marker_text, re.IGNORECASE):
                            ul['class'] = 'roman-list'

    def _find_or_create_parent_list(self, element, list_class):
        """Find or create a parent list for an element."""
        prev = element.find_previous_sibling()

        if prev and prev.name == 'ul' and list_class in prev.get('class', []):
            return prev

        # Create new list
        new_ul = self.soup.new_tag('ul', **{'class': list_class})
        element.insert_before(new_ul)
        return new_ul

    def _check_numeric_patterns(self, p):
        """Check if a paragraph contains numeric patterns that need processing."""
        text = p.get_text()

        # Skip if it's just regular text with parentheses
        if not re.search(r'\(\d+\).*\(\d+\)', text):
            return

        # This paragraph has multiple numeric items
        # Convert to a proper list structure
        # (Implementation would go here based on specific patterns)
        pass


def process_html_file(file_path):
    """Process a single HTML file."""
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return False

    with open(path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    processor = UnifiedListProcessor(soup)
    changes_made = processor.process_all()

    if changes_made:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"✓ Processed lists in {path.name}")
        return True

    return False


def main():
    """Process HTML files provided as arguments or all ordinance files."""
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        # Process all files in book directory
        book_dir = Path('book')
        if book_dir.exists():
            files = []
            for subdir in ['ordinances', 'resolutions', 'interpretations', 'other']:
                subpath = book_dir / subdir
                if subpath.exists():
                    files.extend(str(f) for f in subpath.glob('*.html'))
        else:
            print("No book directory found")
            return

    processed_count = 0
    for file_path in files:
        if process_html_file(file_path):
            processed_count += 1

    if processed_count > 0:
        print(f"\n✅ Processed {processed_count} file(s)")


if __name__ == '__main__':
    main()