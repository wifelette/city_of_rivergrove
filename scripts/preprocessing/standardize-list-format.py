#!/usr/bin/env python3
"""
Standardize list format in markdown files to prepare them for proper HTML processing.
This runs BEFORE mdBook converts markdown to HTML.

Key changes from the old fix-numbered-lists.py:
- Preserves (a), (b) notation instead of making it bold
- Only converts (1), (2) to proper numbered lists 1., 2.
- This allows postprocessors to detect and style alpha markers properly
"""

import re
import sys
from pathlib import Path

def standardize_lists(content):
    """Standardize list formats in markdown"""
    lines = content.split('\n')
    modified_lines = []
    
    for line in lines:
        # Convert (1), (2) style lists to proper markdown numbered lists
        # These should become standard ordered lists
        match = re.match(r'^(\()(\d+)(\))\s+(.+)$', line)
        if match:
            number = match.group(2)
            text = match.group(4)
            modified_lines.append(f"{number}. {text}")
            continue
        
        # PRESERVE (a), (b) style lists as-is
        # Don't convert to bold - let postprocessor handle styling
        # This is the KEY CHANGE - we keep these as plain text
        # so the postprocessor can detect and wrap them properly
        
        # Fix indented numbered lists (1), (2), etc. under letter items
        # These should become nested numbered lists
        match = re.match(r'^(    )\((\d+)\)\s+(.+)$', line)
        if match:
            indent = match.group(1)
            number = match.group(2)
            text = match.group(3)
            # Convert to numbered list with proper indentation
            modified_lines.append(f"{indent}{number}. {text}")
            continue
            
        # Convert indented roman numeral lists (i), (ii), etc. to bullet lists
        # Markdown doesn't natively support roman numerals
        match = re.match(r'^(    )\(([ivx]+)\)\s+(.+)$', line, re.IGNORECASE)
        if match:
            indent = match.group(1)
            text = match.group(3)
            # Convert to bullet list since markdown doesn't support roman numerals
            # The postprocessor will detect and style these appropriately
            modified_lines.append(f"{indent}- {text}")
            continue
            
        # Keep the line as-is
        modified_lines.append(line)
    
    return '\n'.join(modified_lines)

def process_file(filepath):
    """Process a single file"""
    print(f"  Standardizing lists in {filepath.name}...")
    
    # Skip the test document - it needs to preserve all list formats for testing
    if 'list-test-comprehensive' in filepath.name:
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Standardize the lists
    fixed_content = standardize_lists(content)
    
    # Check if anything changed
    if fixed_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        # Count changes
        original_numeric = len(re.findall(r'^\(\d+\)', content, re.MULTILINE))
        original_indented_numeric = len(re.findall(r'^    \(\d+\)', content, re.MULTILINE))
        original_roman = len(re.findall(r'^    \([ivx]+\)', content, re.MULTILINE | re.IGNORECASE))
        
        changes = []
        if original_numeric > 0:
            changes.append(f"{original_numeric} numbered lists")
        if original_indented_numeric > 0:
            changes.append(f"{original_indented_numeric} indented numbered lists")
        if original_roman > 0:
            changes.append(f"{original_roman} roman numeral lists")
            
        if changes:
            print(f"    ✓ Standardized {', '.join(changes)}")
        return True
    else:
        return False

def process_directory(directory_path, pattern="*.md"):
    """Process all markdown files in a directory"""
    dir_path = Path(directory_path)
    if not dir_path.exists():
        print(f"  Directory {directory_path} not found")
        return 0
    
    files_processed = 0
    for filepath in dir_path.glob(pattern):
        if process_file(filepath):
            files_processed += 1
    
    return files_processed

def main():
    """Main function - process files in src directories"""
    # Process all markdown files in src directories
    directories = [
        "src/ordinances",
        "src/resolutions", 
        "src/interpretations",
        "src/other",
        "src/agendas",
        "src/minutes",
        "src/transcripts"
    ]
    
    total_processed = 0
    for directory in directories:
        if Path(directory).exists():
            processed = process_directory(directory)
            if processed > 0:
                total_processed += processed
    
    if total_processed > 0:
        print(f"  ✓ Standardized lists in {total_processed} files")
    
if __name__ == "__main__":
    main()