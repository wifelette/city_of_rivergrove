#!/usr/bin/env python3
"""
Custom list processor that converts special list formats to proper HTML
while preserving the exact legal enumeration style.
This runs as a post-processor after mdBook generates HTML.
"""

import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

def process_numbered_lists(html_content):
    """Convert (1), (2) style lists in paragraphs to proper HTML lists"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find paragraphs that contain list items
    for p in soup.find_all('p'):
        text = p.get_text()
        
        # Check if this paragraph contains multiple numbered items
        if re.search(r'\(\d+\)', text):
            # Split by line breaks
            lines = text.split('\n')
            
            # Process lines to group numbered items with their content
            numbered_items = []
            current_item = None
            
            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue
                    
                # Check if this is a new numbered item
                match = re.match(r'^(\((\d+)\))\s+(.+)$', line_stripped)
                if match:
                    # Save previous item if exists
                    if current_item:
                        numbered_items.append(current_item)
                    # Start new item
                    current_item = {
                        'marker': match.group(1),
                        'number': match.group(2),
                        'text': match.group(3)
                    }
                elif current_item:
                    # This is a continuation of the current item
                    # Add to the current item's text
                    current_item['text'] += '\n' + line_stripped
            
            # Don't forget the last item
            if current_item:
                numbered_items.append(current_item)
            
            # If we found multiple items, convert to ordered list
            if len(numbered_items) > 1:
                ol = soup.new_tag('ol')
                for item in numbered_items:
                    li = soup.new_tag('li')
                    # Keep the original marker in a span for styling
                    marker_span = soup.new_tag('span', attrs={'class': 'custom-list-marker'})
                    marker_span.string = item['marker']
                    li.append(marker_span)
                    
                    # Process the text content, looking for roman numerals
                    text_lines = item['text'].split('\n')
                    
                    # Check if this item contains roman numeral sublists
                    has_roman_numerals = False
                    roman_items = []
                    regular_text = []
                    
                    for text_line in text_lines:
                        # Check for roman numeral pattern
                        roman_match = re.match(r'^\s*\(([ivx]+)\)\s+(.+)$', text_line.strip(), re.IGNORECASE)
                        if roman_match:
                            has_roman_numerals = True
                            roman_items.append({
                                'numeral': roman_match.group(1),
                                'text': roman_match.group(2)
                            })
                        elif not has_roman_numerals:
                            # This is regular text before any roman numerals
                            regular_text.append(text_line)
                        elif roman_items:
                            # Continuation of the last roman numeral item
                            roman_items[-1]['text'] += ' ' + text_line.strip()
                    
                    # Add the regular text first
                    if regular_text:
                        li.append(' ' + regular_text[0])
                        for text_line in regular_text[1:]:
                            if text_line.strip():
                                li.append(' ' + text_line)
                    
                    # If we have roman numerals, create a nested structure
                    if has_roman_numerals and roman_items:
                        sublist = soup.new_tag('div', attrs={'class': 'roman-sublist'})
                        for roman_item in roman_items:
                            item_div = soup.new_tag('div', attrs={'class': 'roman-sublist-item'})
                            marker = soup.new_tag('span', attrs={'class': 'roman-marker'})
                            marker.string = f"({roman_item['numeral']})"
                            item_div.append(marker)
                            item_div.append(' ' + roman_item['text'])
                            sublist.append(item_div)
                        li.append(sublist)
                    elif not regular_text and not has_roman_numerals:
                        # No special formatting needed, just add the text
                        for i, text_line in enumerate(text_lines):
                            if i > 0:
                                li.append(soup.new_tag('br'))
                            li.append(' ' + text_line if i == 0 else text_line)
                    
                    ol.append(li)
                
                # Replace the paragraph with the list
                p.replace_with(ol)
    
    return str(soup)

def process_special_numbered_lists(html_content):
    """Handle special numbered lists that start at non-standard numbers (e.g., 1.4)"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for sequences of paragraphs that match our special numbering pattern
    # Specifically looking for lists that start at 1.4 (Resolution 41425)
    paragraphs = soup.find_all('p')
    
    for i, p in enumerate(paragraphs):
        text = p.get_text().strip()
        # Check if this is the start of our special list (1.4)
        if text.startswith('1.4 '):
            # Found the start of a special list
            list_items = []
            current_p = p
            p_index = i
            
            # Collect all consecutive numbered items
            while p_index < len(paragraphs):
                current_text = paragraphs[p_index].get_text().strip()
                match = re.match(r'^(1\.(\d+))\s+(.+)$', current_text)
                
                if match:
                    list_items.append({
                        'full_num': match.group(1),
                        'sub_num': match.group(2),
                        'content': match.group(3),
                        'element': paragraphs[p_index]
                    })
                    p_index += 1
                else:
                    # End of the numbered sequence
                    break
            
            # Only process if we found a sequence starting at 1.4
            if list_items and list_items[0]['full_num'] == '1.4':
                # Create an ordered list with custom styling
                ol = soup.new_tag('ol', attrs={'class': 'special-start-list'})
                
                # Set the counter to start at 4
                ol['style'] = 'counter-reset: list-item 3;'
                
                # Create list items
                for item in list_items:
                    li = soup.new_tag('li')
                    # Don't set value attribute to avoid browser numbering
                    
                    # Add custom number as span
                    num_span = soup.new_tag('span', attrs={'class': 'special-list-number'})
                    num_span.string = item['full_num']
                    li.append(num_span)
                    li.append(' ' + item['content'])
                    ol.append(li)
                
                # Replace all the paragraphs with the single list
                list_items[0]['element'].replace_with(ol)
                for item in list_items[1:]:
                    item['element'].decompose()
    
    return str(soup)

