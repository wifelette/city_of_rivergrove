#!/usr/bin/python3
"""
Complex List Preprocessor for City of Rivergrove Documents

This preprocessor handles complex nested list structures that mdBook has trouble parsing correctly.
It runs BEFORE mdBook conversion to ensure lists are properly formatted and maintain their context.

Key features:
1. Detects list sections and preserves their boundaries
2. Converts (a), (b) style to proper markdown lists with preserved markers
3. Handles nested numeric lists under alphabetic items
4. Ensures proper spacing after headings to prevent list merging
5. Adds HTML comments to preserve list context through mdBook processing

Author: Claude
Date: 2025
"""

import re
import sys
from pathlib import Path

class ListSection:
    """Represents a section of list items with metadata"""
    def __init__(self, start_line, heading_before=None):
        self.start_line = start_line
        self.end_line = None
        self.items = []
        self.heading_before = heading_before
        self.intro_text = None

class ListItem:
    """Represents a single list item with potential nested items"""
    def __init__(self, marker, content, line_num, indent_level=0):
        self.marker = marker  # e.g., '(a)', '(1)', etc.
        self.content = content
        self.line_num = line_num
        self.indent_level = indent_level
        self.nested_items = []
        self.marker_type = self.detect_type()

    def detect_type(self):
        """Detect if this is alpha, numeric, or roman numeral"""
        inner = self.marker.strip('()')
        if inner.isdigit():
            return 'numeric'
        elif inner.isalpha():
            return 'alpha'
        else:
            # Could be roman numeral
            return 'roman'

def find_list_sections(lines):
    """
    Find all list sections in the document.
    Returns a list of ListSection objects.
    """
    sections = []
    current_section = None
    last_heading = None
    last_heading_line = -1

    # Patterns for different list markers
    alpha_pattern = re.compile(r'^(\([a-z]\))\s+(.+)$', re.IGNORECASE)
    numeric_pattern = re.compile(r'^(\(\d+\))\s+(.+)$')
    indented_numeric_pattern = re.compile(r'^(    )(\(\d+\))\s+(.+)$')
    heading_pattern = re.compile(r'^#+\s+')

    for i, line in enumerate(lines):
        # Track headings
        if heading_pattern.match(line):
            last_heading = line.strip()
            last_heading_line = i
            # If we had an open section, close it
            if current_section:
                current_section.end_line = i - 1
                sections.append(current_section)
                current_section = None
            continue

        # Check for list items
        is_list_item = False
        marker = None
        content = None
        indent = 0

        # Check for alpha list items
        match = alpha_pattern.match(line)
        if match:
            is_list_item = True
            marker = match.group(1)
            content = match.group(2)

        # Check for numeric list items
        if not is_list_item:
            match = numeric_pattern.match(line)
            if match:
                is_list_item = True
                marker = match.group(1)
                content = match.group(2)

        # Check for indented numeric list items
        if not is_list_item:
            match = indented_numeric_pattern.match(line)
            if match:
                is_list_item = True
                marker = match.group(2)
                content = match.group(3)
                indent = 1

        if is_list_item:
            # Start a new section if needed
            if not current_section:
                # Check if this is right after a heading (within 3 lines)
                if last_heading and (i - last_heading_line) <= 3:
                    current_section = ListSection(i, heading_before=last_heading)
                else:
                    current_section = ListSection(i)

                # Capture any intro text between heading and first list item
                if last_heading_line >= 0 and i > last_heading_line + 1:
                    intro_lines = []
                    for j in range(last_heading_line + 1, i):
                        if lines[j].strip():
                            intro_lines.append(lines[j])
                    if intro_lines:
                        current_section.intro_text = '\n'.join(intro_lines)

            # Add item to current section
            item = ListItem(marker, content, i, indent)

            # Handle nesting - if this is indented and we have items
            if indent > 0 and current_section.items:
                # Add to the last non-indented item
                for parent in reversed(current_section.items):
                    if parent.indent_level < indent:
                        parent.nested_items.append(item)
                        break
            else:
                current_section.items.append(item)

        # Check if we should close the current section
        elif current_section and line.strip():
            # Non-empty, non-list line - close section
            # Unless it's a continuation of the previous line
            if not lines[i-1].rstrip().endswith(',') and not lines[i-1].rstrip().endswith(';'):
                current_section.end_line = i - 1
                sections.append(current_section)
                current_section = None

    # Close any remaining section
    if current_section:
        current_section.end_line = len(lines) - 1
        sections.append(current_section)

    return sections

