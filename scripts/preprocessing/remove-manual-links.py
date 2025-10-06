#!/usr/bin/python3
"""
Remove manual markdown cross-reference links from source documents.
These should be plain text that gets converted to links during the build process.
"""

import re
from pathlib import Path

def remove_manual_links(content):
    """Remove manual markdown links to ordinances/resolutions, keeping just the text."""
    
    # Pattern to match markdown links to ordinances or resolutions
    # Captures the link text and ignores the URL part
    pattern = r'\[([^\]]+)\]\(\.\./(ordinances|resolutions)/[^)]+\.md\)'
    
    def replace_link(match):
        # Return just the link text without the markdown link syntax
        return match.group(1)
    
    return re.sub(pattern, replace_link, content)

def process_file(file_path):
    """Process a single file to remove manual links."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"  ✗ File not found: {file_path}")
        return False
    
    try:
        content = path.read_text(encoding='utf-8')
        original_content = content
        
        # Remove manual links
        content = remove_manual_links(content)
        
        # Only write if changes were made
        if content != original_content:
            path.write_text(content, encoding='utf-8')
            
            # Count how many links were removed
            links_removed = original_content.count('](../') - content.count('](../')
            print(f"  ✓ Removed {links_removed} manual links from {path.name}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"  ✗ Error processing {path.name}: {e}")
        return False

def main():
    """Remove manual links from all source documents."""
    print("Removing manual cross-reference links from source documents...")
    
    processed_count = 0
    
    # Process Ordinances
    print("\nProcessing Ordinances...")
    ord_dir = Path("Ordinances")
    if ord_dir.exists():
        for file in ord_dir.glob("*.md"):
            if process_file(file):
                processed_count += 1
    
    # Process Resolutions
    print("\nProcessing Resolutions...")
    res_dir = Path("Resolutions")
    if res_dir.exists():
        for file in res_dir.glob("*.md"):
            if process_file(file):
                processed_count += 1
    
    # Process Interpretations
    print("\nProcessing Interpretations...")
    int_dir = Path("Interpretations")
    if int_dir.exists():
        for file in int_dir.glob("*.md"):
            if process_file(file):
                processed_count += 1
    
    print(f"\n✅ Processed {processed_count} files")

if __name__ == "__main__":
    main()