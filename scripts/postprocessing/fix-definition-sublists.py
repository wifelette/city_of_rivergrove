#!/usr/bin/env python3
"""
Fix nested lists under definition items in ordinances.
Converts indented (1), (2), etc. under letter definitions to proper markdown nested lists.
"""

import re
import sys
from pathlib import Path

def fix_definition_sublists(content):
    """Convert indented (1), (2) style lists under definitions to proper markdown format"""
    lines = content.split('\n')
    modified_lines = []
    in_definition = False
    
    for i, line in enumerate(lines):
        # Check if this is a letter definition line (a), (b), etc.
        letter_match = re.match(r'^\(([a-z]+)\)\s+(.+)$', line, re.IGNORECASE)
        if letter_match:
            in_definition = True
            modified_lines.append(line)  # Keep definition as-is
            continue
            
        # Check if this is an indented numbered item under a definition
        indented_match = re.match(r'^(    )\((\d+)\)\s+(.+)$', line)
        if indented_match and in_definition:
            indent = indented_match.group(1)
            number = indented_match.group(2)
            text = indented_match.group(3)
            # Convert to a proper nested numbered list
            modified_lines.append(f"{indent}{number}. {text}")
            continue
        
        # Check if we're leaving the definition (non-indented, non-list line)
        if line and not line.startswith('    ') and not re.match(r'^\(([a-z]+)\)', line, re.IGNORECASE):
            in_definition = False
            
        # Keep the line as-is
        modified_lines.append(line)
    
    return '\n'.join(modified_lines)

def process_file(filepath):
    """Process a single file"""
    print(f"Processing {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the nested lists
    fixed_content = fix_definition_sublists(content)
    
    # Check if anything changed
    if fixed_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        # Count changes
        original_matches = len(re.findall(r'^    \(\d+\)', content, re.MULTILINE))
        
        print(f"  ✓ Fixed {original_matches} nested definition sublists")
        return True
    else:
        print(f"  No changes needed")
        return False

def main():
    """Main function"""
    # Process all ordinance files
    ordinance_files = list(Path("Ordinances").glob("*.md"))
    
    total_fixed = 0
    for filepath in ordinance_files:
        if process_file(filepath):
            total_fixed += 1
    
    print(f"\n✅ Fixed {total_fixed} files with nested definition sublists")
    
if __name__ == "__main__":
    main()