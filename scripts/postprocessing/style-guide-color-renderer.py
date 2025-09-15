#!/usr/bin/env python3
"""
Style Guide Color Renderer
Renders hex color codes as colored previews in the Style Guide ONLY.
Avoids false positives like "Ordinance #345" or "Resolution #301".
"""

import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

def is_style_guide_file(filepath):
    """Check if this is the style guide file"""
    filename = filepath.name.lower()
    # Check if this is a style guide file
    return 'style-guide' in filename or 'style_guide' in filename

def render_color_codes(soup, is_style_guide):
    """
    Render hex color codes as colored previews.
    Only applies to Style Guide files.
    Avoids document references like "Ordinance #345".
    """
    if not is_style_guide:
        return soup

    # Pattern for hex colors (3 or 6 digits)
    # Negative lookbehind to avoid matching after Ordinance/Resolution/Interpretation
    hex_pattern = re.compile(
        r'(?<!Ordinance |Resolution |Interpretation |Ord |Res |Int )'
        r'(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})(?![0-9a-fA-F])'
    )

    # Process all text nodes
    for element in soup.find_all(text=True):
        parent = element.parent

        # Skip if already processed or in a code block
        if parent.name in ['code', 'pre', 'script', 'style']:
            continue

        text = str(element)

        # Check if text contains potential hex codes
        if '#' not in text:
            continue

        # Replace hex codes with styled spans
        new_html = text
        for match in hex_pattern.finditer(text):
            color = match.group(1)
            # Create a span with inline style for color preview
            color_preview = (
                f'<span class="color-preview" '
                f'style="background-color: {color}; '
                f'padding: 2px 6px; '
                f'border-radius: 3px; '
                f'color: white; '
                f'font-family: monospace; '
                f'font-size: 0.9em; '
                f'display: inline-block; '
                f'margin: 0 2px;">'
                f'{color}</span>'
            )
            new_html = new_html.replace(color, color_preview)

        # Only replace if we made changes
        if new_html != text:
            new_element = BeautifulSoup(new_html, 'html.parser')
            element.replace_with(new_element)

    return soup

def process_file(filepath):
    """Process a single HTML file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        soup = BeautifulSoup(content, 'html.parser')

        # Check if this is the style guide
        is_style_guide = is_style_guide_file(filepath)

        # Apply color rendering
        soup = render_color_codes(soup, is_style_guide)

        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))

        if is_style_guide:
            print(f"✓ Processed style guide with color rendering: {filepath.name}")

        return True

    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: style-guide-color-renderer.py <file.html>")
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    success = process_file(filepath)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()