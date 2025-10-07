#!/usr/bin/env python3
"""
Unified List Processor for City of Rivergrove Documents

This is the SINGLE source of truth for all list processing in the build pipeline.
It handles:
1. Converting paragraph-based lists to HTML lists
2. Detecting list types (alpha, numeric, roman)
3. Adding semantic CSS classes
4. Wrapping markers in styled spans
5. Processing Document Notes sections

Author: Claude
Date: 2024
"""

import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString

def detect_list_type(text, prev_type=None, prev_char=None):
    """
    Detect the type of list based on the marker pattern.
    Returns: ('alpha'|'numeric'|'roman'|None, marker_text, marker_char)

    Args:
        text: The text to check for list markers
        prev_type: The type of the previous marker ('alpha', 'roman', 'numeric')
        prev_char: The character of the previous marker (e.g., 'h' for '(h)')
    """
    # Skip inline numeric references like "(10) days" or "(20) percent"
    # These are numeric references within text, not list items
    inline_reference_pattern = re.compile(r'^\s*\(\d+\)\s+(days?|percent|months?|years?|hours?|minutes?|feet|foot|inches?)\b', re.IGNORECASE)
    if inline_reference_pattern.match(text):
        return None, None, None

    # Skip paragraph references like "(a) which was relied on"
    # These are references to other paragraphs, not new list items
    paragraph_reference_pattern = re.compile(r'^\s*\([a-z]\)\s+(which|that|as|of|from|to|for|and|or|in)\b', re.IGNORECASE)
    if paragraph_reference_pattern.match(text):
        return None, None, None

    # Pattern to match list markers - both (1) and 1. formats
    paren_pattern = re.compile(r'^\s*\(([a-z]+|[0-9]+|[ivxlcdm]+)\)\s+', re.IGNORECASE)
    period_pattern = re.compile(r'^\s*([0-9]+|[a-z])\.\s+', re.IGNORECASE)

    match = paren_pattern.match(text)
    if match:
        marker = match.group(1).lower()
        full_marker = f"({marker})"
    else:
        match = period_pattern.match(text)
        if match:
            marker = match.group(1).lower()
            full_marker = match.group(0).strip()

    if match:
        # Check type
        if marker.isdigit():
            return 'numeric', full_marker, marker
        elif marker.isalpha():
            # Ambiguous markers that could be either alpha or roman
            ambiguous = ['i', 'v', 'x', 'l', 'c', 'd', 'm']
            # Definitely roman numerals (multi-character)
            definite_roman = ['ii', 'iii', 'iv', 'vi', 'vii', 'viii', 'ix',
                              'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii',
                              'xviii', 'xix', 'xx']

            if marker in definite_roman:
                return 'roman', full_marker, marker
            elif marker in ambiguous:
                # Use context to determine type
                # If we're in an alphabetic sequence, stay alphabetic
                if prev_type == 'alpha':
                    # Check if this is sequential
                    if prev_char and len(marker) == 1 and len(prev_char) == 1:
                        # Check if it's the next letter (h -> i)
                        if ord(marker) == ord(prev_char) + 1:
                            return 'alpha', full_marker, marker
                    # Even if not perfectly sequential, stay in alpha mode
                    return 'alpha', full_marker, marker

                # Special case: 'i' after 'h' is almost certainly alphabetic
                if marker == 'i' and prev_char == 'h':
                    return 'alpha', full_marker, marker

                # Default 'i' to alpha in most cases (common in alphabetic lists)
                if marker == 'i':
                    return 'alpha', full_marker, marker

                # Other ambiguous markers default to roman if no context
                return 'roman', full_marker, marker
            else:
                # Definitely alphabetic (like 'a', 'b', 'h', 'j', etc.)
                return 'alpha', full_marker, marker

    return None, None, None

def convert_paragraph_lists(soup):
    """
    Convert paragraphs containing list patterns into proper HTML lists.
    """
    # Process all paragraphs
    paragraphs = list(soup.find_all('p'))
    
    for p in paragraphs:
        # Skip if already processed or inside a list
        if not p or not p.parent or p.find_parent(['ul', 'ol', 'li']):
            continue
            
        text = str(p)
        
        # Check if paragraph contains list patterns
        if '(a)' in text or '(1)' in text or '(i)' in text or '(b)' in text:
            # Get lines - handle both <br> and newlines
            lines = []
            if '<br/>' in text or '<br>' in text:
                # Split by br tags
                parts = re.split(r'<br/?>', text)
                for part in parts:
                    clean = BeautifulSoup(part, 'html.parser').get_text().strip()
                    if clean:
                        lines.append(clean)
            else:
                # Split by newlines first
                text_only = p.get_text()
                potential_lines = text_only.split('\n')
                lines = [line.strip() for line in potential_lines if line.strip()]

                # If we didn't get multiple lines, try splitting by list markers
                if len(lines) <= 1 and text_only:
                    # Try to split by consecutive list markers
                    # Pattern: split before (i), (ii), (a), (b), (1), (2), etc.
                    # Split at list markers, keeping the marker with the following text
                    pattern = r'(?=\([a-z]+\))|(?=\([0-9]+\))|(?=\([ivxlcdm]+\))'
                    parts = re.split(pattern, text_only)
                    lines = []
                    for part in parts:
                        part = part.strip()
                        if part and (part.startswith('(') or lines):  # Include intro text before first marker
                            lines.append(part)
            
            # Check if we have list items
            if lines and len(lines) >= 2:
                list_items = []
                list_type = None
                intro_lines = []  # Lines before the first list item
                prev_type = None
                prev_char = None

                for line in lines:
                    item_type, marker, char = detect_list_type(line, prev_type, prev_char)
                    if item_type:
                        list_items.append((line, item_type, marker))
                        if not list_type:
                            list_type = item_type
                        prev_type = item_type
                        prev_char = char
                    elif not list_items:
                        # This is text before any list items
                        intro_lines.append(line)

                # Convert to list if we have at least 2 list items
                if len(list_items) >= 2:
                    # Create elements to replace the paragraph
                    replacement_elements = []

                    # If there's introductory text, keep it as a paragraph
                    if intro_lines:
                        intro_p = soup.new_tag('p')
                        intro_p.string = ' '.join(intro_lines)
                        replacement_elements.append(intro_p)

                    # Create a new ul element for the list items
                    new_ul = soup.new_tag('ul')
                    new_ul['class'] = [f'{list_type}-list']

                    for item_text, item_type, marker in list_items:
                        li = soup.new_tag('li')
                        # Create marker span
                        marker_span = soup.new_tag('span')
                        marker_span['class'] = [f'list-marker-{item_type}']
                        marker_span.string = marker

                        # Get text after marker
                        remaining = item_text[len(marker):].strip()

                        li.append(marker_span)
                        li.append(' ' + remaining)
                        new_ul.append(li)

                    replacement_elements.append(new_ul)

                    # Replace the paragraph with the new elements
                    if replacement_elements:
                        # Insert all new elements before the paragraph
                        for elem in reversed(replacement_elements[1:]):
                            p.insert_after(elem)
                        # Replace the paragraph with the first element
                        p.replace_with(replacement_elements[0])

