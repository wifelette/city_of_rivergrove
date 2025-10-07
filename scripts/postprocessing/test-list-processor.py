#!/usr/bin/env python3
"""
Test script for the simplified list processor.
Tests on a few complex examples before rolling out everywhere.
"""

import re
from bs4 import BeautifulSoup
from pathlib import Path
import sys

def simplified_letter_list_processor(html_content):
    """
    Simplified processor that:
    1. Removes any special styling divs from items inside lists
    2. Only adds minimal formatting (bold) to letter markers
    3. Doesn't add blockquote-like backgrounds or borders
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # First pass: Remove ALL definition-item and letter-item divs from list items
    # These should never have special styling when already in a list
    for li in soup.find_all('li'):
        # Look for any divs with these classes
        for div in li.find_all('div', class_=['definition-item', 'letter-item']):
            # Extract just the text content
            text_content = div.get_text()
            # Replace the div with plain text
            div.replace_with(text_content)
        
        # Check if the li text starts with (a), (b), etc. and make the marker bold
        # Get the first text node
        first_text = None
        for content in li.contents:
            if isinstance(content, str) and content.strip():
                first_text = content
                break
        
        if first_text:
            # Look for letter/number markers at the start
            match = re.match(r'^(\([a-z0-9]+\))\s+(.+)$', first_text.strip(), re.IGNORECASE)
            if match:
                # Create a bold element for the marker
                marker = soup.new_tag('strong')
                marker.string = match.group(1)
                
                # Find and replace the text node
                for i, content in enumerate(li.contents):
                    if isinstance(content, str) and content.strip().startswith(match.group(1)):
                        # Replace this text node with marker + remaining text
                        li.contents[i] = marker
                        li.insert(i + 1, ' ' + match.group(2))
                        break
    
    # Second pass: For standalone paragraphs with (a), (b) - just bold the marker
    # Don't add any background or border styling
    for p in soup.find_all('p'):
        # Skip if inside a list or blockquote
        if p.find_parent(['li', 'ul', 'ol', 'blockquote']):
            continue
        
        # Check if this paragraph starts with a letter marker
        text = p.get_text()
        match = re.match(r'^(\([a-z]\))\s+(.+)$', text.strip(), re.IGNORECASE)
        if match:
            # Just make the marker bold, no special divs
            marker_span = soup.new_tag('strong')
            marker_span.string = match.group(1)
            
            # Clear and rebuild the paragraph
            p.clear()
            p.append(marker_span)
            p.append(' ' + match.group(2))
    
    return str(soup)

def test_file(filepath):
    """Test the processor on a single file and show before/after."""
    print(f"\n{'='*60}")
    print(f"Testing: {filepath.name}")
    print('='*60)
    
    # Read the HTML file
    with open(filepath, 'r', encoding='utf-8') as f:
        original_html = f.read()
    
    # Find sections with letter lists
    soup = BeautifulSoup(original_html, 'html.parser')
    
    # Look for list items with (a), (b), (c) patterns
    found_examples = False
    for li in soup.find_all('li'):
        text = li.get_text()
        if text.strip().startswith('(') and ')' in text[:4]:
            if not found_examples:
                print("\n--- Found letter-numbered list items ---")
                found_examples = True
            
            # Get the parent list for context
            parent = li.parent
            if parent and parent.name in ['ul', 'ol']:
                # Show a few items from this list
                print(f"\nOriginal list item:")
                print(f"  {str(li)[:200]}")
                
                # Process just this item
                processed = simplified_letter_list_processor(str(li))
                print(f"Processed:")
                print(f"  {processed[:200]}")
                
                # Only show first 3 examples per file
                if parent.find_all('li').index(li) >= 2:
                    break
    
    if not found_examples:
        print("No letter-numbered lists found in this file")
    
    return True

def main():
    """Test on selected complex files."""
    
    # Test files with complex lists
    test_files = [
        '/Users/leahsilber/Github/city_of_rivergrove/book/ordinances/2003-Ord-73-2003A-Conditional-Use-Provisions.html',
        '/Users/leahsilber/Github/city_of_rivergrove/book/ordinances/1989-Ord-54-89C-Land-Development.html',
        '/Users/leahsilber/Github/city_of_rivergrove/book/ordinances/2004-Ord-74-2004-Tree-Cutting-Amendment.html',
    ]
    
    print("Testing simplified list processor on complex examples...")
    print("This will show before/after for letter-numbered lists")
    
    for filepath in test_files:
        path = Path(filepath)
        if path.exists():
            test_file(path)
        else:
            print(f"Warning: {filepath} not found")
    
    print("\n" + "="*60)
    print("Test complete. Review the output above.")
    print("If the results look good, we can apply this to all files.")
    print("="*60)

if __name__ == "__main__":
    main()