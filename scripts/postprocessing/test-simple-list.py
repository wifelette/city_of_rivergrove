#!/usr/bin/env python3
"""Simple test to verify list processing works correctly."""

from bs4 import BeautifulSoup
import re

# Test HTML with various list formats
test_html = """
<ul>
<li>(a) A simple list item with letter marker</li>
<li>(b) Another list item</li>
<li>(1) A numbered item</li>
<li>Regular bullet item</li>
</ul>

<ol>
<li>(i) Roman numeral item</li>
<li>(ii) Another roman</li>
</ol>

<p>(a) This is a standalone paragraph with letter marker that might be a definition.</p>
"""

def process_lists(html):
    """Simple processor that just bolds markers in lists."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Process list items
    for li in soup.find_all('li'):
        text = li.get_text().strip()
        # Check for markers at the start
        match = re.match(r'^(\([a-z0-9ivx]+\))\s+(.+)$', text, re.IGNORECASE)
        if match:
            marker = match.group(1)
            content = match.group(2)
            
            # Clear and rebuild with bold marker
            li.clear()
            strong = soup.new_tag('strong')
            strong.string = marker
            li.append(strong)
            li.append(' ' + content)
    
    return str(soup.prettify())

print("Original HTML:")
print(test_html)
print("\n" + "="*60 + "\n")
print("Processed HTML:")
print(process_lists(test_html))