def process_nested_lists_in_li(soup):
    """
    Process list patterns within <li> elements to create proper nested lists.
    """
    # Process all li elements that might contain nested lists
    for li in soup.find_all('li'):
        # Skip if already has nested list
        if li.find('ul'):
            continue
            
        # Get text content
        text = li.get_text()
        
        # Check for nested list patterns
        lines = text.split('\n')
        if len(lines) > 1:
            main_text = []
            nested_items = []
            prev_type = None
            prev_char = None

            for line in lines:
                line = line.strip()
                if line:
                    item_type, marker, char = detect_list_type(line, prev_type, prev_char)
                    if item_type and not main_text:
                        # This is the main list item
                        main_text.append(line)
                    elif item_type:
                        # This is a nested item
                        nested_items.append((line, item_type, marker))
                    elif not nested_items:
                        # Part of main text
                        main_text.append(line)
            
            # If we have nested items, restructure
            if nested_items and len(nested_items) >= 2:
                # Clear and rebuild li
                li.clear()
                
                # Add main text
                if main_text:
                    li.append(' '.join(main_text) + '\n')
                
                # Determine nested list type from first item
                nested_type = nested_items[0][1]
                
                # Create nested list
                nested_ul = soup.new_tag('ul')
                nested_ul['class'] = [f'{nested_type}-list']
                
                for item_text, item_type, marker in nested_items:
                    nested_li = soup.new_tag('li')
                    
                    # Create marker span
                    marker_span = soup.new_tag('span')
                    marker_span['class'] = [f'list-marker-{item_type}']
                    marker_span.string = marker
                    
                    # Get text after marker
                    remaining = item_text[len(marker):].strip()
                    
                    nested_li.append(marker_span)
                    nested_li.append(' ' + remaining)
                    nested_ul.append(nested_li)
                
                li.append(nested_ul)

def process_existing_lists(soup):
    """
    Process existing <ul> lists to add classes and wrap markers if needed.
    """
    for ul in soup.find_all('ul'):
        # Skip if already has our classes
        if ul.get('class') and any(cls in ul.get('class') for cls in ['alpha-list', 'numeric-list', 'roman-list']):
            # But still process the markers
            for li in ul.find_all('li', recursive=False):
                process_li_markers(li, soup)
            continue
        
        # Detect list type from first item
        first_li = ul.find('li')
        if first_li:
            text = first_li.get_text()
            list_type, marker, _ = detect_list_type(text, None, None)
            
            if list_type:
                # Add class to ul
                ul['class'] = ul.get('class', []) + [f'{list_type}-list']
                
                # Process all li elements
                for li in ul.find_all('li', recursive=False):
                    process_li_markers(li, soup)

def process_li_markers(li, soup):
    """
    Process markers in a single li element.
    Handles both single items and multiple items merged into one li.
    """
    # Get all text content and check for multiple list items
    full_text = li.get_text()
    lines = full_text.split('\n')
    
    # Find all lines that start with list markers
    list_items = []
    prev_type = None
    prev_char = None
    for line in lines:
        line = line.strip()
        if line:
            item_type, marker, char = detect_list_type(line, prev_type, prev_char)
            if item_type:
                list_items.append((line, item_type, marker))
                prev_type = item_type
                prev_char = char
    
    # If we have multiple list items in one li, we need to split them
    if len(list_items) > 1:
        parent_ul = li.parent
        
        # Create new li elements for each item
        new_lis = []
        for item_text, item_type, marker in list_items:
            new_li = soup.new_tag('li')
            
            # Create marker span
            marker_span = soup.new_tag('span')
            marker_span['class'] = [f'list-marker-{item_type}']
            marker_span.string = marker
            
            # Get text after marker
            remaining = item_text[len(marker):].strip()
            
            new_li.append(marker_span)
            new_li.append(' ' + remaining)
            new_lis.append(new_li)
        
        # Insert new lis after the current one
        for new_li in reversed(new_lis[1:]):
            li.insert_after(new_li)
        
        # Replace the current li's content with the first item
        li.clear()
        for child in list(new_lis[0].children):
            li.append(child.extract() if hasattr(child, 'extract') else child)
    
    # Single item - process normally
    elif len(list_items) == 1:
        # Check if already has correct marker span
        existing_span = li.find('span', class_=re.compile('list-marker-'))
        if existing_span:
            return  # Already processed correctly
        
        item_text, item_type, marker = list_items[0]
        
        # Clear and rebuild the li
        li.clear()
        
        # Create marker span
        marker_span = soup.new_tag('span')
        marker_span['class'] = [f'list-marker-{item_type}']
        marker_span.string = marker
        
        # Get text after marker
        remaining = item_text[len(marker):].strip()
        
        li.append(marker_span)
        li.append(' ' + remaining)

def process_document_notes(soup):
    """
    Process Document Notes sections to add badges and special formatting.
    """
    # Find all h3 elements that might be document notes
    for h3 in soup.find_all('h3'):
        h3_text = h3.get_text()
        
        # Check if this is a document note header
        if any(marker in h3_text for marker in ['Stamp', 'Handwritten', 'Margin note']):
            # Extract page reference if present
            page_match = re.search(r'\{\{page:(\d+)\}\}', h3_text)
            if page_match:
                page_num = page_match.group(1)
                # Remove the page reference from the text
                h3_text = re.sub(r'\s*\{\{page:\d+\}\}', '', h3_text).strip()
                
                # Determine badge type
                badge_class = 'note-badge'
                if 'Stamp' in h3_text:
                    badge_class += ' stamp'
                elif 'Handwritten' in h3_text:
                    badge_class += ' handwritten'
                elif 'Margin note' in h3_text:
                    badge_class += ' margin-note'
                
                # Clear and rebuild h3
                h3.clear()
                h3['class'] = ['document-note-header']
                
                # Add badge
                badge = soup.new_tag('span')
                badge['class'] = [badge_class]
                badge.string = h3_text
                h3.append(badge)
                
                # Add page reference
                if page_num:
                    page_span = soup.new_tag('span')
                    page_span['class'] = ['page-reference']
                    page_span.string = f' (page {page_num})'
                    h3.append(page_span)

