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
                parts = re.split(r'\n(?=\(([1-9]|[ivx]+)\))', content)
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
            if 'Front Setback' in text_content or 'Side Setback' in text_content or 'Rear Setback' in text_content:
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

    if code_block_fixed or alpha_fixed or setback_fixed:
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