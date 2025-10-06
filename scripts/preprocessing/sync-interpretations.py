#!/usr/bin/python3
"""
Sync interpretations from the main Interpretations directory to src/interpretations for mdBook

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
    - {{signature}} -> <span class="signature-mark" aria-label="Signature" data-tooltip="Signature present in original document">Signature</span><br>
    """
    # Handle empty fields first
    content = re.sub(r'\{\{filled:\s*\}\}',
                    '<span class="form-field-empty form-field-medium" data-tooltip="Field left blank in source doc"></span>',
                    content)

    # Handle filled fields
    def replace_filled(match):
        text = match.group(1).strip()
        return f'<span class="form-field-filled" data-tooltip="Field filled in on source doc">{text}</span>'

    content = re.sub(r'\{\{filled:([^}]+)\}\}', replace_filled, content)

    # Convert {{signature}} to styled signature mark with line break
    content = re.sub(r'\{\{signature\}\}',
                     '<span class="signature-mark" aria-label="Signature" data-tooltip="Signature present in original document">Signature</span><br>',
                     content)

    return content

def sync_interpretations():
    """Copy all files from Interpretations/ to src/interpretations/"""
    source_dir = Path("source-documents/Interpretations")
    dest_dir = Path("src/interpretations")
    
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
        # No filename modification needed for interpretations
        dest_name = file.name
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
            updated_files.append(dest_name)
    
    # Remove files that no longer exist in source
    for dest_name in existing_dest_files:
        if dest_name not in processed_dest_names:
            existing_dest_files[dest_name].unlink()
            removed_files.append(dest_name)
    
    # Print results
    if updated_files or removed_files:
        if updated_files:
            print(f"  Updated {len(updated_files)} interpretation file(s):")
            for filename in sorted(updated_files):
                print(f"    ✓ {filename}")
        if removed_files:
            print(f"  Removed {len(removed_files)} interpretation file(s):")
            for filename in sorted(removed_files):
                print(f"    ✗ {filename}")
    else:
        print(f"  No changes needed ({len(list(source_dir.glob('*.md')))} files already in sync)")
    
    return True

if __name__ == "__main__":
    if sync_interpretations():
        print("✓ Interpretations synced successfully")
    else:
        print("✗ Failed to sync interpretations")
        sys.exit(1)