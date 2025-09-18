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

def detect_list_type(text):
    """
    Detect the type of list based on the marker pattern.
    Returns: ('alpha'|'numeric'|'roman'|None, marker_text)
    """
    # Pattern to match list markers
    pattern = re.compile(r'^\s*\(([a-z]+|[0-9]+|[ivxlcdm]+)\)\s+', re.IGNORECASE)
    match = pattern.match(text)
    
    if match:
        marker = match.group(1).lower()
        full_marker = f"({marker})"
        
        # Check type
        if marker.isalpha() and marker not in ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii']:
            return 'alpha', full_marker
        elif marker.isdigit():
            return 'numeric', full_marker
        elif marker in ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xiii', 'xiv', 'xv', 'xvi', 'xvii', 'xviii', 'xix', 'xx']:
            return 'roman', full_marker
    
    return None, None

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
                    import re
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

                for line in lines:
                    item_type, marker = detect_list_type(line)
                    if item_type:
                        list_items.append((line, item_type, marker))
                        if not list_type:
                            list_type = item_type
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
            
            for line in lines:
                line = line.strip()
                if line:
                    item_type, marker = detect_list_type(line)
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
            list_type, marker = detect_list_type(text)
            
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
    for line in lines:
        line = line.strip()
        if line:
            item_type, marker = detect_list_type(line)
            if item_type:
                list_items.append((line, item_type, marker))
    
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
    # Find all paragraphs
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
        item_type, marker = detect_list_type(text)
        
        if item_type:
            # Found a list item - collect consecutive list items
            list_items = []
            list_type = item_type
            j = i
            
            # Look ahead to find all items of the same type
            # Skip non-list paragraphs between list items
            while j < len(paragraphs):
                p_text = paragraphs[j].get_text().strip()
                p_type, p_marker = detect_list_type(p_text)
                
                if p_type and p_type == list_type:
                    # Same type of list item
                    list_items.append((p_text, p_type, p_marker, paragraphs[j]))
                    j += 1
                elif not p_type:
                    # Non-list paragraph - look ahead to see if more list items follow
                    lookahead = j + 1
                    found_more = False
                    while lookahead < min(j + 5, len(paragraphs)):  # Look up to 5 paragraphs ahead
                        ahead_text = paragraphs[lookahead].get_text().strip()
                        ahead_type, _ = detect_list_type(ahead_text)
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
                import re
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
    
    # 5. Process lists in table cells
    process_lists_in_tables(soup)
    
    # 6. Process Document Notes
    process_document_notes(soup)
    
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