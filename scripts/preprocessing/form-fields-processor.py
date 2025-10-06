#!/usr/bin/python3
"""
Form fields processor that converts blank field patterns (underscores)
to a special markdown notation that will be processed during HTML generation.

Converts various underscore patterns to [BLANK] notation.
"""

import re
import sys
from pathlib import Path

def process_unfilled_blanks(content):
    """
    Convert unfilled blank fields (underscores) to markdown notation.
    Patterns like \_\_\_ or \_\_\_\_ or even __ become [BLANK] markers.
    This is legacy support - new documents should use {{filled:}} syntax.
    """
    # Multiple patterns to catch different underscore variations
    patterns = [
        # Escaped underscores: \_\_\_ or \_\_\_\_
        (r'(\\_){2,}', lambda m: determine_blank_size(len(m.group(0)) // 2)),
        # Regular underscores with spaces: ___ or ____
        (r'(?<!\w)_{2,}(?!\w)', lambda m: determine_blank_size(len(m.group(0)))),
        # Asterisk + underscores pattern: **\_\_\_**
        (r'\*\*(\\_)+\*\*', lambda m: '<!--BLANK-->'),
        # Multiple asterisks with underscores: ********\_\_\_\_********
        (r'\*{2,}(\\_)+\*{2,}', lambda m: '<!--BLANK-->'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def process_filled_fields(content):
    """
    Convert filled field markers to special notation.
    
    Syntax:
    - {{filled:}} -> [BLANK] (empty field)
    - {{filled:text}} -> [FILLED:text] (filled field)
    - {{signature}} -> [SIGNATURE] (signature mark)
    """
    # First handle empty filled fields (blank fields using new syntax)
    content = re.sub(r'\{\{filled:\s*\}\}', '<!--BLANK-->', content)
    
    # Then handle filled fields with content
    pattern = r'\{\{filled:([^}]+)\}\}'
    content = re.sub(pattern, r'<!--FILLED:\1-->', content)
    
    # Handle signature markers
    content = re.sub(r'\{\{signature\}\}', '<!--SIGNATURE-->', content)
    
    return content

def determine_blank_size(underscore_count):
    """
    Determine the size notation based on underscore count.
    """
    if underscore_count <= 3:
        return '<!--BLANK:short-->'
    elif underscore_count <= 6:
        return '<!--BLANK:medium-->'
    else:
        return '<!--BLANK:long-->'


def process_file(file_path):
    """Process a single file to convert form fields."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"Error: File not found: {file_path}")
        return False
    
    try:
        content = path.read_text(encoding='utf-8')
        original_content = content
        
        # Process filled fields first (handles both empty and filled)
        content = process_filled_fields(content)
        
        # Then process legacy underscore blanks
        content = process_unfilled_blanks(content)
        
        # Only write if changes were made
        if content != original_content:
            path.write_text(content, encoding='utf-8')
            print(f"✓ Processed form fields in: {path.name}")
            
            # Count what was processed
            blank_count = content.count('<!--BLANK')
            filled_count = content.count('<!--FILLED:')
            
            if blank_count > 0:
                print(f"  Blank fields converted: {blank_count}")
            if filled_count > 0:
                print(f"  Filled fields marked: {filled_count}")
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error processing {path.name}: {e}")
        return False

def main():
    """Main entry point for the form fields processor."""
    if len(sys.argv) < 2:
        print("Usage: python3 form-fields-processor.py <file_path> [file_path2 ...]")
        print("Example: python3 form-fields-processor.py src/resolutions/*.md")
        sys.exit(1)
    
    success_count = 0
    
    for file_path in sys.argv[1:]:
        # Handle glob patterns
        path = Path(file_path)
        if '*' in str(path):
            # Glob pattern - expand it
            parent = path.parent
            pattern = path.name
            for file in parent.glob(pattern):
                if file.suffix == '.md':
                    if process_file(file):
                        success_count += 1
        else:
            # Single file
            if process_file(file_path):
                success_count += 1
    
    if success_count > 0:
        print(f"\n✅ Processed form fields in {success_count} file(s)")

if __name__ == "__main__":
    main()