def convert_to_markdown_list(section, lines):
    """
    Convert a ListSection to proper markdown list format.
    Returns the converted lines.
    """
    output = []

    # Add a blank line before the list if it's right after a heading
    if section.heading_before:
        # Ensure blank line after heading
        output.append('')

    # Add intro text if present
    if section.intro_text:
        output.append(section.intro_text)
        output.append('')  # Blank line before list

    # Add list boundary marker comment
    output.append(f'<!-- LIST_SECTION_START type="{section.items[0].marker_type if section.items else "unknown"}" -->')

    # Process each item
    for item in section.items:
        # For alpha and numeric items, preserve the marker in the content
        # but use markdown list syntax
        if item.marker_type == 'alpha':
            # Use dash for alpha lists, preserve marker in content
            output.append(f'- {item.marker} {item.content}')
        elif item.marker_type == 'numeric':
            # Use proper numbered list
            num = item.marker.strip('()')
            output.append(f'{num}. {item.content}')

        # Add nested items
        if item.nested_items:
            for nested in item.nested_items:
                if nested.marker_type == 'numeric':
                    num = nested.marker.strip('()')
                    output.append(f'    {num}. {nested.content}')
                else:
                    output.append(f'    - {nested.marker} {nested.content}')

    # Add list boundary marker comment
    output.append('<!-- LIST_SECTION_END -->')
    output.append('')  # Blank line after list

    return output

def process_document(content):
    """
    Process an entire document to fix complex list issues.
    """
    lines = content.split('\n')

    # Find all list sections
    sections = find_list_sections(lines)

    if not sections:
        return content  # No changes needed

    # Build the output, replacing list sections
    output = []
    last_end = -1

    for section in sections:
        # Add everything before this section
        if section.start_line > last_end + 1:
            # Adjust for intro text that we'll include with the list
            start = last_end + 1
            if section.intro_text:
                # Skip lines that are part of intro text
                intro_lines = section.intro_text.split('\n')
                while start < section.start_line:
                    if lines[start].strip() in [line.strip() for line in intro_lines]:
                        start += 1
                    else:
                        break

            # Add non-list lines
            for i in range(last_end + 1, start):
                output.append(lines[i])

            # Skip the original intro text lines (they'll be added with the list)
            if section.intro_text:
                # Skip ahead to the actual list start
                for i in range(start, section.start_line):
                    if lines[i].strip() not in [line.strip() for line in intro_lines]:
                        output.append(lines[i])

        # Convert and add the list section
        converted = convert_to_markdown_list(section, lines)
        output.extend(converted)

        last_end = section.end_line

    # Add everything after the last section
    if last_end < len(lines) - 1:
        for i in range(last_end + 1, len(lines)):
            output.append(lines[i])

    return '\n'.join(output)

def process_file(file_path):
    """Process a single file for complex list issues."""
    path = Path(file_path)

    if not path.exists():
        print(f"Error: File not found: {file_path}")
        return False

    try:
        content = path.read_text(encoding='utf-8')
        original_content = content

        # Process the document
        content = process_document(content)

        # Only write if changes were made
        if content != original_content:
            # Create backup
            backup_path = path.with_suffix('.bak')
            backup_path.write_text(original_content, encoding='utf-8')

            # Write processed content
            path.write_text(content, encoding='utf-8')
            print(f"✓ Processed complex lists in: {path.name}")

            # Count the number of list sections processed
            sections_added = content.count('<!-- LIST_SECTION_START')
            print(f"  Added {sections_added} list section markers")

            return True
        else:
            print(f"  No complex list processing needed: {path.name}")
            return False

    except Exception as e:
        print(f"Error processing {path.name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 complex-list-preprocessor.py <file_path> [file_path2 ...]")
        print("Example: python3 complex-list-preprocessor.py src/ordinances/1989-Ord-54-89C-Land-Development.md")
        sys.exit(1)

    success_count = 0
    for file_path in sys.argv[1:]:
        if process_file(file_path):
            success_count += 1

    print(f"\n✅ Processed {success_count} file(s) with complex list formatting")

if __name__ == "__main__":
    main()