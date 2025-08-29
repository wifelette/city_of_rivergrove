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
            # Split by line breaks or semicolons
            lines = text.split('\n')
            
            # Check if we have multiple numbered items
            numbered_items = []
            for line in lines:
                match = re.match(r'^(\((\d+)\))\s+(.+)$', line.strip())
                if match:
                    numbered_items.append({
                        'marker': match.group(1),
                        'number': match.group(2),
                        'text': match.group(3)
                    })
            
            # If we found multiple items, convert to ordered list
            if len(numbered_items) > 1:
                ol = soup.new_tag('ol')
                for item in numbered_items:
                    li = soup.new_tag('li')
                    # Keep the original marker in a span for styling
                    marker_span = soup.new_tag('span', attrs={'class': 'custom-list-marker'})
                    marker_span.string = item['marker']
                    li.append(marker_span)
                    li.append(' ' + item['text'])
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
                    
                    # Add the content with the number as a prefix
                    num_span = soup.new_tag('span', attrs={'class': 'special-list-number'})
                    num_span.string = item['full_num'] + ' '
                    li.append(num_span)
                    
                    # Add the rest of the content
                    content_span = soup.new_tag('span')
                    content_span.string = item['content']
                    li.append(content_span)
                    ol.append(li)
                
                # Replace the first paragraph with our new list
                list_items[0]['element'].replace_with(ol)
                
                # Remove the remaining paragraphs that were part of the list
                for item in list_items[1:]:
                    item['element'].extract()
    
    return str(soup)

def process_letter_lists(html_content):
    """Convert (a), (b) style lists to custom styled divs"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Process definition-style letter lists
    for p in soup.find_all('p'):
        text = p.get_text()
        
        # Check for letter markers at start of paragraph
        match = re.match(r'^(\(([a-z])\))\s+(.+)$', text.strip(), re.IGNORECASE)
        if match:
            # Create a custom div for definition items
            div = soup.new_tag('div', attrs={'class': 'definition-item'})
            
            # Add the marker
            marker_span = soup.new_tag('span', attrs={'class': 'definition-marker'})
            marker_span.string = match.group(1)
            div.append(marker_span)
            
            # Add the content
            content_span = soup.new_tag('span', attrs={'class': 'definition-content'})
            content_span.string = ' ' + match.group(3)
            div.append(content_span)
            
            p.replace_with(div)
    
    return str(soup)

def process_roman_lists(html_content):
    """Convert (i), (ii) style lists to custom HTML"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for indented roman numerals in code blocks or preformatted text
    for pre in soup.find_all(['pre', 'code']):
        text = pre.get_text()
        
        # Check if this contains roman numeral lists
        if re.search(r'\([ivx]+\)', text, re.IGNORECASE):
            lines = text.split('\n')
            
            # Create a custom list
            ol = soup.new_tag('ol', attrs={'class': 'roman-list'})
            
            for line in lines:
                # Match indented roman numerals
                match = re.match(r'^(\s*)\(([ivx]+)\)\s+(.+)$', line, re.IGNORECASE)
                if match:
                    li = soup.new_tag('li')
                    marker_span = soup.new_tag('span', attrs={'class': 'roman-marker'})
                    marker_span.string = f"({match.group(2)})"
                    li.append(marker_span)
                    li.append(' ' + match.group(3))
                    ol.append(li)
            
            if ol.contents:
                pre.replace_with(ol)
    
    return str(soup)