def convert_consecutive_paragraph_lists(soup):
    """
    Convert consecutive <p> tags that start with list markers into lists.
    This handles cases where each list item is a separate paragraph.
    """
    # Special handling for Section 1.050 Definitions
    # Find the section heading
    for h in soup.find_all(['h3']):
        h_text = h.get_text()
        if 'Section 1.050' in h_text and 'Definition' in h_text:  # Changed to match either Definitions or Definition
            # Convert ALL definition paragraphs after this heading into a single list
            definition_paragraphs = []
            current = h.find_next_sibling()

            # Skip intro paragraphs
            while current and current.name == 'p':
                text = current.get_text().strip()
                if text.startswith('(') and ')' in text[:4]:  # This is a definition
                    break
                # Skip intro paragraph
                current = current.find_next_sibling()

            # Now collect all definition paragraphs AND lists until we hit Article 2
            while current:
                if current.name == 'p':
                    text = current.get_text().strip()
                    if text.startswith('(') and ')' in text[:6]:  # Allow up to 6 chars for marker (e.g., "(w)")
                        # Make sure this is a letter definition (a-z), not from Article 2
                        paren_pos = text.index(')')
                        marker = text[1:paren_pos] if paren_pos > 0 else ''

                        # Check if it's an alphabetic definition
                        if marker.isalpha() and len(marker) <= 2:  # Single or double letter (a-z, aa, etc)
                            definition_paragraphs.append(current)
                            current = current.find_next_sibling()
                        else:
                            # Hit a non-alphabetic marker, stop
                            break
                    else:
                        # Not a definition paragraph, skip it
                        current = current.find_next_sibling()
                elif current.name in ['h2', 'h3', 'hr']:
                    # Hit next section
                    break
                elif current.name == 'ul':
                    # Found a list - check if it's a definition list (starts with alphabetic marker)
                    text = current.get_text().strip()
                    if text.startswith('(') and ')' in text[:6]:
                        paren_pos = text.index(')')
                        marker = text[1:paren_pos] if paren_pos > 0 else ''
                        if marker.isalpha() and len(marker) <= 2:
                            # This is a definition that's already been converted to a list
                            # (likely has nested items, like (i) Lot or (w) Street)
                            definition_paragraphs.append(current)
                            current = current.find_next_sibling()
                        else:
                            current = current.find_next_sibling()
                    else:
                        current = current.find_next_sibling()
                else:
                    current = current.find_next_sibling()

            # Convert all collected definition paragraphs/lists to a single list
            if len(definition_paragraphs) >= 2:
                # Create single ul for all definitions
                new_ul = soup.new_tag('ul')
                new_ul['class'] = ['alpha-list']

                for element in definition_paragraphs:
                    if element.name == 'p':
                        # Convert paragraph to list item
                        text = element.get_text().strip()
                        item_type, marker, _ = detect_list_type(text, 'alpha', None)

                        if item_type:
                            li = soup.new_tag('li')

                            # Create marker span
                            marker_span = soup.new_tag('span')
                            marker_span['class'] = [f'list-marker-{item_type}']
                            marker_span.string = marker

                            # Get text after marker
                            remaining = text[len(marker):].strip()

                            li.append(marker_span)
                            li.append(' ' + remaining)
                            new_ul.append(li)

                    elif element.name == 'ul':
                        # This is already a list (like (i) or (w) with nested items)
                        # Extract the list items and add them to our new list
                        for existing_li in element.find_all('li', recursive=False):
                            # Clone the existing list item
                            new_li = soup.new_tag('li')
                            # Copy all children of the existing li
                            for child in list(existing_li.children):
                                if isinstance(child, str):
                                    new_li.append(child)
                                else:
                                    new_li.append(child.extract())
                            new_ul.append(new_li)

                # Insert the list after the first element
                definition_paragraphs[0].insert_before(new_ul)

                # Remove the original paragraphs/lists
                for element in definition_paragraphs:
                    element.decompose()

                # Don't process these paragraphs again
                paragraphs = soup.find_all('p')

    # Find all paragraphs (refresh after special handling)
    paragraphs = soup.find_all('p')
    
    i = 0
    while i < len(paragraphs):
        p = paragraphs[i]

        # Skip if already processed
        if not p or not p.parent:
            i += 1
            continue

        # Check if this paragraph starts with a list marker
        text = p.get_text().strip()

        # Debug Section 4.120
        if "The Commission shall schedule a public hearing pursuant to Article 8" in text:
            print(f"  DEBUG: Found Section 4.120 (a) at index {i}")
            # Look at the next few paragraphs
            for k in range(i, min(i+5, len(paragraphs))):
                if k < len(paragraphs):
                    pk_text = paragraphs[k].get_text().strip()[:80]
                    pk_type, pk_marker, _ = detect_list_type(paragraphs[k].get_text().strip(), None, None)
                    print(f"    Paragraph {k}: type={pk_type}, marker={pk_marker}, text={pk_text}...")

        item_type, marker, char = detect_list_type(text, None, None)

        if item_type:
            # Found a list item - collect consecutive list items
            list_items = []
            list_type = item_type
            j = i
            prev_type = list_type
            prev_char = char

            # Look ahead to find all items of the same type
            # Skip non-list paragraphs between list items
            while j < len(paragraphs):
                current_p = paragraphs[j]

                # Check if we've hit a section boundary (heading between paragraphs)
                # Look for any heading elements between the previous and current paragraph
                if j > i:
                    prev_p = paragraphs[j-1]
                    next_elem = prev_p.find_next_sibling()
                    while next_elem and next_elem != current_p:
                        if next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr']:
                            # Hit a section boundary - stop collecting
                            break
                        next_elem = next_elem.find_next_sibling()
                    else:
                        # Continue checking this paragraph
                        pass
                    if next_elem and next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr']:
                        break

                p_text = current_p.get_text().strip()
                p_type, p_marker, p_char = detect_list_type(p_text, prev_type, prev_char)

                if p_type and p_type == list_type:
                    # Same type of list item
                    list_items.append((p_text, p_type, p_marker, current_p))
                    prev_type = p_type
                    prev_char = p_char
                    j += 1
                elif not p_type:
                    # Non-list paragraph - look ahead to see if more list items follow
                    lookahead = j + 1
                    found_more = False
                    while lookahead < min(j + 5, len(paragraphs)):  # Look up to 5 paragraphs ahead
                        ahead_text = paragraphs[lookahead].get_text().strip()
                        ahead_type, _, _ = detect_list_type(ahead_text, None, None)
                        if ahead_type == list_type:
                            found_more = True
                            break
                        elif ahead_type and ahead_type != list_type:
                            # Different type of list starts
                            break
                        lookahead += 1

                    if found_more:
                        # Skip the non-list paragraphs
                        j += 1
                        continue
                    else:
                        # No more items of this type
                        break
                else:
                    # Different type of list item
                    break
            
            # If we have at least 2 list items, convert to a list
            if len(list_items) >= 2:
                # Debug Section 4.120
                if any("City Council shall make a finding" in str(item[0]) for item in list_items):
                    print(f"  DEBUG Section 4.120: Found {len(list_items)} list items")
                    for idx, (text, type, marker, p) in enumerate(list_items):
                        print(f"    Item {idx}: {marker} - {text[:60]}...")

                # Create the list
                new_ul = soup.new_tag('ul')
                new_ul['class'] = [f'{list_type}-list']
                
                for item_text, item_type, item_marker, item_p in list_items:
                    li = soup.new_tag('li')
                    
                    # Create marker span
                    marker_span = soup.new_tag('span')
                    marker_span['class'] = [f'list-marker-{item_type}']
                    marker_span.string = item_marker
                    
                    # Get text after marker
                    remaining = item_text[len(item_marker):].strip()
                    
                    li.append(marker_span)
                    li.append(' ' + remaining)
                    new_ul.append(li)
                
                # Insert the list before the first paragraph
                list_items[0][3].insert_before(new_ul)
                
                # Remove the original paragraphs
                for _, _, _, p in list_items:
                    p.decompose()
                
                # Update paragraphs list and continue
                paragraphs = soup.find_all('p')
                continue
        
        i += 1

def process_lists_in_tables(soup):
    """
    Process list notation within table cells.
    Wraps markers like (1), (a), (i) in styled spans.
    """
    for td in soup.find_all('td'):
        if td.string:
            continue  # Skip if it's just a simple string
        
        # Process the contents
        new_contents = []
        for element in td.contents:
            if isinstance(element, NavigableString):
                text = str(element)
                # Check for list patterns and wrap them
                # Pattern for (a), (1), (i) etc.
                pattern = r'(\([a-z]+\)|\([0-9]+\)|\([ivxlcdm]+\))'
                
                def replace_marker(match):
                    marker = match.group(1)
                    marker_content = marker[1:-1]  # Remove parentheses
                    
                    # Determine type
                    if marker_content.isdigit():
                        marker_type = 'numeric'
                    elif marker_content.isalpha() and marker_content.lower() not in ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x']:
                        marker_type = 'alpha'
                    elif marker_content.lower() in ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii']:
                        marker_type = 'roman'
                    else:
                        return marker
                    
                    # Create span
                    span = soup.new_tag('span')
                    span['class'] = [f'list-marker-{marker_type}']
                    span.string = marker
                    return str(span)
                
                # Replace markers with styled spans
                processed = re.sub(pattern, replace_marker, text, flags=re.IGNORECASE)
                
                # Parse the processed string back to BeautifulSoup elements
                if processed != text:
                    fragment = BeautifulSoup(processed, 'html.parser')
                    new_contents.extend(fragment.contents)
                else:
                    new_contents.append(element)
            else:
                new_contents.append(element)
        
        # Replace td contents
        td.clear()
        for content in new_contents:
            if isinstance(content, NavigableString):
                td.append(content)
            else:
                td.append(content.extract() if hasattr(content, 'extract') else content)

