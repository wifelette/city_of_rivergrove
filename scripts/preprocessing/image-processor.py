#!/usr/bin/env python3
"""
Image processor that converts {{image:}} tags to proper markdown/HTML
for inline images in legal documents.

Syntax:
{{image:filename|alt=text|caption=text}}

This will:
1. Look for the image in src/images/{document-type}/ directory
2. Convert to proper HTML with figure/figcaption tags
3. Apply consistent styling
"""

import re
import sys
from pathlib import Path

def get_image_path(filename, document_path):
    """
    Determine the correct image path based on document type and location.
    """
    # Determine document type from path
    doc_types = {
        'ordinances': 'ordinances',
        'resolutions': 'resolutions', 
        'interpretations': 'interpretations'
    }
    
    doc_type = None
    for key in doc_types:
        if key in str(document_path).lower():
            doc_type = doc_types[key]
            break
    
    if not doc_type:
        # Default to ordinances if can't determine
        doc_type = 'ordinances'
    
    # Extract document identifier from path
    doc_name = Path(document_path).stem
    
    # Build the image filename
    image_filename = f"{doc_name}-{filename}.png"
    
    # Return relative path for mdBook
    return f"images/{doc_type}/{image_filename}"

def process_image_tags(content, file_path):
    """
    Convert {{image:}} tags to HTML figure elements.
    
    Example:
    {{image:slope-measurement|alt=Slope diagrams|caption=Figure 1: Slope measurement method}}
    
    Becomes:
    <figure class="document-figure">
        <img src="images/ordinances/2001-Ord-70-2001-WQRA-slope-measurement.png" 
             alt="Slope diagrams" />
        <figcaption>Figure 1: Slope measurement method</figcaption>
    </figure>
    """
    
    def replace_image_tag(match):
        full_tag = match.group(0)
        params = match.group(1)
        
        # Parse parameters
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
        
        # Get the image path
        image_path = get_image_path(filename, file_path)
        
        # Build HTML
        html = f'<figure class="document-figure">\n'
        html += f'    <img src="{image_path}" alt="{alt_text}" />\n'
        if caption:
            html += f'    <figcaption>{caption}</figcaption>\n'
        html += f'</figure>'
        
        return html
    
    # Pattern to match {{image:...}} tags
    pattern = r'\{\{image:([^}]+)\}\}'
    
    # Replace all image tags
    content = re.sub(pattern, replace_image_tag, content)
    
    return content

def process_file(file_path):
    """Process a single file to convert image tags."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"Error: File not found: {file_path}")
        return False
    
    try:
        content = path.read_text(encoding='utf-8')
        original_content = content
        
        # Process image tags
        content = process_image_tags(content, file_path)
        
        # Only write if changes were made
        if content != original_content:
            path.write_text(content, encoding='utf-8')
            print(f"✓ Processed images in: {path.name}")
            
            # Count what was processed
            image_count = content.count('<figure class="document-figure">')
            if image_count > 0:
                print(f"  Images processed: {image_count}")
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error processing {path.name}: {e}")
        return False

def main():
    """Main entry point for the image processor."""
    if len(sys.argv) < 2:
        print("Usage: python3 image-processor.py <file_path> [file_path2 ...]")
        print("Example: python3 image-processor.py src/ordinances/*.md")
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
        print(f"\n✅ Processed images in {success_count} file(s)")

if __name__ == "__main__":
    main()