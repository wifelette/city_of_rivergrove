#!/usr/bin/env python3
"""
Fix numbered lists that use (1), (2) format to proper markdown 1., 2. format
Also fixes indented lists with (i), (ii), etc.
"""

import re
import sys
from pathlib import Path

def fix_numbered_lists(content):
    """Convert (1), (2) style lists to proper markdown format"""
    lines = content.split('\n')
    modified_lines = []
    
    for line in lines:
        # Fix main numbered lists (1), (2), etc.
        # Match lines that start with (number) 
        match = re.match(r'^(\()(\d+)(\))\s+(.+)$', line)
        if match:
            number = match.group(2)
            text = match.group(4)
            modified_lines.append(f"{number}. {text}")
            continue
        
        # Fix root-level letter lists (a), (b), (c), etc. - these are definitions
        # Match lines that start with (letter) at the beginning
        match = re.match(r'^(\()([a-z]+)(\))\s+(.+)$', line, re.IGNORECASE)
        if match:
            letter = match.group(2)
            text = match.group(4)
            # Convert single letters to numbered list (a=1, b=2, etc.)
            if len(letter) == 1:
                # Keep as paragraph with bold letter for definition lists
                modified_lines.append(f"**({letter})** {text}")
            else:
                # Multi-letter like (aa) - keep as-is
                modified_lines.append(line)
            continue
            
        # Fix indented numbered lists (1), (2), etc. under letter items
        # These should become nested lists
        match = re.match(r'^(    )\((\d+)\)\s+(.+)$', line)
        if match:
            indent = match.group(1)
            number = match.group(2)
            text = match.group(3)
            # Convert to numbered list with proper indentation
            modified_lines.append(f"{indent}{number}. {text}")
            continue
            
        # Fix indented roman numeral lists (i), (ii), etc.
        # These should become indented markdown lists
        match = re.match(r'^(    )\(([ivx]+)\)\s+(.+)$', line, re.IGNORECASE)
        if match:
            indent = match.group(1)
            text = match.group(3)
            # Convert to bullet list since markdown doesn't support roman numerals
            modified_lines.append(f"{indent}- {text}")
            continue
            
        # Keep the line as-is
        modified_lines.append(line)
    
    return '\n'.join(modified_lines)

def process_file(filepath):
    """Process a single file"""
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the lists
    fixed_content = fix_numbered_lists(content)
    
    # Check if anything changed
    if fixed_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        # Count changes
        original_matches = len(re.findall(r'^\(\d+\)', content, re.MULTILINE))
        original_roman = len(re.findall(r'^    \([ivx]+\)', content, re.MULTILINE | re.IGNORECASE))
        
        print(f"  ✓ Fixed {original_matches} numbered lists and {original_roman} indented lists")
        return True
    else:
        print(f"  No changes needed")
        return False

def main():
    """Main function"""
    # Files to process
    files_to_fix = [
        "Ordinances/1987-Ord-#52-Flood.md",
        "Ordinances/1989-Ord-#54-89-C-Land-Development.md"
    ]
    
    total_fixed = 0
    for filepath in files_to_fix:
        if Path(filepath).exists():
            if process_file(filepath):
                total_fixed += 1
        else:
            print(f"Warning: {filepath} not found")
    
    print(f"\n✅ Fixed {total_fixed} files")
    
if __name__ == "__main__":
    main()