def merge_separated_lists(soup):
    """
    Merge consecutive <ul> lists that should be a single continuous list.
    This handles cases where mdBook splits a list due to indented content.
    """
    # Find all ul elements
    uls = soup.find_all('ul')

    i = 0
    while i < len(uls) - 1:
        current_ul = uls[i]
        next_ul = uls[i + 1]

        # Check if these are adjacent siblings or close enough to merge
        # Get all siblings between current and next
        current_parent = current_ul.parent
        next_parent = next_ul.parent

        # Only merge if they have the same parent
        if current_parent == next_parent:
            # Check what's between them
            between = []
            sibling = current_ul.next_sibling
            while sibling and sibling != next_ul:
                # Skip whitespace-only text nodes
                if isinstance(sibling, NavigableString):
                    if sibling.strip():
                        between.append(sibling)
                else:
                    between.append(sibling)
                sibling = sibling.next_sibling

            # If nothing substantial between them, consider merging
            if not between:
                # Get the items to check continuity
                current_items = current_ul.find_all('li', recursive=False)
                next_items = next_ul.find_all('li', recursive=False)

                if current_items and next_items:
                    # Get the last item of current list
                    last_text = current_items[-1].get_text()
                    last_type, last_marker, last_char = detect_list_type(last_text, None, None)

                    # Get the first item of next list
                    # Check if it's item (i) with nested numeric items
                    first_li = next_items[0]
                    first_text = first_li.get_text()

                    # Extract just the first line to detect the main marker
                    first_line = first_text.split('\n')[0] if '\n' in first_text else first_text
                    first_type, first_marker, first_char = detect_list_type(first_line, last_type, last_char)

                    # Check if we should merge - look for missing (i) after (h)
                    # The first list might have items beyond (h), so we need to find where (i) should go
                    if first_type == 'alpha' and first_char == 'i':
                        # Check if the first list has (h) somewhere
                        insert_position = None
                        for j, item in enumerate(current_items):
                            item_text = item.get_text()
                            item_type, _, item_char = detect_list_type(item_text, None, None)
                            if item_type == 'alpha' and item_char == 'h':
                                # Found (h) - (i) should go after it
                                insert_position = j + 1
                                break

                        if insert_position is not None:
                            # We found where to insert item (i)
                            # First, we need to restructure item (i) if it has nested items
                            if first_li.find('ul'):
                                # Item (i) already has proper nested structure
                                pass
                            else:
                                # Check if item (i) has inline numeric items that need nesting
                                lines = first_text.split('\n')
                                if len(lines) > 1:
                                    # Rebuild item (i) with proper nesting
                                    first_li.clear()

                                    # Add the main (i) marker and text
                                    marker_span = soup.new_tag('span')
                                    marker_span['class'] = ['list-marker-alpha']
                                    marker_span.string = first_marker
                                    first_li.append(marker_span)

                                    # Get main text (after marker, before nested items)
                                    main_text = first_line[len(first_marker):].strip()
                                    first_li.append(' ' + main_text + '\n')

                                    # Create nested list for numeric items
                                    nested_ul = soup.new_tag('ul')
                                    nested_ul['class'] = ['numeric-list']

                                    for line in lines[1:]:
                                        line = line.strip()
                                        if line:
                                            nested_type, nested_marker, _ = detect_list_type(line, None, None)
                                            if nested_type:
                                                nested_li = soup.new_tag('li')
                                                nested_span = soup.new_tag('span')
                                                nested_span['class'] = [f'list-marker-{nested_type}']
                                                nested_span.string = nested_marker
                                                nested_li.append(nested_span)
                                                nested_li.append(' ' + line[len(nested_marker):].strip())
                                                nested_ul.append(nested_li)

                                    if nested_ul.find_all('li'):
                                        first_li.append(nested_ul)

                            # Extract items from the second list
                            items_to_insert = []
                            for li in next_items:
                                items_to_insert.append(li.extract())

                            # Insert items at the correct position
                            # First, get all current items as a list we can manipulate
                            all_items = list(current_ul.find_all('li', recursive=False))

                            # Insert the new items at the correct position
                            for idx, new_item in enumerate(items_to_insert):
                                if insert_position + idx < len(all_items):
                                    # Insert before the item at this position
                                    all_items[insert_position + idx].insert_before(new_item)
                                else:
                                    # Append at the end
                                    current_ul.append(new_item)

                            # Update the class if needed to ensure it stays as alpha-list
                            if 'alpha-list' not in current_ul.get('class', []):
                                current_ul['class'] = ['alpha-list']

                            # Remove the now-empty next_ul
                            next_ul.decompose()

                            # Update the uls list
                            uls = soup.find_all('ul')
                            continue

        i += 1

def fix_misplaced_nested_items(soup):
    """
    Fix specific known cases where numeric items are misplaced as siblings instead of nested.
    Focus on the Section 1.050 definitions where Lot and Street definitions have displaced sub-items.
    """
    print("  DEBUG: fix_misplaced_nested_items called")
    # Find all alpha-list ul elements
    for ul in soup.find_all('ul', class_='alpha-list'):
        print(f"    DEBUG: Found alpha-list with {len(ul.find_all('li', recursive=False))} items")
        items = ul.find_all('li', recursive=False)

        # Look for specific known problematic patterns
        for i, current_item in enumerate(items):
            current_marker = current_item.find('span', class_='list-marker-alpha')
            if not current_marker:
                continue

            current_text = current_item.get_text()
            marker_text = current_marker.get_text()

            # Debug all (i) items to see what we're getting
            if marker_text == '(i)':
                has_quoted_lot = '"Lot"' in current_text
                print(f"  DEBUG: Found item (i): {current_text[:100]}...")
                print(f"    Contains 'Lot': {'Lot' in current_text}")
                print(f"    Contains quoted Lot: {has_quoted_lot}")
                print(f"    Ends with ':': {current_text.strip().endswith(':')}")

            # Specific fix for (i) "Lot" definition
            # Note: HTML may have converted quotes to entities, so check for both
            if marker_text == '(i)' and ('Lot' in current_text) and current_text.strip().endswith(':'):
                print(f"  DEBUG: Processing item (i) with Lot definition ending with colon")
                # Look for the three lot type definitions that should be nested here
                lot_items_to_move = []

                # NEW: Look for sibling items with numeric markers that are lot definitions
                for j, other_item in enumerate(items):
                    if j == i:  # Skip the current item
                        continue

                    other_marker = other_item.find('span', class_='list-marker-numeric')
                    if other_marker:
                        # This is a numeric item that might belong under (i)
                        other_text = other_item.get_text()
                        # Check if it's one of the lot type definitions
                        if any(lot_type in other_text for lot_type in [
                            'Corner Lot', 'Reversed Corner Lot', 'Through Lot'
                        ]):
                            print(f"    Found misplaced lot definition: {other_marker.get_text()}")
                            # Extract the entire item to move it
                            lot_items_to_move.append(other_item.extract())
                    else:
                        # Also check if this item has a nested numeric list with lot definitions
                        nested_list = other_item.find('ul', class_='numeric-list')
                        if nested_list:
                            nested_items = nested_list.find_all('li', recursive=False)
                            for nested_item in nested_items:
                                nested_text = nested_item.get_text()
                                # Check for lot type definitions
                                if any(lot_type in nested_text for lot_type in [
                                    'Corner Lot', 'Reversed Corner Lot', 'Through Lot'
                                ]):
                                    lot_items_to_move.append(nested_item.extract())

                            # If we emptied the nested list, remove it
                            if not nested_list.find_all('li'):
                                nested_list.extract()

                # If we found lot definitions, create nested structure under (i)
                if lot_items_to_move:
                    # Create nested ul for the lot definitions
                    nested_ul = soup.new_tag('ul')
                    nested_ul['class'] = ['numeric-list']

                    # Sort by number
                    def get_lot_number(item):
                        marker = item.find('span', class_='list-marker-numeric')
                        if marker:
                            marker_text = marker.get_text()
                            if '(1)' in marker_text:
                                return 1
                            elif '(2)' in marker_text:
                                return 2
                            elif '(3)' in marker_text:
                                return 3
                        return 999

                    lot_items_to_move.sort(key=get_lot_number)

                    # Add items to nested list
                    for item in lot_items_to_move:
                        nested_ul.append(item)

                    current_item.append(nested_ul)
                    print(f"  Fixed misplaced lot definitions under item (i) - moved {len(lot_items_to_move)} items")

            # Specific fix for (w) "Street" definition
            elif marker_text == '(w)' and ('Street' in current_text) and current_text.strip().endswith(':'):
                print(f"  DEBUG: Processing item (w) with Street definition ending with colon")
                # Look for the four street type definitions that should be nested here
                street_items_to_move = []

                # Look for sibling items with numeric markers that are street definitions
                for j, other_item in enumerate(items):
                    if j == i:  # Skip the current item
                        continue

                    other_marker = other_item.find('span', class_='list-marker-numeric')
                    if other_marker:
                        # This is a numeric item that might belong under (w)
                        other_text = other_item.get_text()
                        # Check if it's one of the street type definitions
                        if any(street_type in other_text for street_type in [
                            'Alley', 'Arterial', 'Collector', 'Cul-de-sac'
                        ]):
                            print(f"    Found misplaced street definition: {other_marker.get_text()}")
                            # Extract the entire item to move it
                            street_items_to_move.append(other_item.extract())

                # If we found street definitions, create nested structure under (w)
                if street_items_to_move:
                    # Create nested ul for the street definitions
                    nested_ul = soup.new_tag('ul')
                    nested_ul['class'] = ['numeric-list']

                    # Add items to nested list in order
                    for item in street_items_to_move:
                        nested_ul.append(item)

                    current_item.append(nested_ul)
                    print(f"  Fixed misplaced street definitions under item (w) - moved {len(street_items_to_move)} items")


