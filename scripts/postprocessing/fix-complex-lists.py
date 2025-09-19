#!/usr/bin/env python3
"""
Fix complex list issues in documents with nested lists and multiple sections.
This is a generalized version of fix-ord54-lists.py that works on any document.

Key features:
1. Detects orphaned list items that should be in lists
2. Finds list items that got merged into wrong sections
3. Properly nests numeric items under alphabetic parents
4. Works across entire document, not just specific sections

Author: Claude
Date: 2025
"""

from bs4 import BeautifulSoup, NavigableString, Tag
from pathlib import Path
import re
import sys

def is_list_item_text(text):
    """Check if text starts with a list marker like (a), (1), etc."""
    if not text:
        return False
    text = text.strip()
    # Check for (a), (b), etc. or (1), (2), etc.
    return bool(re.match(r'^\([a-z]\)|\(\d+\)', text, re.IGNORECASE))

def get_list_marker(text):
    """Extract the list marker from text, e.g., '(a)' from '(a) Some text'"""
    match = re.match(r'^(\([a-z]\)|\(\d+\))', text.strip(), re.IGNORECASE)
    return match.group(1) if match else None

def is_numeric_marker(marker):
    """Check if a marker is numeric like (1), (2)"""
    return bool(re.match(r'^\(\d+\)$', marker))

def is_alpha_marker(marker):
    """Check if a marker is alphabetic like (a), (b)"""
    return bool(re.match(r'^\([a-z]\)$', marker, re.IGNORECASE))

def find_orphaned_list_items(soup):
    """Find paragraphs that contain list items but aren't in lists"""
    orphaned = []

    # Look for paragraphs containing list markers
    for p in soup.find_all('p'):
        text = p.get_text().strip()
        if is_list_item_text(text):
            # Check if this paragraph is already in a list
            if not p.find_parent(['ul', 'ol', 'li']):
                orphaned.append(p)

    return orphaned

def find_section_boundaries(soup):
    """Find all section headings and their positions"""
    sections = []

    # Find all h2, h3, h4 headings
    for heading in soup.find_all(['h2', 'h3', 'h4']):
        sections.append({
            'heading': heading,
            'text': heading.get_text().strip(),
            'level': int(heading.name[1])  # h2 -> 2, h3 -> 3, etc.
        })

    return sections

def should_item_be_in_section(item_text, section_info, next_section_info):
    """Determine if a list item belongs in the current section"""
    # This is a heuristic - we assume items between two sections belong to the first
    # unless they explicitly reference the second section

    # For now, simple rule: if we're between sections, item belongs to current section
    return True

def create_list_from_orphans(orphans, list_type='alpha'):
    """Create a proper list structure from orphaned paragraphs"""
    if not orphans:
        return None

    # Create the list element
    new_list = BeautifulSoup('<ul class="alpha-list"></ul>', 'html.parser').ul
    if list_type == 'numeric':
        new_list['class'] = ['numeric-list']

    current_parent = None

    for orphan in orphans:
        text = orphan.get_text().strip()
        marker = get_list_marker(text)

        if not marker:
            continue

        # Create list item
        li = BeautifulSoup('<li></li>', 'html.parser').li

        # Add styled marker span
        if is_alpha_marker(marker):
            span_class = 'list-marker-alpha'
        else:
            span_class = 'list-marker-numeric'

        marker_span = BeautifulSoup(f'<span class="{span_class}">{marker}</span>', 'html.parser').span
        li.append(marker_span)

        # Add the content (without the marker)
        content = text[len(marker):].strip()
        li.append(' ' + content)

        # Check if this is a numeric item that should be nested
        if is_numeric_marker(marker) and current_parent and is_alpha_marker(get_list_marker(current_parent.get_text())):
            # This numeric item should be nested under the previous alpha item
            nested_list = current_parent.find('ul', class_='numeric-list')
            if not nested_list:
                # Create nested list
                nested_list = BeautifulSoup('<ul class="numeric-list"></ul>', 'html.parser').ul
                current_parent.append(nested_list)
            nested_list.append(li)
        else:
            # Add to main list
            new_list.append(li)
            if is_alpha_marker(marker):
                current_parent = li

    return new_list

