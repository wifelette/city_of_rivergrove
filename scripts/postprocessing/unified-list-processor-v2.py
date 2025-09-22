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

        # Fix orphaned paragraphs after single-item lists
        self._fix_orphaned_paragraphs()

        # Fix orphaned ordered lists
        self._fix_orphaned_ordered_lists()

        # Fix misplaced list items
        self._fix_misplaced_items()

        # Fix concatenated numeric items in list items
        self._fix_all_concatenated_items()

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

    def _fix_orphaned_paragraphs(self):
        """Fix paragraphs that should be nested inside list items."""
        # Find all alpha lists that might have orphaned content after them
        for ul in self.soup.find_all('ul', class_='alpha-list'):
            items = ul.find_all('li', recursive=False)

            # First handle single-item lists
            if len(items) == 1:
                li = items[0]

                # Collect all content that should be nested under this item
                content_to_nest = []
                next_elem = ul.find_next_sibling()

                while next_elem:
                    # Stop if we hit another alpha list or a heading
                    if (next_elem.name == 'ul' and 'alpha-list' in next_elem.get('class', [])) or \
                       next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        break

                    # Collect paragraphs
                    if next_elem.name == 'p':
                        content_to_nest.append(next_elem)
                        temp = next_elem.find_next_sibling()
                        next_elem = temp
                    # Also collect ordered lists
                    elif next_elem.name == 'ol':
                        content_to_nest.append(next_elem)
                        temp = next_elem.find_next_sibling()
                        next_elem = temp
                    else:
                        break

                # Now nest all collected content
                if content_to_nest:
                    for elem in content_to_nest:
                        if elem.name == 'p':
                            # Add paragraph content to the list item
                            li.append(' ')
                            li.append(elem.get_text().strip())
                            elem.extract()
                        elif elem.name == 'ol':
                            # Convert ol to proper nested list
                            self._nest_ordered_list(li, elem)

                    self.changes_made = True
                    marker = li.find('span', class_='list-marker-alpha')
                    if marker:
                        print(f"  Fixed orphaned content after {marker.get_text()}")

            # Also handle multi-item lists where last item should have content nested
            elif len(items) > 1:
                last_li = items[-1]
                text = last_li.get_text().strip()

                # Check if the last item indicates it should have nested content
                if (text.endswith(':') or
                    'following' in text.lower() or
                    'criteria' in text.lower() or
                    'shall be given' in text.lower() or
                    'consideration' in text.lower()):

                    # Collect orphaned numeric paragraphs
                    content_to_nest = []
                    next_elem = ul.find_next_sibling()

                    while next_elem:
                        # Stop at headings or other alpha lists
                        if next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                            break
                        if next_elem.name == 'ul' and 'alpha-list' in next_elem.get('class', []):
                            break

                        # Collect numeric paragraphs (starting with (1), (2), etc.)
                        if next_elem.name == 'p':
                            p_text = next_elem.get_text().strip()
                            if re.match(r'^\(\d+\)', p_text):
                                content_to_nest.append(next_elem)
                                temp = next_elem.find_next_sibling()
                                next_elem = temp
                            else:
                                break
                        else:
                            break

                    # Convert collected paragraphs to nested list
                    if content_to_nest:
                        new_ul = self.soup.new_tag('ul', **{'class': 'numeric-list'})

                        for p in content_to_nest:
                            p_text = p.get_text().strip()
                            # Extract number and content
                            match = re.match(r'^\((\d+)\)\s*(.+)$', p_text, re.DOTALL)
                            if match:
                                num = match.group(1)
                                content = match.group(2)

                                new_li = self.soup.new_tag('li')
                                marker_span = self.soup.new_tag('span', **{'class': 'list-marker-numeric'})
                                marker_span.string = f"({num})"
                                new_li.append(marker_span)
                                new_li.append(' ' + content)
                                new_ul.append(new_li)

                            p.extract()

                        last_li.append(new_ul)
                        self.changes_made = True

                        marker = last_li.find('span', class_='list-marker-alpha')
                        if marker:
                            print(f"  Fixed {len(content_to_nest)} orphaned numeric paragraphs after {marker.get_text()}")

    def _fix_orphaned_ordered_lists(self):
        """Fix <ol> elements that should be nested under alpha items."""
        # Look for all ordered lists that might be orphaned
        for ol in self.soup.find_all('ol'):
            # Check if this ol is immediately after an alpha list
            prev = ol.find_previous_sibling()

            # Handle case 1: ol directly after alpha list
            if prev and prev.name == 'ul' and 'alpha-list' in prev.get('class', []):
                # Get the last li in the alpha list
                last_li = prev.find_all('li', recursive=False)[-1] if prev.find_all('li', recursive=False) else None
                if last_li:
                    # Check if this li should have the ol nested under it
                    text = last_li.get_text().strip()
                    # Check various patterns that indicate this item should have nested content
                    if (text.endswith(':') or
                        'DEFINITION' in text or
                        'PURPOSE' in text or
                        'INTENT' in text or
                        text.endswith(')')):  # Just ends with a parenthesis like "(a) DEFINITION"
                        self._nest_ordered_list(last_li, ol)

            # Handle case 2: ol after a paragraph, which is after an alpha list
            elif prev and prev.name == 'p':
                # Check if there's an alpha list before the paragraph
                prev_prev = prev.find_previous_sibling()
                if prev_prev and prev_prev.name == 'ul' and 'alpha-list' in prev_prev.get('class', []):
                    # Get the last li in the alpha list
                    last_li = prev_prev.find_all('li', recursive=False)[-1] if prev_prev.find_all('li', recursive=False) else None
                    if last_li:
                        text = last_li.get_text().strip()
                        # Check if this item is likely the parent
                        if ('PURPOSE' in text or 'INTENT' in text or
                            'DEFINITION' in text or text.endswith(':')):
                            # Append the paragraph content first, then the list
                            p_text = prev.get_text().strip()
                            if p_text:
                                last_li.append(' ')
                                last_li.append(p_text)
                            self._nest_ordered_list(last_li, ol)
                            prev.extract()  # Remove the paragraph since we moved its content

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

    def _fix_all_concatenated_items(self):
        """Find and fix all list items with concatenated numeric content."""
        for li in self.soup.find_all('li'):
            # Check if this item has concatenated content
            text = li.get_text()
            if re.search(r'\(\d+\)[^()]+\(\d+\)', text):
                # This item has multiple numeric items concatenated
                self._fix_concatenated_numeric_items(li)

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
        # First check if the li itself has concatenated content in its text
        text = ''.join(str(c) for c in li.children if isinstance(c, str) or (hasattr(c, 'name') and c.name != 'ul'))

        # Look for patterns like (1) something (2) something
        if re.search(r'\(\d+\)[^()]+\(\d+\)', text):
            # Extract the marker from the li
            marker = li.find('span', class_=['list-marker-alpha', 'list-marker-numeric', 'list-marker-roman'])
            if not marker:
                return

            marker_text = marker.get_text()

            # Get just the content (excluding nested lists)
            content_parts = []
            for child in li.children:
                if isinstance(child, str):
                    content_parts.append(str(child))
                elif hasattr(child, 'name') and child.name != 'ul' and child != marker:
                    content_parts.append(str(child))

            full_content = ''.join(content_parts).strip()

            # Find all numeric items in the content
            # Pattern to match (1) content (2) content etc.
            # But skip inline numeric references like "twenty (20)"
            # List items should be at start or after punctuation/newline
            # Not after a word character

            # First, protect inline references like "twenty (20)" or "percent (20)"
            inline_pattern = r'(\w+\s*\(\d+\))'
            protected_content = re.sub(inline_pattern, lambda m: m.group(1).replace('(', '<<LP>>').replace(')', '<<RP>>'), full_content)

            # Now find actual list items
            pattern = r'\((\d+)\)\s*([^()]+?)(?=\(\d+\)|$)'
            matches = re.findall(pattern, protected_content, re.DOTALL)

            if len(matches) > 0:
                # Clear the li's direct content (but keep marker and any existing nested lists)
                for child in list(li.children):
                    if child != marker and (not hasattr(child, 'name') or child.name != 'ul'):
                        if hasattr(child, 'extract'):
                            child.extract()
                        else:
                            li.contents.remove(child)

                # Add the intro text before the first numeric item (if any)
                intro_match = re.match(r'^(.*?)\s*\(\d+\)', full_content)
                if intro_match and intro_match.group(1).strip():
                    li.append(' ' + intro_match.group(1).strip())

                # Create a nested numeric list
                new_ul = self.soup.new_tag('ul', **{'class': 'numeric-list'})

                for num, content in matches:
                    new_li = self.soup.new_tag('li')
                    marker_span = self.soup.new_tag('span', **{'class': 'list-marker-numeric'})
                    marker_span.string = f"({num})"
                    new_li.append(marker_span)
                    new_li.append(' ' + content.strip())
                    new_ul.append(new_li)

                li.append(new_ul)
                self.changes_made = True
                print(f"  Fixed concatenated items in {marker_text} - split into {len(matches)} items")
                return

        # Also check if this li has a nested numeric list that needs fixing
        nested_list = li.find('ul', class_='numeric-list')
        if not nested_list:
            return

        # Check the nested items for concatenation
        for nested_li in list(nested_list.find_all('li', recursive=False)):
            text_content = nested_li.get_text()

            # Check if we have multiple numeric markers (2. 3. 4.)
            # Match patterns like "2. " or "2) "
            if re.findall(r'\b[2-9][\.\)]\s', text_content):
                # Split on numeric patterns - updated to not require quotes
                # This will match "1. Corner Lot means..." or "2. \"Reversed Corner Lot\" means..."
                parts = re.split(r'(\b[1-9]\.)(?:\s+)', text_content)

                # Rebuild into numeric items
                numeric_items = []
                for i in range(len(parts)):
                    if re.match(r'\b[1-9]\.', parts[i]):
                        num = parts[i].rstrip('.')
                        # Get content until next number or end
                        if i + 1 < len(parts):
                            # Find where next item starts
                            content = parts[i + 1]
                            # Remove trailing part that belongs to next item
                            content = re.sub(r'\s*\b[2-9]\.$', '', content)
                            numeric_items.append((num, content.strip()))

                if len(numeric_items) > 1:  # We have multiple items
                    # Clear nested_li content but keep the marker
                    marker = nested_li.find('span', class_='list-marker-numeric')
                    for child in list(nested_li.children):
                        if child != marker:
                            if hasattr(child, 'extract'):
                                child.extract()
                            else:
                                child.replace_with('')

                    # Add back just the first item's content
                    nested_li.append(' ' + numeric_items[0][1])

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
        # First, add setback-list class to lists in Section 5.080
        for h3 in self.soup.find_all(['h3', 'h4']):
            if 'Section 5.080' in h3.get_text():
                # Find all lists after this section until next heading
                elem = h3.find_next_sibling()
                while elem:
                    if elem.name in ['h2', 'h3', 'h4']:
                        break
                    if elem.name == 'ul':
                        current_classes = elem.get('class', [])
                        if 'setback-list' not in current_classes:
                            current_classes.append('setback-list')
                            elem['class'] = current_classes
                            self.changes_made = True
                            print("  Added 'setback-list' CSS class to Section 5.080 list")
                    elem = elem.find_next_sibling()

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