def add_custom_css(html_content):
    """Add custom CSS for our special list styles"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check if we've already added our custom CSS
    if soup.find('style', id='custom-list-styles'):
        return str(soup)
    
    # Add custom CSS to head
    head = soup.find('head')
    if head:
        style = soup.new_tag('style', id='custom-list-styles')
        style.string = """
        /* Custom list styles for legal documents */
        .custom-list-marker {
            font-weight: bold;
            margin-right: 0.5em;
        }
        
        .definition-item {
            margin: 1em 0;
        }
        
        .definition-marker {
            font-weight: bold;
            margin-right: 0.5em;
        }
        
        .roman-list {
            list-style: none;
            padding-left: 2em;
        }
        
        .roman-list li {
            margin: 0.5em 0;
        }
        
        .roman-marker {
            font-weight: normal;
            margin-right: 0.5em;
        }
        
        /* Special list that starts at non-standard number (e.g., 1.4) */
        .special-start-list {
            list-style: none !important;
            padding-left: 2em;
            counter-reset: none !important;
        }
        
        .special-start-list li {
            margin: 0.5em 0;
            position: relative;
            list-style: none !important;
        }
        
        .special-start-list li::before {
            content: none !important;
        }
        
        .special-list-number {
            font-weight: bold;
            margin-right: 0.5em;
            display: inline-block;
            min-width: 2em;
        }
        
        /* Override mdBook's list styling for our custom lists */
        ol:has(.custom-list-marker) {
            list-style: none;
            counter-reset: none;
        }
        
        ol:has(.custom-list-marker) li::before {
            content: none;
        }
        
        ol.special-start-list li::before {
            content: none;
        }
        
        /* Form field styles for legal documents */
        .form-field-empty {
            display: inline-block;
            border-bottom: 1px solid #999;
            margin: 0 2px;
            cursor: default;
            vertical-align: baseline;
            height: 1em;
            position: relative;
        }
        
        .form-field-empty:hover {
            background-color: #f0f0f0;
            border-bottom-color: #666;
        }
        
        /* Add a visual indicator for blank fields */
        .form-field-empty::after {
            content: attr(data-tooltip);
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease-in;
            transition-delay: 0.5s;
            margin-top: 4px;
            z-index: 100000;
        }
        
        .form-field-empty:hover::after {
            opacity: 1;
        }
        
        .form-field-short {
            min-width: 60px;
        }
        
        .form-field-medium {
            min-width: 120px;
        }
        
        .form-field-long {
            min-width: 200px;
        }
        
        .form-field-filled {
            display: inline-block;
            padding: 2px 4px 4px 4px;
            background-color: #e3f2fd;
            border-bottom: 2px solid #1976d2;
            color: #000;
            font-weight: 600;
            cursor: default !important;
            position: relative;
            margin: 0 3px;
            vertical-align: baseline;
            line-height: 1.4;
        }
        
        /* Ensure tooltips appear above other elements */
        .form-field-filled:hover,
        .form-field-empty:hover {
            z-index: 1000;
        }
        
        /* Force no help cursor for form fields and remove any title tooltips */
        .form-field-filled,
        .form-field-filled:hover,
        .form-field-empty,
        .form-field-empty:hover {
            cursor: default !important;
        }
        
        /* Hide any native browser tooltips */
        .form-field-filled[title],
        .form-field-empty[title] {
            cursor: default !important;
        }
        
        .form-field-filled[title]:hover::before,
        .form-field-empty[title]:hover::before {
            content: '' !important;
        }
        
        .form-field-filled:hover {
            background-color: #bbdefb;
            border-bottom-color: #0d47a1;
        }
        
        /* CSS tooltip for filled fields */
        .form-field-filled::after {
            content: attr(data-tooltip);
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            white-space: nowrap;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease-in;
            transition-delay: 0.5s;
            margin-top: 4px;
            z-index: 100000;
        }
        
        .form-field-filled:hover::after {
            opacity: 1;
        }
        
        /* Special positioning for tooltips in headings to avoid clipping */
        h1 .form-field-filled::after,
        h2 .form-field-filled::after,
        h3 .form-field-filled::after {
            top: 100%;
            bottom: auto;
            margin-top: 8px;
            margin-bottom: 0;
            font-weight: normal;
            font-size: 12px;
        }
        
        /* Same for empty field tooltips in headings */
        h1 .form-field-empty::after,
        h2 .form-field-empty::after,
        h3 .form-field-empty::after {
            font-weight: normal;
            font-size: 12px;
        }
        
        /* Special styling for form fields in headings */
        h1 .form-field-filled, 
        h2 .form-field-filled, 
        h3 .form-field-filled {
            font-size: inherit;
            font-weight: inherit;
            vertical-align: baseline;
        }
        
        h1 .form-field-empty, 
        h2 .form-field-empty, 
        h3 .form-field-empty {
            vertical-align: baseline;
            height: 0.8em;
            margin-bottom: -0.1em;
        }
        
        /* Document figure styles for inline images */
        .document-figure {
            margin: 2em auto;
            text-align: center;
            max-width: 100%;
            page-break-inside: avoid;
        }
        
        .document-figure img {
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            padding: 10px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .document-figure figcaption {
            margin-top: 1em;
            font-style: italic;
            color: #666;
            font-size: 0.9em;
            line-height: 1.4;
        }
        
        /* Responsive image sizing */
        @media screen and (min-width: 768px) {
            .document-figure {
                max-width: 80%;
            }
        }
        
        @media print {
            .document-figure {
                page-break-inside: avoid;
                max-width: 100%;
            }
            
            .document-figure img {
                max-width: 100%;
                box-shadow: none;
            }
        }
        """
        head.append(style)
    
    return str(soup)

def process_form_fields(html_content):
    """Convert <!--BLANK--> markers to styled HTML elements."""
    # Pattern to match <!--BLANK--> or <!--BLANK:size--> markers
    blank_pattern = r'<!--BLANK(?::(\w+))?-->'
    
    def replace_blank(match):
        size = match.group(1) if match.group(1) else 'medium'
        size_class = f'form-field-{size}'
        return f'<span class="form-field-empty {size_class}" data-tooltip="Field left blank in source doc"></span>'
    
    # Replace all blank markers
    html_content = re.sub(blank_pattern, replace_blank, html_content)
    
    # Pattern to match <!--FILLED: content--> markers (if manually added)
    filled_pattern = r'<!--FILLED:\s*([^-]+)-->'
    
    def replace_filled(match):
        content = match.group(1)
        return f'<span class="form-field-filled" data-tooltip="Field filled in on source doc">{content}</span>'
    
    # Replace all filled markers
    html_content = re.sub(filled_pattern, replace_filled, html_content)
    
    return html_content

def process_html_file(filepath):
    """Process a single HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply all processors
    content = process_special_numbered_lists(content)  # Process special lists first
    content = process_numbered_lists(content)
    content = process_letter_lists(content)
    content = process_roman_lists(content)
    content = add_custom_css(content)
    
    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✓ Processed {filepath.name}")

def main():
    """Process all HTML files in the book directory"""
    book_dir = Path("book")
    
    if not book_dir.exists():
        print("Error: book directory not found")
        sys.exit(1)
    
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