def process_roman_lists(html_content):
    """Convert roman numeral lists in preformatted blocks to proper lists"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Process lists in <pre> blocks
    for pre in soup.find_all('pre'):
        text = pre.get_text()
        lines = text.split('\n')
        
        # Check if this looks like a roman numeral list
        roman_pattern = r'^\s*\(([ivx]+)\)\s+(.+)$'
        list_items = []
        
        for line in lines:
            match = re.match(roman_pattern, line.strip(), re.IGNORECASE)
            if match:
                list_items.append({
                    'numeral': match.group(1),
                    'text': match.group(2)
                })
        
        # If we found roman numeral items, convert to a list
        if list_items:
            ol = soup.new_tag('ol', attrs={'class': 'roman-list'})
            for item in list_items:
                li = soup.new_tag('li')
                # Add the roman numeral as a span
                roman_span = soup.new_tag('span', attrs={'class': 'roman-marker'})
                roman_span.string = f"({item['numeral']})"
                li.append(roman_span)
                li.append(' ' + item['text'])
                ol.append(li)
            
            pre.replace_with(ol)
    
    return str(soup)

def process_definition_lists(html_content):
    """Convert definition-style paragraphs to structured lists"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for patterns like "Section 1. Definition" or specific resolution sections
    for p in soup.find_all('p'):
        text = p.get_text()
        
        # Only match specific patterns that are actual section definitions
        # - "Section N." at the start
        # - Single lowercase letter like "a." at the start  
        match = re.match(r'^(Section \d+|[a-z])\.\s+(.+)$', text)
        if match:
            term = match.group(1)
            definition = match.group(2)
            
            # Create a definition-style div
            div = soup.new_tag('div', attrs={'class': 'definition-item'})
            term_span = soup.new_tag('span', attrs={'class': 'definition-marker'})
            term_span.string = term + '.'
            div.append(term_span)
            div.append(' ' + definition)
            
            p.replace_with(div)
    
    return str(soup)