def fix_concatenated_numeric_items(soup):
    """Fix list items that have multiple numeric items concatenated together."""
    changes_made = False

    for li in soup.find_all('li'):
        # Get just the content (excluding nested lists)
        content_parts = []
        marker = li.find('span', class_=['list-marker-alpha', 'list-marker-numeric', 'list-marker-roman'])

        for child in li.children:
            if isinstance(child, str):
                content_parts.append(str(child))
            elif hasattr(child, 'name') and child.name != 'ul' and child != marker:
                content_parts.append(str(child))

        full_content = ''.join(content_parts).strip()

        # Look for patterns like (1) something (2) something
        if re.search(r'\(\d+\)[^()]+\(\d+\)', full_content):
            if not marker:
                continue

            marker_text = marker.get_text()

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
                new_ul = soup.new_tag('ul')
                new_ul['class'] = ['numeric-list']

                for num, content in matches:
                    new_li = soup.new_tag('li')
                    marker_span = soup.new_tag('span')
                    marker_span['class'] = ['list-marker-numeric']
                    marker_span.string = f"({num})"
                    new_li.append(marker_span)
                    new_li.append(' ' + content.strip())
                    new_ul.append(new_li)

                li.append(new_ul)
                changes_made = True
                print(f"  Fixed concatenated items in {marker_text} - split into {len(matches)} items")

        # Also check nested numeric lists for concatenation
        nested_list = li.find('ul', class_='numeric-list')
        if nested_list:
            for nested_li in list(nested_list.find_all('li', recursive=False)):
                text_content = nested_li.get_text()

                # Check if we have multiple numeric markers (2. 3. 4.)
                if re.findall(r'\b[2-9][\.\)]\s', text_content):
                    # Split on numeric patterns
                    parts = re.split(r'(\b[1-9]\.)(?:\s+)', text_content)

                    # Rebuild into numeric items
                    numeric_items = []
                    for i in range(len(parts)):
                        if re.match(r'\b[1-9]\.', parts[i]):
                            num = parts[i].rstrip('.')
                            if i + 1 < len(parts):
                                content = parts[i + 1]
                                content = re.sub(r'\s*\b[2-9]\.$', '', content)
                                numeric_items.append((num, content.strip()))

                    if len(numeric_items) > 1:
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
                            new_li = soup.new_tag('li')
                            marker_span = soup.new_tag('span')
                            marker_span['class'] = ['list-marker-numeric']
                            marker_span.string = f"({num})"
                            new_li.append(marker_span)
                            new_li.append(' ' + content)
                            nested_li.insert_after(new_li)
                            nested_li = new_li

                        changes_made = True
                        print(f"  Split concatenated numeric items in nested list")

def fix_orphaned_paragraphs(soup):
    """Fix paragraphs that should be nested inside list items."""
    changes_made = False

    for ul in soup.find_all('ul', class_='alpha-list'):
        items = ul.find_all('li', recursive=False)

        # Handle single-item lists
        if len(items) == 1:
            li = items[0]
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
                        nest_ordered_list_in_li(li, elem, soup)

                changes_made = True
                marker = li.find('span', class_='list-marker-alpha')
                if marker:
                    print(f"  Fixed orphaned content after {marker.get_text()}")

        # Handle multi-item lists where last item should have content nested
        elif len(items) > 1:
            last_li = items[-1]
            text = last_li.get_text().strip()

            # Check if the last item indicates it should have nested content
            if (text.endswith(':') or
                'following' in text.lower() or
                'criteria' in text.lower() or
                'shall be given' in text.lower() or
                'consideration' in text.lower()):

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

                # Convert paragraphs to nested list
                if content_to_nest:
                    new_ul = soup.new_tag('ul')
                    new_ul['class'] = ['numeric-list']

                    for p in content_to_nest:
                        text = p.get_text().strip()
                        match = re.match(r'^\((\d+)\)\s*(.*)$', text, re.DOTALL)
                        if match:
                            num = match.group(1)
                            content = match.group(2)

                            new_li = soup.new_tag('li')
                            marker_span = soup.new_tag('span')
                            marker_span['class'] = ['list-marker-numeric']
                            marker_span.string = f"({num})"
                            new_li.append(marker_span)
                            new_li.append(' ' + content)
                            new_ul.append(new_li)

                        p.extract()

                    last_li.append(new_ul)
                    changes_made = True
                    marker = last_li.find('span', class_='list-marker-alpha')
                    if marker:
                        print(f"  Fixed {len(content_to_nest)} orphaned numeric paragraphs after {marker.get_text()}")

def nest_ordered_list_in_li(li, ol, soup):
    """Helper function to convert an ordered list to nested format in a list item."""
    # Create a new unordered list for consistency
    new_ul = soup.new_tag('ul')
    new_ul['class'] = ['numeric-list']

    # Convert ol items to ul items with numeric markers
    for i, ol_li in enumerate(ol.find_all('li', recursive=False), 1):
        new_li = soup.new_tag('li')
        marker_span = soup.new_tag('span')
        marker_span['class'] = ['list-marker-numeric']
        marker_span.string = f"({i})"
        new_li.append(marker_span)
        new_li.append(' ' + ol_li.get_text())
        new_ul.append(new_li)

    li.append(new_ul)
    ol.extract()

def fix_orphaned_ordered_lists(soup):
    """Fix ordered lists that should be nested under alpha list items."""
    changes_made = False

    for ol in soup.find_all('ol'):
        parent = ol.parent
        if parent.name in ['body', 'article', 'section', 'div', 'main']:
            prev = ol.find_previous_sibling()
            if prev and prev.name == 'ul' and 'alpha-list' in prev.get('class', []):
                # Find the last item in the alpha list
                last_li = prev.find_all('li', recursive=False)[-1] if prev.find_all('li', recursive=False) else None
                if last_li:
                    # Convert ol to nested format
                    nest_ordered_list_in_li(last_li, ol, soup)
                    changes_made = True
                    print(f"  Fixed orphaned ordered list with {len(ol.find_all('li'))} items")

