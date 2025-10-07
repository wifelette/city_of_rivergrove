#!/usr/bin/env python3
"""
Document-Specific Processor for Ordinance #54-89

This processor handles unique formatting issues in Ord #54-89 Land Development
that don't appear in other documents. See docs/one-off-fixes-inventory.md for
rationale.

Specific Issues Fixed:
1. ALL CAPS section headers (e.g., "(a) DEFINITIONS:")
2. Concatenated numeric items under alpha headers
3. Orphaned continuation paragraphs
4. Complex nesting in Sections 5.100, 5.120

Author: Claude Code
Date: January 2025
"""

import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag

def is_all_caps_header(text):
    """
    Detect if text is an ALL CAPS section header.
    Pattern: (a) WORD1 WORD2... (all caps, possibly with colons)
    """
    # Remove the marker and check if rest is mostly uppercase
    pattern = r'^\([a-z]\)\s+([A-Z\s:]+)$'
    match = re.match(pattern, text.strip())
    if match:
        content = match.group(1).strip()
        # Check if it's mostly caps (allowing for colons and spaces)
        letters_only = re.sub(r'[^A-Za-z]', '', content)
        if letters_only and letters_only.isupper():
            return True
    return False

def should_skip_conversion(paragraph):
    """
    Determine if a paragraph starting with (a), (b), etc. should NOT be
    converted to a list item.

    Returns True if it should stay as a paragraph.
    """
    text = paragraph.get_text().strip()

    # Skip ALL CAPS headers
    if is_all_caps_header(text):
        return True

    # Skip if it's very short (likely a header)
    if len(text) < 50 and text.endswith(':'):
        return True

    return False

def merge_alpha_with_following_ol(soup):
    """
    Find paragraphs like "(a) DEFINITION" followed by <ol> elements,
    and merge them into proper nested list structure.

    Pattern:
        <p>(a) DEFINITION</p>
        <ol>
          <li>Item 1</li>
          <li>Item 2</li>
        </ol>

    Becomes:
        <ul class="alpha-list">
          <li>
            <span class="list-marker-alpha">(a)</span> DEFINITION
            <ol>
              <li>Item 1</li>
              <li>Item 2</li>
            </ol>
          </li>
        </ul>
    """
    changes_made = 0

    # Find all paragraphs that start with alpha markers
    alpha_pattern = re.compile(r'^\s*\(([a-z])\)\s+(.+)', re.IGNORECASE)

    for p in soup.find_all('p'):
        text = p.get_text().strip()
        match = alpha_pattern.match(text)

        if not match:
            continue

        marker = match.group(1).lower()
        content = match.group(2)

        # Check if next sibling is an <ol>
        next_elem = p.find_next_sibling()
        if not next_elem or next_elem.name != 'ol':
            continue

        # Don't convert ALL CAPS headers
        if should_skip_conversion(p):
            # But we should still style them specially
            p['class'] = p.get('class', []) + ['section-header-alpha']
            continue

        # Create new list structure
        ul = soup.new_tag('ul', **{'class': 'alpha-list'})
        li = soup.new_tag('li')

        # Add styled marker
        span = soup.new_tag('span', **{'class': 'list-marker-alpha'})
        span.string = f'({marker})'
        li.append(span)
        li.append(NavigableString(' ' + content))

        # Move the <ol> inside the <li>
        ol = next_elem.extract()
        li.append(ol)

        ul.append(li)

        # Replace original paragraph with new structure
        p.replace_with(ul)
        changes_made += 1

    return changes_made

def nest_continuation_paragraphs(soup):
    """
    Find paragraphs that should be nested inside preceding list items.

    Pattern:
        <ul class="alpha-list">
          <li>(b) PURPOSE AND INTENT</li>
        </ul>
        <p>The conduct of business in residences...</p>

    The paragraph should be nested inside the <li>.
    """
    changes_made = 0

    for ul in soup.find_all('ul', class_='alpha-list'):
        # Get the last <li> in this list
        list_items = ul.find_all('li', recursive=False)
        if not list_items:
            continue

        last_li = list_items[-1]

        # Check for following paragraph
        next_elem = ul.find_next_sibling()
        if not next_elem or next_elem.name != 'p':
            continue

        # Check if the next sibling after that is another list or heading
        # (indicating this paragraph belongs to the current list item)
        following = next_elem.find_next_sibling()
        if following and following.name in ['ul', 'ol', 'h3', 'h4']:
            # This paragraph is likely a continuation
            p = next_elem.extract()
            last_li.append(p)
            changes_made += 1

    return changes_made

def style_all_caps_headers(soup):
    """
    Add special CSS classes to ALL CAPS headers that we're leaving as paragraphs.
    This allows them to be styled distinctly from regular text.
    """
    changes_made = 0

    for p in soup.find_all('p'):
        text = p.get_text().strip()
        if is_all_caps_header(text):
            classes = p.get('class', [])
            if 'section-header-alpha' not in classes:
                p['class'] = classes + ['section-header-alpha']
                changes_made += 1

    return changes_made

def process_file(html_file):
    """Process a single HTML file."""
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Track changes
    total_changes = 0

    # Run processing steps
    changes = merge_alpha_with_following_ol(soup)
    if changes > 0:
        print(f"  • Merged {changes} alpha headers with following lists")
        total_changes += changes

    changes = nest_continuation_paragraphs(soup)
    if changes > 0:
        print(f"  • Nested {changes} continuation paragraphs")
        total_changes += changes

    changes = style_all_caps_headers(soup)
    if changes > 0:
        print(f"  • Styled {changes} ALL CAPS headers")
        total_changes += changes

    # Write back if changes were made
    if total_changes > 0:
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        return True

    return False

def main():
    """Main entry point."""
    book_dir = Path('book')

    # Only process Ord #54-89
    target_file = book_dir / 'ordinances' / '1989-Ord-54-89C-Land-Development.html'

    if not target_file.exists():
        print(f"⚠️  Target file not found: {target_file}")
        return 1

    print(f"🔧 Processing Ordinance #54-89 (document-specific fixes)...")

    if process_file(target_file):
        print(f"  ✅ Applied Ord #54-specific formatting fixes")
    else:
        print(f"  ℹ️  No changes needed")

    return 0

if __name__ == '__main__':
    sys.exit(main())
