#!/usr/bin/env python3
"""
Fix signature formatting in markdown files to ensure proper line breaks.
Adds double spaces at the end of signature lines for proper Markdown line breaks.
"""

import re
from pathlib import Path

def fix_signature_formatting(content):
    """Fix signature blocks and hearing info to have proper line breaks."""
    
    # Pattern to find signature lines
    # Matches: [Signature] or [Unsigned], Name, Title
    signature_pattern = r'(\[(?:Signature|Unsigned)\][^\n]*(?:Mayor|Recorder|Manager|Clerk|Attorney|MAYOR|RECORDER))\n'
    
    # Add double spaces at the end of signature lines for Markdown line breaks
    content = re.sub(signature_pattern, r'\1  \n', content)
    
    # Also fix Date lines that come after signatures
    # Ensure Date: lines have proper formatting
    date_pattern = r'(\*\*Date\*\*:[^\n]*)\n'
    content = re.sub(date_pattern, r'\1  \n', content)
    
    # Fix hearing/meeting lines (bolded lines at the beginning of documents)
    hearing_patterns = [
        r'(\*\*Planning Commission[^\n]*\*\*:[^\n]*)\n',
        r'(\*\*City Council[^\n]*\*\*:[^\n]*)\n',
        r'(\*\*Adopted[^\n]*\*\*:[^\n]*)\n',
        r'(\*\*Mayor[^\n]*\*\*:[^\n]*)\n',
        r'(\*\*Attest[^\n]*\*\*:[^\n]*)\n',
        r'(\*\*ATTEST[^\n]*\*\*:[^\n]*)\n',
    ]
    
    for pattern in hearing_patterns:
        content = re.sub(pattern, r'\1  \n', content)
    
    return content

def process_files():
    """Process all markdown files to fix signature formatting."""
    
    # Process ordinances, resolutions, and interpretations
    directories = [
        Path("Ordinances"),
        Path("Resolutions"),
        Path("Interpretations"),
        Path("src/ordinances"),
        Path("src/resolutions"),
        Path("src/interpretations")
    ]
    
    fixed_count = 0
    
    for directory in directories:
        if not directory.exists():
            continue
            
        for md_file in directory.glob("*.md"):
            # Read file
            content = md_file.read_text(encoding='utf-8')
            original = content
            
            # Fix signature formatting
            content = fix_signature_formatting(content)
            
            # Only write if changed
            if content != original:
                md_file.write_text(content, encoding='utf-8')
                print(f"Fixed signatures in: {md_file}")
                fixed_count += 1
    
    print(f"\nFixed signature formatting in {fixed_count} files")

if __name__ == "__main__":
    process_files()