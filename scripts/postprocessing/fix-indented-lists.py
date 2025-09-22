#!/usr/bin/env python3
"""
Fix indented list items that mdBook interprets as code blocks.
Specifically handles cases where items like (1), (2), (3) are indented
under parent items like (a), (b), (c).

Author: Claude
Date: 2025
"""

from bs4 import BeautifulSoup, NavigableString, Tag
from pathlib import Path
import re
import sys

def fix_code_block_lists(soup):
    """Convert code blocks that should be nested lists back to proper list format."""
    changes_made = False

    # Find all code blocks that might be misinterpreted lists
    for pre in soup.find_all('pre'):
        code = pre.find('code')
        if not code:
            continue

        text = code.get_text()

        # Check if this looks like list items (numeric or roman numerals)
        if re.match(r'^\s*\(([1-9]|[ivx]+)\)', text):
            # Split into lines
            lines = text.split('\n')

            # Determine if it's numeric or roman numerals
            is_roman = bool(re.match(r'^\s*\([ivx]+\)', text))
            list_class = 'roman-list' if is_roman else 'numeric-list'
            marker_class = 'roman-marker' if is_roman else 'list-marker-numeric'

            # Create appropriate list
            new_ul = soup.new_tag('ul', **{'class': list_class})

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Extract the marker and content (works for both numeric and roman)
                match = re.match(r'^(\([0-9ivx]+\))\s*(.*)$', line)
                if match:
                    marker = match.group(1)
                    content = match.group(2)

                    # Create list item with styled marker
                    li = soup.new_tag('li')
                    span = soup.new_tag('span', **{'class': marker_class})
                    span.string = marker
                    li.append(span)
                    li.append(' ' + content)
                    new_ul.append(li)

            # Check if this code block follows a paragraph with item (b) or similar
            prev = pre.find_previous_sibling()
            if prev and prev.name == 'p':
                text = prev.get_text()
                # If previous paragraph looks like a list item that should have sub-items
                if re.match(r'^\([a-z]\)', text):
                    # Create a proper list structure
                    # Convert the paragraph to a list item
                    match = re.match(r'^(\([a-z]\))\s*(.*)$', text)
                    if match:
                        marker = match.group(1)
                        content = match.group(2)

                        # Create or find the parent ul
                        parent_ul = None
                        prev_prev = prev.find_previous_sibling()

                        # Look for existing ul with alpha-list class
                        for sibling in prev.find_previous_siblings():
                            if sibling.name == 'ul' and 'alpha-list' in sibling.get('class', []):
                                parent_ul = sibling
                                break

                        if not parent_ul:
                            parent_ul = soup.new_tag('ul', **{'class': 'alpha-list'})
                            prev.insert_before(parent_ul)

                        # Create the list item with the alpha marker
                        li = soup.new_tag('li')
                        span = soup.new_tag('span', **{'class': 'list-marker-alpha'})
                        span.string = marker
                        li.append(span)
                        li.append(' ' + content)

                        # Add the numeric sub-list to this item
                        li.append(new_ul)
                        parent_ul.append(li)

                        # Remove the original paragraph and code block
                        prev.extract()
                        pre.extract()
                        changes_made = True
                        print(f"  Fixed code block with {len(new_ul.find_all('li'))} numeric items under item {marker}")
                        continue

            # If not handled above, just replace the code block with the list
            pre.replace_with(new_ul)
            changes_made = True
            print(f"  Fixed standalone code block with {len(new_ul.find_all('li'))} numeric items")

    return changes_made

