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
        
        /* Override mdBook's list styling for our custom lists */
        ol:has(.custom-list-marker) {
            list-style: none;
            counter-reset: none;
        }
        
        ol:has(.custom-list-marker) li::before {
            content: none;
        }
        """
        head.append(style)
    
    return str(soup)

def process_html_file(filepath):
    """Process a single HTML file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Apply all processors
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