def process_parenthetical_lists_in_paragraphs(html_content):
    """Process lists with items like (a), (b), (c) that appear in paragraphs"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Pattern for alphabetical lists
    alpha_pattern = r'\([a-z]\)'
    
    for p in soup.find_all('p'):
        text = p.get_text()
        
        # Check if paragraph contains multiple parenthetical items
        if re.search(alpha_pattern, text, re.IGNORECASE):
            # Try to split into list items
            # This is complex as items might be inline or on separate lines
            lines = text.split('\n')
            
            list_items = []
            for line in lines:
                # Match items that start with (a), (b), etc.
                match = re.match(r'^\s*(\([a-z]\))\s+(.+)$', line.strip(), re.IGNORECASE)
                if match:
                    list_items.append({
                        'marker': match.group(1),
                        'content': match.group(2)
                    })
            
            # If we found multiple items, convert to a list
            if len(list_items) > 1:
                ol = soup.new_tag('ol', attrs={'class': 'alpha-list'})
                for item in list_items:
                    li = soup.new_tag('li')
                    marker_span = soup.new_tag('span', attrs={'class': 'custom-list-marker'})
                    marker_span.string = item['marker']
                    li.append(marker_span)
                    li.append(' ' + item['content'])
                    ol.append(li)
                
                p.replace_with(ol)
    
    return str(soup)

def process_mixed_roman_lists(html_content):
    """Process lists in <pre> blocks that have roman numerals"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Process all <pre> blocks
    for pre in soup.find_all('pre'):
        lines = pre.get_text().split('\n')
        
        # Check if this contains roman numerals
        has_roman = False
        list_items = []
        
        for line in lines:
            # Match lines that start with (i), (ii), etc. or i., ii., etc.
            match = re.match(r'^\s*(?:\(([ivx]+)\)|([ivx]+)\.)\s+(.+)$', line, re.IGNORECASE)
            if match:
                has_roman = True
                numeral = match.group(1) if match.group(1) else match.group(2)
                text = match.group(3)
                list_items.append({
                    'numeral': numeral,
                    'text': text,
                    'format': 'paren' if match.group(1) else 'dot'
                })
            elif line.strip() and list_items:
                # This might be a continuation of the previous item
                list_items[-1]['text'] += ' ' + line.strip()
        
        # If we found roman numerals, convert to a proper list
        if has_roman and list_items:
            ol = soup.new_tag('ol', attrs={'class': 'roman-list'})
            for item in list_items:
                li = soup.new_tag('li')
                marker = f"({item['numeral']})" if item['format'] == 'paren' else f"{item['numeral']}."
                marker_span = soup.new_tag('span', attrs={'class': 'roman-marker'})
                marker_span.string = marker
                li.append(marker_span)
                li.append(' ' + item['text'])
                ol.append(li)
            
            if ol.contents:
                pre.replace_with(ol)
    
    # Also look for ordered lists where items start with (i), (ii), etc.
    for ol in soup.find_all('ol'):
        has_roman = False
        for li in ol.find_all('li', recursive=False):
            # Get the text content
            text = li.get_text(strip=True)
            # Check if it starts with a roman numeral in parentheses
            if re.match(r'^\([ivx]+\)', text, re.IGNORECASE):
                has_roman = True
                break
        
        # If this list has roman numerals, add special class
        if has_roman:
            ol['class'] = ol.get('class', []) + ['roman-parenthetical-list']
    
    return str(soup)

def add_custom_css(html_content):
    """Add custom CSS for our special list styles"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # CSS is now in modular files - no need to inject inline styles
    # Styles are loaded via theme/css/main.css imports:
    # - components/form-fields.css
    # - layout/mdbook-overrides.css (custom lists)
    # - base/typography.css (document figures)
    return str(soup)

def process_form_fields(html_content):
    """Convert <!--BLANK--> markers to styled HTML elements."""
    # Pattern to match <!--BLANK--> or <!--BLANK:size--> markers
    blank_pattern = r'<!--BLANK(?::(\w+))?-->'
    
    def replace_blank(match):
        size = match.group(1) if match.group(1) else 'medium'
        return f'<span class="form-field-empty form-field-{size}" data-tooltip="This field was blank on the original document"></span>'
    
    # Replace all blank markers with styled spans
    html_content = re.sub(blank_pattern, replace_blank, html_content)
    
    # Pattern to match {{filled:text}} format
    filled_pattern = r'\{\{filled:([^}]+)\}\}'
    
    def replace_filled(match):
        text = match.group(1)
        return f'<span class="form-field-filled" data-tooltip="Field filled in on source doc">{text}</span>'
    
    # Replace all filled markers with styled spans
    html_content = re.sub(filled_pattern, replace_filled, html_content)
    
    return html_content

def process_html_file(filepath):
    """Process a single HTML file with all our custom transformations"""
    # Read the file
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply all processing functions
    content = process_form_fields(content)
    content = process_numbered_lists(content)
    content = process_roman_lists(content)
    content = process_parenthetical_lists_in_paragraphs(content)
    content = process_definition_lists(content)
    content = process_special_numbered_lists(content)
    content = process_mixed_roman_lists(content)
    content = add_custom_css(content)
    
    # Write the processed content back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def copy_assets():
    """Copy theme and images to book directory"""
    import shutil
    book_dir = Path("book")
    
    # Always remove and recopy theme directory
    if (book_dir / "theme").exists():
        shutil.rmtree(book_dir / "theme")
    if Path("theme").exists():
        shutil.copytree("theme", book_dir / "theme")
    
    # Always remove and recopy images directory  
    if (book_dir / "images").exists():
        shutil.rmtree(book_dir / "images")
    if Path("images").exists():
        shutil.copytree("images", book_dir / "images")

def main():
    """Process all HTML files in the book directory"""
    book_dir = Path("book")
    
    if not book_dir.exists():
        print("Error: book directory not found")
        sys.exit(1)
    
    # Copy assets first
    copy_assets()
    
    # Process all HTML files
    html_files = list(book_dir.glob("**/*.html"))
    
    print(f"Processing {len(html_files)} HTML files...")
    
    for filepath in html_files:
        try:
            process_html_file(filepath)
        except Exception as e:
            print(f"  ✗ Error processing {filepath.name}: {e}")
    
    print(f"\n✅ Custom list processing complete")

if __name__ == "__main__":
    main()