def convert_alpha_paragraphs_to_list(soup):
    """Convert paragraphs that start with (a), (b), (c) to proper list items."""
    changes_made = False

    # Find all paragraphs
    for p in soup.find_all('p'):
        text = p.get_text()

        # Check if this paragraph starts with an alpha marker
        match = re.match(r'^(\([a-z]\))\s*(.*)$', text, re.DOTALL)
        if match:
            marker = match.group(1)
            content = match.group(2)

            # Check if content contains embedded numeric or roman numeral sub-items
            # Pattern: (1) ... (2) ... (3) ... or (i) ... (ii) ... (iii) ...
            if re.search(r'\n?\(([1-9]|[ivx]+)\)', content):
                # Split content into main text and sub-items
                # Use non-capturing group to avoid extra parts in split
                parts = re.split(r'\n(?=\((?:[1-9]|[ivx]+)\))', content)
                main_text = parts[0].strip()

                # Create the alpha list item
                parent_ul = None
                prev = p.find_previous_sibling()
                if prev:
                    if prev.name == 'ul' and 'alpha-list' in prev.get('class', []):
                        parent_ul = prev
                    elif prev.name == 'p':
                        prev_text = prev.get_text()
                        if re.match(r'^\([a-z]\)', prev_text):
                            prev_prev = prev.find_previous_sibling()
                            if prev_prev and prev_prev.name == 'ul' and 'alpha-list' in prev_prev.get('class', []):
                                parent_ul = prev_prev

                if not parent_ul:
                    parent_ul = soup.new_tag('ul', **{'class': 'alpha-list'})
                    p.insert_before(parent_ul)

                # Create the list item with alpha marker
                li = soup.new_tag('li')
                span = soup.new_tag('span', **{'class': 'list-marker-alpha'})
                span.string = marker
                li.append(span)
                li.append(' ' + main_text)

                # Create nested list for sub-items
                if len(parts) > 1:
                    # Determine if sub-items are numeric or roman
                    first_sub_item = parts[1].strip() if len(parts) > 1 else ""
                    is_roman = bool(re.match(r'^\([ivx]+\)', first_sub_item))
                    list_class = 'roman-list' if is_roman else 'numeric-list'
                    marker_class = 'roman-marker' if is_roman else 'list-marker-numeric'

                    nested_ul = soup.new_tag('ul', **{'class': list_class})

                    # Process each sub-item (numeric or roman)
                    for part in parts[1:]:
                        part = part.strip()
                        num_match = re.match(r'^(\([0-9ivx]+\))\s*(.*)$', part, re.DOTALL)
                        if num_match:
                            num_marker = num_match.group(1)
                            num_content = num_match.group(2)

                            # Create nested list item
                            nested_li = soup.new_tag('li')
                            nested_span = soup.new_tag('span', **{'class': marker_class})
                            nested_span.string = num_marker
                            nested_li.append(nested_span)
                            nested_li.append(' ' + num_content)
                            nested_ul.append(nested_li)

                    # Add nested list to parent item
                    li.append(nested_ul)
                    print(f"  Created nested list for item {marker} with {len(parts)-1} sub-items")

                parent_ul.append(li)
                p.extract()
                changes_made = True

            else:
                # Regular alpha item without sub-items
                # Check if this belongs to a series of list items
                # Look for a parent ul or nearby siblings with alpha markers
                parent_ul = None

                # Check previous sibling
                prev = p.find_previous_sibling()
                if prev:
                    if prev.name == 'ul' and 'alpha-list' in prev.get('class', []):
                        parent_ul = prev
                    elif prev.name == 'p':
                        # Check if previous paragraph was also an alpha item
                        prev_text = prev.get_text()
                        if re.match(r'^\([a-z]\)', prev_text):
                            # Find or create the ul
                            prev_prev = prev.find_previous_sibling()
                            if prev_prev and prev_prev.name == 'ul' and 'alpha-list' in prev_prev.get('class', []):
                                parent_ul = prev_prev

                # If we don't have a parent_ul yet, create one
                if not parent_ul:
                    parent_ul = soup.new_tag('ul', **{'class': 'alpha-list'})
                    p.insert_before(parent_ul)

                # Create the list item
                li = soup.new_tag('li')
                span = soup.new_tag('span', **{'class': 'list-marker-alpha'})
                span.string = marker
                li.append(span)
                li.append(' ' + content)

                # Add to parent ul
                parent_ul.append(li)

                # Remove the original paragraph
                p.extract()
                changes_made = True
                print(f"  Converted paragraph {marker} to list item")

    return changes_made

