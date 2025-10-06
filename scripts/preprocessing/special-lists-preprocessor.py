#!/usr/bin/python3
"""
Special list preprocessor for handling unusual list formats in specific documents.
This handles edge cases like lists that start at non-standard numbers (e.g., 1.4 instead of 1.1)
"""

import re
import sys
from pathlib import Path

def process_resolution_41425(content):
    """
    Handle the special case in Resolution 41425 where the instructions list
    starts at 1.4 (with no 1.1-1.3 preceding it).
    
    We'll add a special marker that the custom-list-processor can recognize
    to handle this during the HTML build phase.
    """
    lines = content.split('\n')
    modified_lines = []
    in_special_section = False
    found_first_item = False
    list_items = []
    
    for i, line in enumerate(lines):
        # Detect when we're in the instructions section
        if "CITY OF RIVERGROVE INSTRUCTIONS FOR REQUESTING PUBLIC RECORDS" in line:
            in_special_section = True
            modified_lines.append(line)
            continue
        
        # Process the special numbered items (1.4 through 1.9)
        if in_special_section:
            match = re.match(r'^(1\.(\d+))\s+(.+)$', line)
            if match:
                list_num = match.group(1)  # e.g., "1.4"
                item_num = match.group(2)   # e.g., "4"
                content = match.group(3)
                
                # For the first item (1.4), add a special marker comment
                if list_num == "1.4" and not found_first_item:
                    # Add a marker that indicates this list starts at 1.4
                    modified_lines.append("")  # blank line before marker
                    modified_lines.append("<!-- SPECIAL_LIST_START:1.4 -->")
                    found_first_item = True
                
                # Collect this item
                list_items.append(f"{list_num} {content}")
            elif line.strip() == "" and found_first_item:
                # Blank line while collecting list items - just skip it
                pass
            else:
                # Non-blank, non-list line means end of list
                if found_first_item and list_items and line.strip() != "":
                    # Add all collected list items
                    for item in list_items:
                        modified_lines.append(item)
                        modified_lines.append("")  # blank line after each item
                    # Add the end marker
                    modified_lines.append("<!-- SPECIAL_LIST_END -->")
                    # Reset for any future lists
                    list_items = []
                    found_first_item = False
                    in_special_section = False
                
                # Add the current line
                modified_lines.append(line)
        else:
            modified_lines.append(line)
    
    # Handle case where list goes to end of file
    if found_first_item and list_items:
        for item in list_items:
            modified_lines.append(item)
            modified_lines.append("")
        modified_lines.append("<!-- SPECIAL_LIST_END -->")
    
    return '\n'.join(modified_lines)

def process_document_specific_lists(file_path, content):
    """
    Apply document-specific list processing based on filename.
    """
    filename = Path(file_path).name
    
    # Resolution 41425 - Special case with list starting at 1.4
    if "41425" in filename or "Public-Records-Policy" in filename:
        content = process_resolution_41425(content)
    
    # Add more document-specific handlers here as needed
    # elif "other-document" in filename:
    #     content = process_other_document(content)
    
    return content

def process_file(file_path):
    """Process a single file for special list formatting."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"Error: File not found: {file_path}")
        return False
    
    try:
        content = path.read_text(encoding='utf-8')
        original_content = content
        
        # Apply document-specific list processing
        content = process_document_specific_lists(file_path, content)
        
        # Only write if changes were made
        if content != original_content:
            path.write_text(content, encoding='utf-8')
            print(f"✓ Processed special lists in: {path.name}")
            return True
        else:
            print(f"  No special list processing needed: {path.name}")
            return False
            
    except Exception as e:
        print(f"Error processing {path.name}: {e}")
        return False

def main():
    """Main entry point for the special list preprocessor."""
    if len(sys.argv) < 2:
        print("Usage: python3 special-lists-preprocessor.py <file_path> [file_path2 ...]")
        print("Example: python3 special-lists-preprocessor.py src/resolutions/2019-Res-41425-Public-Records-Policy.md")
        sys.exit(1)
    
    success_count = 0
    for file_path in sys.argv[1:]:
        if process_file(file_path):
            success_count += 1
    
    print(f"\n✅ Processed {success_count} file(s) with special list formatting")

if __name__ == "__main__":
    main()