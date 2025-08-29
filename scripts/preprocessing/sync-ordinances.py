#!/usr/bin/env python3
"""
Sync ordinances from the main Ordinances directory to src/ordinances for mdBook
"""

import os
import re
import shutil
import sys
from pathlib import Path

def process_images(content, doc_name):
    """
    Convert image syntax to HTML figure elements.
    
    Converts:
    {{image:filename|alt=text|caption=text}} to proper HTML figure elements
    """
    def replace_image_tag(match):
        params = match.group(1)
        parts = params.split('|')
        filename = parts[0].strip()
        
        # Default values
        alt_text = ""
        caption = ""
        
        # Parse additional parameters
        for part in parts[1:]:
            if '=' in part:
                key, value = part.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'alt':
                    alt_text = value
                elif key == 'caption':
                    caption = value
        
        # Build image path - relative to the HTML file location in book/ordinances/
        image_filename = f"{doc_name}-{filename}.png"
        image_path = f"../images/ordinances/{image_filename}"
        
        # Build HTML
        html = f'<figure class="document-figure">\n'
        html += f'    <img src="{image_path}" alt="{alt_text}" />\n'
        if caption:
            html += f'    <figcaption>{caption}</figcaption>\n'
        html += f'</figure>'
        
        return html
    
    # Pattern to match {{image:...}} tags
    pattern = r'\{\{image:([^}]+)\}\}'
    content = re.sub(pattern, replace_image_tag, content)
    
    return content

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
        
        processed_lines.append(line)
    
    return '\n'.join(processed_lines)

def sync_ordinances():
    """Copy all files from source-documents/Ordinances/ to src/ordinances/"""
    source_dir = Path("source-documents/Ordinances")
    dest_dir = Path("src/ordinances")
    
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
        # Map filename: remove # from ordinance files
        dest_name = file.name.replace("#", "")
        dest_file = dest_dir / dest_name
        processed_dest_names.add(dest_name)
        
        # Read and process source content
        with open(file, 'r', encoding='utf-8') as f:
            source_content = f.read()
        
        # Get document name for image processing
        doc_name = dest_file.stem
        
        # Process images first (before form fields, as images might contain form fields)
        processed_content = process_images(source_content, doc_name)
        
        # Process form fields
        processed_content = process_form_fields(processed_content)
        
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
            print(f"  Updated {len(updated_files)} ordinance file(s):")
            for filename in sorted(updated_files):
                print(f"    ✓ {filename}")
        if removed_files:
            print(f"  Removed {len(removed_files)} ordinance file(s):")
            for filename in sorted(removed_files):
                print(f"    ✗ {filename}")
    else:
        print(f"  No changes needed ({len(list(source_dir.glob('*.md')))} files already in sync)")
    
    return True

if __name__ == "__main__":
    if sync_ordinances():
        print("✓ Ordinances synced successfully")
    else:
        print("✗ Failed to sync ordinances")
        sys.exit(1)