def fix_section_5110_list_classification(soup):
    """Fix Section 5.110 where all items (a) through (e) should be in a single alpha list."""
    # Find the Section 5.110 heading
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        if 'Section 5.110' in heading.get_text() and 'Houses Moved Into City' in heading.get_text():
            print(f"\nFixing Section 5.110 list structure...")

            # Collect all the list items that should be together
            list_items = []
            current = heading.find_next_sibling()

            while current and current.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if current.name == 'p':
                    text = current.get_text().strip()
                    # Check if it's a list item (a), (b), or (e)
                    if text.startswith('(a)') or text.startswith('(b)') or text.startswith('(e)'):
                        list_items.append(('p', current, text))
                elif current.name == 'ul':
                    # This is the existing list with (c) and (d)
                    for li in current.find_all('li', recursive=False):
                        li_text = li.get_text().strip()
                        list_items.append(('li', li, li_text))

                # Stop if we've collected all 5 items
                if len(list_items) >= 5:
                    break

                current = current.find_next_sibling()

            # If we found all the items, restructure them
            if len(list_items) >= 4:  # At least (a), (b), (c), (d)
                print(f"  Found {len(list_items)} items to combine into single list")

                # Create a new alpha-list
                new_ul = soup.new_tag('ul')
                new_ul['class'] = ['alpha-list']

                # Process each item
                for item_type, element, text in list_items:
                    # Extract marker and content
                    import re
                    match = re.match(r'^\(([a-e])\)\s*(.*)', text, re.DOTALL)
                    if match:
                        marker = f"({match.group(1)})"
                        content = match.group(2)

                        # Create new li
                        new_li = soup.new_tag('li')

                        # Create marker span
                        marker_span = soup.new_tag('span')
                        marker_span['class'] = ['list-marker-alpha']
                        marker_span.string = marker

                        new_li.append(marker_span)
                        new_li.append(' ' + content)
                        new_ul.append(new_li)

                # Insert the new list after the heading
                heading.insert_after(new_ul)

                # Remove the old elements
                for item_type, element, _ in list_items:
                    if item_type == 'p':
                        element.decompose()
                    elif item_type == 'li':
                        # Remove the parent ul if this is the last item
                        parent = element.parent
                        element.decompose()
                        if parent and not parent.find_all('li'):
                            parent.decompose()

                print(f"  Fixed: combined all items into single alpha-list")
                return

def fix_section_5100_tree_cutting(soup):
    """
    Special fix for Section 5.100 Tree Cutting.
    This section has items (a) through (f) with headings and content that need special formatting.
    """
    # Find Section 5.100
    section = None
    for h3 in soup.find_all('h3'):
        if 'Section 5.100' in h3.get_text() and 'Tree Cutting' in h3.get_text():
            section = h3
            break

    if not section:
        return False

    # Collect all the orphaned paragraphs and lists that should be part of the section
    # The structure should be: (a) DEFINITIONS with content, (b) APPLICATION with content, etc.

    # Create a new alpha list for the entire section
    main_list = soup.new_tag('ul')
    main_list['class'] = ['alpha-list']

    # Define the expected structure
    items = [
        ('(a)', 'DEFINITIONS:', 'definitions'),
        ('(b)', 'APPLICATION FOR PERMIT', 'application'),
        ('(c)', 'EMERGENCIES', 'emergencies'),
        ('(d)', 'CRITERIA FOR ISSUANCE OF PERMITS', 'criteria'),
        ('(e)', 'APPEAL', 'appeal'),
        ('(f)', 'PENALTIES', 'penalties')
    ]

    current = section.find_next_sibling()
    processed_elements = []

    # Collect all elements until the next section
    while current and current.name not in ['h2', 'h3']:
        processed_elements.append(current)
        next_elem = current.find_next_sibling()
        current = next_elem

    # Now process the collected elements to build the proper structure
    for marker, heading, item_type in items:
        li = soup.new_tag('li')

        # Add marker
        marker_span = soup.new_tag('span')
        marker_span['class'] = ['list-marker-alpha']
        marker_span.string = marker
        li.append(marker_span)
        li.append(' ')

        # Add heading
        strong = soup.new_tag('strong')
        strong.string = heading
        li.append(strong)

        # Add content based on item type
        if item_type == 'definitions':
            # Find the ordered list with definitions
            for elem in processed_elements:
                if elem.name == 'ol' and ('Tree' in elem.get_text() or 'Cutting' in elem.get_text()):
                    # Clone and add the definitions list
                    definitions_list = elem.__copy__()
                    li.append(definitions_list)
                    break

        elif item_type in ['application', 'emergencies', 'appeal', 'penalties']:
            # Find paragraphs with the relevant content
            content_found = False
            for elem in processed_elements:
                if elem.name == 'p':
                    text = elem.get_text()

                    if item_type == 'application' and 'person desiring to cut' in text:
                        # Add application content paragraphs
                        p1 = soup.new_tag('p')
                        p1.string = text
                        li.append(p1)

                        # Get the next paragraph too
                        next_p_idx = processed_elements.index(elem) + 1
                        if next_p_idx < len(processed_elements):
                            next_p = processed_elements[next_p_idx]
                            if next_p.name == 'p' and 'application shall contain' in next_p.get_text():
                                p2 = soup.new_tag('p')
                                p2.string = next_p.get_text()
                                li.append(p2)
                        content_found = True
                        break

                    elif item_type == 'emergencies' and 'emergency conditions' in text:
                        p = soup.new_tag('p')
                        p.string = text
                        li.append(p)
                        content_found = True
                        break

                    elif item_type == 'appeal' and 'decision made by the Planning Commission' in text:
                        p = soup.new_tag('p')
                        p.string = text
                        li.append(p)
                        content_found = True
                        break

                    elif item_type == 'penalties' and 'Cutting a tree in violation' in text:
                        # Add all penalty-related paragraphs
                        p1 = soup.new_tag('p')
                        p1.string = text
                        li.append(p1)

                        # Get subsequent penalty paragraphs
                        idx = processed_elements.index(elem)
                        for i in range(idx + 1, min(idx + 3, len(processed_elements))):
                            next_elem = processed_elements[i]
                            if next_elem.name == 'p':
                                next_text = next_elem.get_text()
                                if 'City retains' in next_text or 'Nothing in the Tree' in next_text:
                                    p = soup.new_tag('p')
                                    p.string = next_text
                                    li.append(p)
                        content_found = True
                        break

        elif item_type == 'criteria':
            # Find criteria content and the numbered list
            for elem in processed_elements:
                if elem.name == 'p' and 'permit may be issued as requested' in elem.get_text():
                    p = soup.new_tag('p')
                    p.string = elem.get_text()
                    li.append(p)

                    # Find the numbered criteria list
                    idx = processed_elements.index(elem)
                    for i in range(idx + 1, len(processed_elements)):
                        next_elem = processed_elements[i]
                        if next_elem.name == 'ol':
                            criteria_list = next_elem.__copy__()
                            li.append(criteria_list)
                            break
                    break

        main_list.append(li)

    # Remove all the old elements
    for elem in processed_elements:
        if elem.parent:
            elem.extract()

    # Insert the new structured list after the section heading
    section.insert_after(main_list)

    print(f"  Fixed Section 5.100 Tree Cutting structure")
    return True

