#!/usr/bin/env python3
"""
Sync resolutions from the main Resolutions directory to src/resolutions for mdBook

TODO: Update to use unified title resolver (scripts/utils/title_resolver.py)
      See Issue #22 for tracking this work
"""

import os
import re
import shutil
import sys
from pathlib import Path

def process_form_fields(content):
    """
    Convert form field syntax to inline HTML during sync.
    
    Converts:
    - {{filled:}} -> <span class="form-field-empty form-field-medium" data-tooltip="Field left blank in source doc"></span>
    - {{filled:text}} -> <span class="form-field-filled" data-tooltip="Field filled in on source doc">text</span>
    
    Special handling for headings to avoid breaking mdBook anchor generation.
    """
    lines = content.split('\n')
    processed_lines = []
    
    for line in lines:
        # Check if this is a markdown heading
        if line.strip().startswith('#'):
            # For headings, we need to be careful not to break anchor ID generation
            # mdBook generates IDs from the text content, ignoring HTML tags
            # So we can add the spans, but need to keep the text intact
            
            # Handle filled fields in headings - keep the text but add styling
            def replace_heading_filled(match):
                text = match.group(1).strip()
                return f'<span class="form-field-filled" data-tooltip="Field filled in on source doc">{text}</span>'
            
            line = re.sub(r'\{\{filled:([^}]+)\}\}', replace_heading_filled, line)
            
            # Handle empty fields in headings
            line = re.sub(r'\{\{filled:\s*\}\}', 
                        '<span class="form-field-empty form-field-medium" data-tooltip="Field left blank in source doc"></span>', 
                        line)
        else:
            # For non-heading lines, process normally
            # Handle empty fields first
            line = re.sub(r'\{\{filled:\s*\}\}', 
                        '<span class="form-field-empty form-field-medium" data-tooltip="Field left blank in source doc"></span>', 
                        line)
            
            # Handle filled fields
            def replace_filled(match):
                text = match.group(1).strip()
                return f'<span class="form-field-filled" data-tooltip="Field filled in on source doc">{text}</span>'
            
            line = re.sub(r'\{\{filled:([^}]+)\}\}', replace_filled, line)
        
        # Handle new patterns (both in headings and regular lines)
        # Convert {{br}} to HTML line break
        line = re.sub(r'\{\{br\}\}', '<br>', line)
        
        # Convert {{table-footnote:...}} to div with class
        def replace_table_footnote(match):
            content = match.group(1).strip()
            return f'<div class="table-footnotes">{content}</div>'
        
        line = re.sub(r'\{\{table-footnote:\s*([^}]+)\}\}', replace_table_footnote, line)
        
        # Convert {{page:X}} to styled page reference
        def replace_page_ref(match):
            page_num = match.group(1).strip()
            return f'[page {page_num}]'
        
        line = re.sub(r'\{\{page:\s*([^}]+)\}\}', replace_page_ref, line)
        
        processed_lines.append(line)
    
    return '\n'.join(processed_lines)

def sync_resolutions():
    """Copy all files from Resolutions/ to src/resolutions/"""
    source_dir = Path("source-documents/Resolutions")
    dest_dir = Path("src/resolutions")
    
    if not source_dir.exists():
        print(f"Source directory {source_dir} does not exist")
        return False
    
    # Create destination directory if it doesn't exist
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Track changes
    updated_files = []
    removed_files = []
    
    # Get existing destination files
    existing_dest_files = {f.name: f for f in dest_dir.glob("*.md")}
    
    # Copy all .md files from source to destination
    processed_dest_names = set()
    for file in source_dir.glob("*.md"):
        # Map filename: remove # from resolution files
        dest_name = file.name.replace("#", "")
        dest_file = dest_dir / dest_name
        processed_dest_names.add(dest_name)
        
        # Read and process source content
        with open(file, 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        # Process form fields
        processed_content = process_form_fields(source_content)
        
        # Check if file needs updating
        needs_update = False
        if not dest_file.exists():
            needs_update = True
        else:
            # Compare processed content with existing file
            with open(dest_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            if processed_content != existing_content:
                needs_update = True
        
        if needs_update:
            # Write processed content
            with open(dest_file, 'w', encoding='utf-8') as f:
                f.write(processed_content)
            updated_files.append(f"{file.name} -> {dest_name}")
    
    # Remove files that no longer exist in source
    for dest_name in existing_dest_files:
        if dest_name not in processed_dest_names:
            existing_dest_files[dest_name].unlink()
            removed_files.append(dest_name)
    
    # Print results
    if updated_files or removed_files:
        if updated_files:
            print(f"  Updated {len(updated_files)} resolution file(s):")
            for filename in sorted(updated_files):
                print(f"    ✓ {filename}")
        if removed_files:
            print(f"  Removed {len(removed_files)} resolution file(s):")
            for filename in sorted(removed_files):
                print(f"    ✗ {filename}")
    else:
        print(f"  No changes needed ({len(list(source_dir.glob('*.md')))} files already in sync)")
    
    return True

if __name__ == "__main__":
    if sync_resolutions():
        print("✓ Resolutions synced successfully")
    else:
        print("✗ Failed to sync resolutions")
        sys.exit(1)