def fix_document_lists(html_file):
    """Fix list issues throughout the document"""
    path = Path(html_file)

    if not path.exists():
        print(f"File not found: {html_file}")
        return False

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    changes_made = False

    # Find section boundaries
    sections = find_section_boundaries(soup)

    # Process each section
    for i, section in enumerate(sections):
        heading = section['heading']

        # Find the next section (if any)
        next_section = sections[i + 1] if i + 1 < len(sections) else None

        # Find orphaned list items after this heading
        orphans_in_section = []
        current = heading.next_sibling

        while current:
            # Stop if we hit the next section
            if next_section and current == next_section['heading']:
                break

            # Check if this is an orphaned list item
            if isinstance(current, Tag):
                if current.name == 'p' and is_list_item_text(current.get_text()):
                    # Check if already in a list
                    if not current.find_parent(['ul', 'ol', 'li']):
                        orphans_in_section.append(current)

            current = current.next_sibling

        # If we found orphans, create a proper list
        if orphans_in_section:
            print(f"Found {len(orphans_in_section)} orphaned items in section: {section['text']}")

            # Group consecutive orphans
            groups = []
            current_group = []

            for orphan in orphans_in_section:
                if not current_group:
                    current_group.append(orphan)
                else:
                    # Check if this orphan is consecutive with the last one
                    last_orphan = current_group[-1]
                    # Find all elements between them
                    between = []
                    elem = last_orphan.next_sibling
                    while elem and elem != orphan:
                        if isinstance(elem, Tag):
                            between.append(elem)
                        elem = elem.next_sibling

                    # If there are no non-empty elements between, they're consecutive
                    if not any(e.get_text().strip() for e in between if isinstance(e, Tag)):
                        current_group.append(orphan)
                    else:
                        # Start new group
                        groups.append(current_group)
                        current_group = [orphan]

            if current_group:
                groups.append(current_group)

            # Process each group
            for group in groups:
                # Determine list type from first item
                first_text = group[0].get_text().strip()
                first_marker = get_list_marker(first_text)
                list_type = 'alpha' if is_alpha_marker(first_marker) else 'numeric'

                # Create list from group
                new_list = create_list_from_orphans(group, list_type)

                if new_list:
                    # Insert the list where the first orphan was
                    group[0].insert_before(new_list)

                    # Remove the orphaned paragraphs
                    for orphan in group:
                        orphan.decompose()

                    changes_made = True

    # Also check for existing lists that have items that should be nested
    for ul in soup.find_all('ul', class_='alpha-list'):
        items = ul.find_all('li', recursive=False)
        items_to_nest = []
        current_parent = None

        for item in items:
            text = item.get_text().strip()
            marker = get_list_marker(text)

            if marker:
                if is_alpha_marker(marker):
                    # This is a potential parent
                    if items_to_nest and current_parent:
                        # Nest the accumulated numeric items
                        nest_items_under_parent(current_parent, items_to_nest)
                        changes_made = True
                        items_to_nest = []
                    current_parent = item
                elif is_numeric_marker(marker) and current_parent:
                    # This should be nested
                    items_to_nest.append(item)

        # Handle any remaining items to nest
        if items_to_nest and current_parent:
            nest_items_under_parent(current_parent, items_to_nest)
            changes_made = True

    # Save if changes were made
    if changes_made:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"✓ Fixed list issues in {path.name}")
        return True
    else:
        print(f"No list issues found in {path.name}")
        return False

def nest_items_under_parent(parent_li, items_to_nest):
    """Nest numeric items under an alphabetic parent item"""
    if not items_to_nest:
        return

    # Check if parent already has a nested list
    nested_ul = parent_li.find('ul', class_='numeric-list')
    if not nested_ul:
        # Create nested list
        nested_ul = BeautifulSoup('<ul class="numeric-list"></ul>', 'html.parser').ul
        parent_li.append(nested_ul)

    # Move items to nested list
    for item in items_to_nest:
        item.extract()
        nested_ul.append(item)

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        # If no arguments, process known problematic files
        files_to_fix = [
            'book/ordinances/1989-Ord-54-89C-Land-Development.html'
        ]
    else:
        files_to_fix = sys.argv[1:]

    success_count = 0
    for file_path in files_to_fix:
        if fix_document_lists(file_path):
            success_count += 1

    if success_count > 0:
        print(f"\n✅ Fixed list issues in {success_count} file(s)")
    else:
        print("\n❌ No list issues were fixed")

if __name__ == '__main__':
    main()