def fix_embedded_setback_lists(soup):
    """Fix list items that contain embedded setback measurements."""
    changes_made = False

    # Find all list items in alpha-lists
    for ul in soup.find_all('ul', class_='alpha-list'):
        for li in ul.find_all('li', recursive=False):
            # Get the text content
            text_content = ''
            for child in li.children:
                if isinstance(child, str):
                    text_content += child
                elif child.name != 'span':
                    text_content += child.get_text()

            # Check if this contains setback lines (Front Setback, Side Setback, etc.)
            # Only apply this fix to items that actually have setback patterns
            if ('Front Setback - ' in text_content or
                'Side Setback - ' in text_content or
                'Rear Setback - ' in text_content):
                # Extract the marker span first
                marker_span = li.find('span', class_='list-marker-alpha')
                if not marker_span:
                    continue

                # Split the content into main text and setback lines
                lines = text_content.split('\n')
                main_text = ''
                setback_lines = []

                for line in lines:
                    line = line.strip()
                    if line and ('Setback' in line and ' - ' in line):
                        setback_lines.append(line)
                    elif line:
                        if not setback_lines:  # Still in main text
                            if main_text:
                                main_text += ' '
                            main_text += line

                if setback_lines:
                    # Clear the li and rebuild it
                    li.clear()

                    # Add back the marker span
                    li.append(marker_span)
                    li.append(' ' + main_text)

                    # Create a nested unordered list for setback items
                    nested_ul = soup.new_tag('ul', **{'class': 'setback-list'})
                    for setback_line in setback_lines:
                        nested_li = soup.new_tag('li')
                        nested_li.string = setback_line
                        nested_ul.append(nested_li)

                    li.append(nested_ul)
                    changes_made = True
                    print(f"  Fixed embedded setback list with {len(setback_lines)} items")

    return changes_made

def fix_misplaced_numeric_items(soup):
    """Fix numeric items that should be nested under the previous alpha item.

    This handles cases where mdBook creates separate list items with numeric markers
    that should actually be nested under the previous alpha item.
    Example: Item (i) "Lot" followed by a separate item with "1. Corner Lot..."
    """
    changes_made = False

    # Find all alpha lists
    for ul in soup.find_all('ul', class_='alpha-list'):
        items = ul.find_all('li', recursive=False)

        i = 0
        while i < len(items):
            li = items[i]

            # Check if this is an alpha item that should have nested items
            alpha_marker = li.find('span', class_='list-marker-alpha')
            if alpha_marker:
                text = li.get_text()

                # Check if the next item is a numeric item that should be nested
                if i + 1 < len(items):
                    next_li = items[i + 1]
                    next_marker = next_li.find('span', class_='list-marker-numeric')

                    if next_marker:
                        # This numeric item should be nested under the alpha item
                        # Extract all the content from the numeric item
                        next_text = next_li.get_text()

                        # Check if it contains multiple numbered items concatenated
                        # Pattern: "1. ... 2. ... 3. ..."
                        import re
                        parts = re.split(r'(?=\d+\.\s+")', next_text)

                        if len(parts) > 1 or '2.' in next_text or '3.' in next_text:
                            # Create a nested list
                            nested_ul = soup.new_tag('ul', **{'class': 'numeric-list'})

                            # Split the text into individual numbered items
                            # Handle both "1." and "(1)" patterns
                            pattern = r'(\d+\.)\s*(".*?"[^"]*?)(?=\d+\.|$)'
                            matches = re.findall(pattern, next_text, re.DOTALL)

                            if matches:
                                for num, content in matches:
                                    new_li = soup.new_tag('li')

                                    # Convert "1." to "(1)"
                                    marker = f"({num[:-1]})"
                                    marker_span = soup.new_tag('span', **{'class': 'list-marker-numeric'})
                                    marker_span.string = marker
                                    new_li.append(marker_span)
                                    new_li.append(' ')
                                    new_li.append(content.strip())

                                    nested_ul.append(new_li)
                            else:
                                # Fallback: try to split by line breaks if quotes pattern doesn't work
                                lines = next_text.split('.')
                                item_num = 1
                                for line in lines:
                                    line = line.strip()
                                    if line and line[0].isdigit():
                                        # This is a numbered item
                                        # Remove the number from the beginning
                                        content = re.sub(r'^\d+\s*', '', line)
                                        if content:
                                            new_li = soup.new_tag('li')
                                            marker = f"({item_num})"
                                            marker_span = soup.new_tag('span', **{'class': 'list-marker-numeric'})
                                            marker_span.string = marker
                                            new_li.append(marker_span)
                                            new_li.append(' ')
                                            new_li.append(content.strip())
                                            nested_ul.append(new_li)
                                            item_num += 1

                            # Add the nested list to the alpha item
                            li.append(nested_ul)

                            # Remove the misplaced numeric item
                            next_li.extract()
                            changes_made = True
                            print(f"  Fixed misplaced numeric items under {alpha_marker.get_text()} ({len(nested_ul.find_all('li'))} items)")

                            # Update items list since we removed one
                            items = ul.find_all('li', recursive=False)
                            continue

            i += 1

    return changes_made