def fix_section_5080_setback_formatting(soup):
    """
    Special fix for Section 5.080 setback specifications.
    Convert inline setback text to properly formatted nested structure.
    """
    # Find Section 5.080
    section = None
    for h3 in soup.find_all('h3'):
        if 'Section 5.080' in h3.get_text() and 'Building Setbacks' in h3.get_text():
            section = h3
            break

    if not section:
        return False

    # Look for the alpha list after Section 5.080
    current = section.find_next_sibling()
    if current and current.name == 'ul' and 'alpha-list' in current.get('class', []):
        for li in current.find_all('li', recursive=False):
            marker = li.find('span', class_='list-marker-alpha')
            if marker and marker.get_text() in ['(a)', '(c)']:
                # These items have setback specifications
                # Get the text content - preserve newlines!
                li_clone = li.__copy__()
                for child in li_clone.find_all(['span', 'ul']):
                    child.extract()
                # Get the raw HTML string to preserve line breaks
                text = ''.join(str(content) for content in li_clone.contents)

                # Look for setback specifications
                if 'Front Setback' in text and 'Side Setback' in text:
                    import re

                    # Now we should have actual newlines in the text
                    lines = text.split('\n')
                    main_text = []
                    setback_specs = []

                    for line in lines:
                        line = line.strip()
                        if line:
                            # Check if this line contains a setback specification
                            if re.match(r'^(Front|Side|Rear) Setback', line):
                                setback_specs.append(line)
                            elif not setback_specs:
                                # This is part of the main text (before setbacks)
                                main_text.append(line)
                            # Ignore empty lines after setbacks start

                    if setback_specs:
                        # Clear the li content
                        li.clear()

                        # Re-add the marker
                        li.append(marker)

                        # Add the main text
                        li.append(' ' + ' '.join(main_text))

                        # Create a div for setback specifications
                        setback_div = soup.new_tag('div')
                        setback_div['class'] = ['setback-specifications']

                        # Create separate p elements for each specification line
                        for spec in setback_specs:
                            spec_p = soup.new_tag('p')
                            spec_p['class'] = ['setback-spec']
                            spec_p.string = spec
                            setback_div.append(spec_p)

                        li.append(setback_div)

        print(f"  Fixed Section 5.080 setback formatting")
        return True

    return False

def fix_section_4120_item_d(soup):
    """
    Special fix for Section 4.120 where item (d) gets separated from (a), (b), (c).
    This happens because of how the paragraphs are arranged in the source.
    """
    # Find lists that end with item (c) about "City Council shall make a finding"
    for ul in soup.find_all('ul', class_='alpha-list'):
        list_items = ul.find_all('li', recursive=False)
        if list_items:
            last_li = list_items[-1]
            last_text = last_li.get_text()

            # Check if this is Section 4.120(c)
            if "City Council shall make a finding for each of the criteria" in last_text:
                # Look for the orphaned (d) paragraph after this list
                next_elem = ul.find_next_sibling()

                if next_elem and next_elem.name == 'p':
                    next_text = next_elem.get_text().strip()

                    # Check if it's item (d)
                    if next_text.startswith('(d)'):
                        # Convert this paragraph to a list item and add to the list
                        li = soup.new_tag('li')

                        # Create marker span
                        marker_span = soup.new_tag('span')
                        marker_span['class'] = ['list-marker-alpha']
                        marker_span.string = '(d)'

                        # Get content after (d)
                        content = next_text[3:].strip()

                        li.append(marker_span)
                        li.append(' ' + content)
                        ul.append(li)

                        # Remove the original paragraph
                        next_elem.extract()

                        print(f"  Fixed Section 4.120 - added item (d) to list")
                        return True

    return False

def fix_section_2080_single_item(soup):
    """
    Special fix for Section 2.080 which has a single-item list.
    This is unusual but matches the source document.
    """
    # Find Section 2.080
    for h3 in soup.find_all('h3'):
        if 'Section 2.080' in h3.get_text() and 'Termination' in h3.get_text():
            # Look for the paragraph after the heading
            current = h3.find_next_sibling()

            # Skip the intro paragraph
            if current and current.name == 'p' and 'automatically terminate' in current.get_text():
                current = current.find_next_sibling()

                # Check if the next element is the (a) paragraph
                if current and current.name == 'p':
                    text = current.get_text().strip()
                    if text.startswith('(a)'):
                        # Convert this single paragraph to a list
                        ul = soup.new_tag('ul')
                        ul['class'] = ['alpha-list']

                        li = soup.new_tag('li')

                        # Create marker span
                        marker_span = soup.new_tag('span')
                        marker_span['class'] = ['list-marker-alpha']
                        marker_span.string = '(a)'

                        # Get content after (a)
                        content = text[3:].strip()

                        li.append(marker_span)
                        li.append(' ' + content)
                        ul.append(li)

                        # Replace the paragraph with the list
                        current.replace_with(ul)

                        print(f"  Fixed Section 2.080 single-item list")
                        return True

    return False

def fix_orphaned_code_blocks(soup):
    """Fix code blocks that should be nested lists under alpha list items."""
    changes_made = False

    # Look for pre/code blocks that follow alpha lists
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        if not code:
            continue

        # Check if this looks like list content
        text = code.get_text().strip()
        lines = text.split('\n')

        # Check if all non-empty lines start with list markers like (1), (2), etc.
        is_list_content = True
        list_items = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Check for numeric list markers (1), (2), etc.
            if line.startswith('(') and ')' in line[:4]:
                try:
                    # Extract the marker
                    close_paren = line.index(')')
                    marker_text = line[1:close_paren]
                    # Check if it's numeric
                    if marker_text.isdigit():
                        list_items.append(line)
                    else:
                        is_list_content = False
                        break
                except:
                    is_list_content = False
                    break
            else:
                # Not a list marker line
                is_list_content = False
                break

        if is_list_content and list_items:
            # Check if this code block follows an alpha list
            prev = pre.find_previous_sibling()
            if prev and prev.name == 'ul' and 'alpha-list' in prev.get('class', []):
                # Look for the appropriate list item to attach to
                list_items_in_ul = prev.find_all('li', recursive=False)
                target_li = None

                # Check each item to find the one that should have the nested content
                for li in list_items_in_ul:
                    li_text = li.get_text()
                    # Look for phrases that suggest nested content follows
                    if any(phrase in li_text.lower() for phrase in ['as follows:', 'provided', 'shall be', 'maximum']):
                        target_li = li
                        # For Section 2.060, it should be item (b) which contains "maximum special relief shall be as follows:"
                        break

                if target_li:
                    # Create a nested list for the code block content
                    nested_ul = soup.new_tag('ul')
                    nested_ul['class'] = ['numeric-list']

                    # Convert each line to a list item
                    for item_text in list_items:
                        # Parse the list marker and content
                        close_paren = item_text.index(')')
                        marker = item_text[:close_paren + 1]
                        content = item_text[close_paren + 1:].strip()

                        # Create list item
                        li = soup.new_tag('li')

                        # Create marker span
                        marker_span = soup.new_tag('span')
                        marker_span['class'] = ['list-marker-numeric']
                        marker_span.string = marker

                        li.append(marker_span)
                        li.append(' ' + content)
                        nested_ul.append(li)

                    # Add the nested list to the appropriate alpha item
                    target_li.append(nested_ul)

                    # Remove the code block
                    pre.extract()

                    changes_made = True
                    # Get the marker of the item we attached to
                    marker = target_li.find('span', class_='list-marker-alpha')
                    marker_text = marker.string if marker else "unknown"
                    print(f"  Fixed orphaned code block with {len(list_items)} numeric items, nested under alpha item {marker_text}")

    return changes_made