def fix_orphaned_numbered_lists(soup):
    """Fix numbered lists that should be nested under alpha items but aren't.

    This handles cases like Section 5.100 where:
    (a) DEFINITIONS:
    1) "Tree": ...
    2) "Cutting": ...

    The numbered list appears after an alpha item that ends with a colon.
    """
    changes_made = False

    # Find all alpha-list items
    for ul in soup.find_all('ul', class_='alpha-list'):
        # Look at each list item
        for li in ul.find_all('li', recursive=False):
            # Check if this item's text ends with a colon (indicates it should have sub-items)
            text_content = li.get_text().strip()
            if text_content.endswith(':'):
                # Look for an <ol> that immediately follows this ul
                next_sibling = ul.find_next_sibling()

                # Check if the next sibling is an <ol> (ordered list)
                if next_sibling and next_sibling.name == 'ol':
                    # This ol should be nested inside the li
                    # Convert the ol to use our custom classes
                    new_ul = soup.new_tag('ul', **{'class': 'numeric-list'})

                    # Process each li in the ol
                    for idx, ol_li in enumerate(next_sibling.find_all('li'), 1):
                        # Create new list item
                        new_li = soup.new_tag('li')

                        # Add marker - mdBook already stripped the numbers, so we add them back
                        marker = f"({idx})"
                        marker_span = soup.new_tag('span', **{'class': 'list-marker-numeric'})
                        marker_span.string = marker
                        new_li.append(marker_span)
                        new_li.append(' ')

                        # Add all content from the original li
                        for child in ol_li.children:
                            if child.name == 'p':
                                # Preserve the text from p tags
                                new_li.append(child.get_text().strip())
                            elif isinstance(child, str) and child.strip():
                                new_li.append(child.strip())
                            else:
                                # For other elements, try to get their text
                                if hasattr(child, 'get_text'):
                                    text = child.get_text().strip()
                                    if text:
                                        new_li.append(text)

                        new_ul.append(new_li)

                    # Add the new ul to the li
                    li.append(new_ul)

                    # Remove the original ol
                    next_sibling.extract()

                    changes_made = True
                    print(f"  Fixed orphaned numbered list after item ending with ':' ({len(new_ul.find_all('li'))} items)")

    return changes_made

def process_html_file(file_path):
    """Process a single HTML file to fix code block lists."""
    path = Path(file_path)
    if not path.exists():
        print(f"File not found: {file_path}")
        return False

    with open(path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    # Run all fixes
    code_block_fixed = fix_code_block_lists(soup)
    alpha_fixed = convert_alpha_paragraphs_to_list(soup)
    setback_fixed = fix_embedded_setback_lists(soup)
    misplaced_fixed = fix_misplaced_numeric_items(soup)
    orphaned_fixed = fix_orphaned_numbered_lists(soup)

    if code_block_fixed or alpha_fixed or setback_fixed or misplaced_fixed or orphaned_fixed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"✓ Fixed lists in {path.name}")
        return True

    return False

def main():
    """Process all ordinance HTML files or specific files if provided."""
    if len(sys.argv) > 1:
        files = sys.argv[1:]
    else:
        # Process all ordinance files by default
        book_dir = Path('book/ordinances')
        if book_dir.exists():
            files = [str(f) for f in book_dir.glob('*.html')]
        else:
            print("No book/ordinances directory found")
            return

    fixed_count = 0
    for file_path in files:
        if process_html_file(file_path):
            fixed_count += 1

    if fixed_count > 0:
        print(f"\n✓ Fixed {fixed_count} file(s)")

if __name__ == '__main__':
    main()