def fix_section_5100_consistent_formatting(soup):
    """Fix Section 5.100 to remove the roman-list misclassification of (c) and (d)."""
    # Find Section 5.100
    section = None
    for h3 in soup.find_all(['h3']):
        if 'Section 5.100' in h3.get_text() and 'Tree Cutting' in h3.get_text():
            section = h3
            break

    if not section:
        return False

    print(f"\nFixing Section 5.100 Tree Cutting formatting...")

    # Look for the misclassified roman-list with (c) and (d)
    current = section.find_next_sibling()
    fixed = False

    while current and current.name not in ['h2', 'h3']:
        if current.name == 'ul' and 'roman-list' in current.get('class', []):
            # Found the problem list - it has (c) EMERGENCIES and (d) CRITERIA
            items = current.find_all('li', recursive=False)

            # Extract the content
            c_content = None
            d_content = None

            for item in items:
                marker = item.find('span', class_='list-marker-roman')
                if marker:
                    marker_text = marker.get_text()
                    text = item.get_text()
                    if marker_text == '(c)' and 'EMERGENCIES' in text:
                        c_content = text
                    elif marker_text == '(d)' and 'CRITERIA' in text:
                        d_content = text

            if c_content and d_content:
                # Replace the roman list with regular paragraphs like (a) and (b)
                print(f"  Found misclassified roman-list with (c) and (d)")

                # Create paragraph for (c)
                p_c = soup.new_tag('p')
                p_c.string = c_content

                # Create paragraph for (d)
                p_d = soup.new_tag('p')
                p_d.string = d_content

                # Insert the new paragraphs
                current.insert_after(p_d)
                current.insert_after(p_c)

                # Remove the roman list
                current.decompose()

                fixed = True
                print(f"  Fixed: Converted (c) and (d) from roman-list to paragraphs matching (a) and (b)")
                break

        current = current.find_next_sibling()

    return fixed

def fix_section_5120_home_occupations(soup):
    """Fix Section 5.120 where (a) DEFINITION and (b) PURPOSE have orphaned numbered lists."""
    # Find Section 5.120
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        if 'Section 5.120' in heading.get_text() and 'Home Occupations' in heading.get_text():
            print(f"\nFixing Section 5.120 Home Occupations structure...")

            # Collect the items that should be in an alpha list
            items_to_combine = []
            current = heading.find_next_sibling()

            while current and current.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                if current.name == 'p':
                    text = current.get_text().strip()
                    # Check for (a) DEFINITION, (b) PURPOSE AND INTENT, (c) MINOR HOME OCCUPATIONS
                    if text.startswith('(a)') or text.startswith('(b)') or text.startswith('(c)'):
                        # This is a main item - collect it with its nested content
                        item_data = {
                            'p': current,
                            'marker': text[0:3],  # (a), (b), or (c)
                            'content': text[3:].strip(),
                            'nested': None
                        }

                        # Check if the next element is an ordered list (nested items)
                        next_elem = current.find_next_sibling()
                        if next_elem and next_elem.name == 'ol':
                            item_data['nested'] = next_elem
                        elif next_elem and next_elem.name == 'p':
                            # Check if there's intro text before the numbered list
                            next_text = next_elem.get_text().strip()
                            if not next_text.startswith('('):
                                # This is intro text, collect it and check for ol after
                                item_data['intro'] = next_elem
                                following = next_elem.find_next_sibling()
                                if following and following.name == 'ol':
                                    item_data['nested'] = following

                        items_to_combine.append(item_data)

                # Stop when we hit the next section or have collected enough
                if len(items_to_combine) >= 3:
                    break

                current = current.find_next_sibling()

            # Now create the proper structure
            if len(items_to_combine) >= 2:  # At least (a) and (b)
                print(f"  Found {len(items_to_combine)} items to structure properly")

                # Create alpha list
                new_ul = soup.new_tag('ul')
                new_ul['class'] = ['alpha-list']

                for item_data in items_to_combine:
                    # Create list item
                    li = soup.new_tag('li')

                    # Add marker
                    marker_span = soup.new_tag('span')
                    marker_span['class'] = ['list-marker-alpha']
                    marker_span.string = item_data['marker']
                    li.append(marker_span)

                    # Add content
                    li.append(' ' + item_data['content'])

                    # Add intro text if present
                    if 'intro' in item_data and item_data['intro']:
                        li.append('\n')
                        li.append(item_data['intro'].get_text().strip())

                    # Add nested list if present
                    if item_data['nested']:
                        # Convert ol to ul with numeric-list class for consistency
                        nested_ul = soup.new_tag('ul')
                        nested_ul['class'] = ['numeric-list']

                        for i, ol_li in enumerate(item_data['nested'].find_all('li', recursive=False), 1):
                            new_li = soup.new_tag('li')

                            # Add numeric marker
                            marker_span = soup.new_tag('span')
                            marker_span['class'] = ['list-marker-numeric']
                            marker_span.string = f"({i})"
                            new_li.append(marker_span)

                            # Add content
                            new_li.append(' ' + ol_li.get_text().strip())
                            nested_ul.append(new_li)

                        li.append(nested_ul)

                    new_ul.append(li)

                # Insert the new list after the heading
                heading.insert_after(new_ul)

                # Remove old elements
                for item_data in items_to_combine:
                    item_data['p'].decompose()
                    if item_data['nested']:
                        item_data['nested'].decompose()
                    if 'intro' in item_data and item_data['intro']:
                        item_data['intro'].decompose()

                print(f"  Fixed: restructured items into proper alpha-list with nested content")
                return

def process_file(filepath):
    """Process a single HTML file"""
    print(f"  Processing lists in {filepath.name}...")

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    # Process in order:
    # 1. Convert paragraph lists to proper lists (multi-line in same <p>)
    convert_paragraph_lists(soup)

    # 2. Convert consecutive paragraph lists (each item in separate <p>)
    convert_consecutive_paragraph_lists(soup)

    # 3. Process nested lists in existing li elements
    process_nested_lists_in_li(soup)

    # 4. Process existing lists (add classes and wrap markers)
    process_existing_lists(soup)

    # 5. Merge separated lists that should be continuous
    merge_separated_lists(soup)

    # 6. Fix misplaced numeric items that should be nested
    fix_misplaced_nested_items(soup)

    # 7. Process lists in table cells
    process_lists_in_tables(soup)

    # 8. Process Document Notes
    process_document_notes(soup)

    # 9. Fix concatenated numeric items (from V2)
    fix_concatenated_numeric_items(soup)

    # 10. Fix orphaned paragraphs after lists (from V2)
    fix_orphaned_paragraphs(soup)

    # 11. Fix orphaned ordered lists (from V2)
    fix_orphaned_ordered_lists(soup)

    # 12. Fix orphaned code blocks that should be nested lists
    fix_orphaned_code_blocks(soup)

    # 13. Fix Section 2.080 single-item list (specific targeted fix)
    fix_section_2080_single_item(soup)

    # 14. Fix Section 4.120 item (d) (specific targeted fix)
    fix_section_4120_item_d(soup)

    # 15. Fix Section 5.080 setback formatting (specific targeted fix)
    fix_section_5080_setback_formatting(soup)

    # 16. Fix Section 5.100 Tree Cutting (specific targeted fix)
    fix_section_5100_consistent_formatting(soup)

    # 17. Fix Section 5.110 Houses Moved Into City (c/d misclassified as roman)
    fix_section_5110_list_classification(soup)

    # 18. Fix Section 5.120 Home Occupations (a/b with nested lists)
    fix_section_5120_home_occupations(soup)

    # Write back
    content = str(soup)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

def main():
    """Process all HTML files in the book directory"""
    book_dir = Path('book')
    
    if not book_dir.exists():
        print("Error: book directory not found. Run mdbook build first.")
        sys.exit(1)
    
    # Process all HTML files
    html_files = list(book_dir.glob('**/*.html'))
    
    if not html_files:
        print("No HTML files found in book directory")
        sys.exit(1)
    
    print(f"Processing {len(html_files)} HTML files...")
    
    for filepath in html_files:
        try:
            process_file(filepath)
        except Exception as e:
            print(f"  Error processing {filepath.name}: {e}")
            continue
    
    print(f"✓ Processed {len(html_files)} files")

if __name__ == '__main__':
    main()