#!/usr/bin/python3
"""
Standardize markdown header levels in ordinance files while preserving content.
This only changes the markdown formatting (# levels), not the actual text or structure.
"""

import re
from pathlib import Path

def standardize_ordinance_headers(content, filename):
    """
    Standardize header levels in an ordinance file.
    Rules:
    - First ordinance number gets # (h1)
    - "AN ORDINANCE..." titles get ## (h2)
    - "BEFORE THE CITY COUNCIL..." gets ### (h3)
    - Major sections like "AMENDMENTS TO..." get ## (h2)
    - Numbered sections get ### (h3)
    - Lettered subsections get #### (h4)
    """
    
    lines = content.split('\n')
    modified_lines = []
    
    # Track if we've seen the first ordinance number
    seen_first_ordinance = False
    
    for line in lines:
        original_line = line
        
        # Match ordinance number patterns
        ord_patterns = [
            r'^#{1,6}\s*(ORDINANCE\s*(NO\.|#)\s*\d+.*)',
            r'^#{1,6}\s*(ORDINANCE\s*(NO\.|#)\s*[IVXLC]+\b)',  # Roman numerals
            r'^#{1,6}\s*(EXHIBIT\s+[A-Z]\b)',  # For 1974 Ord #16
        ]
        
        for pattern in ord_patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                # First ordinance number gets #, subsequent ones get # too
                # (preserving document structure where numbers repeat)
                line = f"# {match.group(1)}"
                seen_first_ordinance = True
                break
        
        # Match "AN ORDINANCE..." titles
        if re.match(r'^#{1,6}\s*(AN ORDINANCE\b.*)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(AN ORDINANCE\b.*)', line, re.IGNORECASE)
            line = f"## {match.group(1)}"
        
        # Match "BEFORE THE CITY COUNCIL..."
        elif re.match(r'^#{1,6}\s*(BEFORE THE (CITY )?COUNCIL.*)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(BEFORE THE (CITY )?COUNCIL.*)', line, re.IGNORECASE)
            line = f"### {match.group(1)}"
        
        # Match major document sections
        elif re.match(r'^#{1,6}\s*(AMENDMENTS? TO.*)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(AMENDMENTS? TO.*)', line, re.IGNORECASE)
            line = f"## {match.group(1)}"
        elif re.match(r'^#{1,6}\s*(FLOOD (DAMAGE )?PREVENTION ORDINANCE)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(FLOOD (DAMAGE )?PREVENTION ORDINANCE)', line, re.IGNORECASE)
            line = f"## {match.group(1)}"
        elif re.match(r'^#{1,6}\s*(FUNCTIONAL PLAN COMPLIANCE ORDINANCE)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(FUNCTIONAL PLAN COMPLIANCE ORDINANCE)', line, re.IGNORECASE)
            line = f"## {match.group(1)}"
        elif re.match(r'^#{1,6}\s*(EMERGENCY CLAUSE)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(EMERGENCY CLAUSE)', line, re.IGNORECASE)
            line = f"## {match.group(1)}"
        elif re.match(r'^#{1,6}\s*(Water Quality and Flood Management Area Ordinance)', line):
            match = re.match(r'^#{1,6}\s*(Water Quality and Flood Management Area Ordinance)', line)
            line = f"## {match.group(1)}"
        
        # Match section patterns like "Section 1.0", "Section I", "Section 5.100"
        elif re.match(r'^#{1,6}\s*(Section\s+[IVX0-9]+\.?[0-9]*\.?.*)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(Section\s+[IVX0-9]+\.?[0-9]*\.?.*)', line, re.IGNORECASE)
            line = f"### {match.group(1)}"
        
        # Match subsection patterns with numbers like "1.1", "2.1", "5.1-1"
        elif re.match(r'^#{1,6}\s*(\d+\.\d+(?:-\d+)?\s+[A-Z].*)', line):
            match = re.match(r'^#{1,6}\s*(\d+\.\d+(?:-\d+)?\s+[A-Z].*)', line)
            line = f"#### {match.group(1)}"
        
        # Match lettered subsections like "(a) DEFINITIONS", "(b) APPLICATION"
        elif re.match(r'^#{1,6}\s*(\([a-z]\)\s+[A-Z].*)', line):
            match = re.match(r'^#{1,6}\s*(\([a-z]\)\s+[A-Z].*)', line)
            line = f"#### {match.group(1)}"
        
        # Special patterns for specific documents
        elif re.match(r'^#{1,6}\s*(Table\s+\d+.*)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(Table\s+\d+.*)', line, re.IGNORECASE)
            line = f"#### {match.group(1)}"
        elif re.match(r'^#{1,6}\s*(Index)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(Index)', line, re.IGNORECASE)
            line = f"## {match.group(1)}"
        elif re.match(r'^#{1,6}\s*(Document Notes)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(Document Notes)', line, re.IGNORECASE)
            line = f"## {match.group(1)}"
        elif re.match(r'^#{1,6}\s*(Statutory Authorization)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(Statutory Authorization)', line, re.IGNORECASE)
            line = f"## {match.group(1)}"
        
        # For lines like "Add after Section 6.236 the following:"
        elif re.match(r'^#{1,6}\s*(Add .*)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(Add .*)', line, re.IGNORECASE)
            line = f"### {match.group(1)}"
        
        # Numbered list items within amendments (e.g., "1. Section 5.010 is amended...")
        elif re.match(r'^#{1,6}\s*(\d+\.\s+Section\s+.*)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(\d+\.\s+Section\s+.*)', line, re.IGNORECASE)
            line = f"### {match.group(1)}"
        
        modified_lines.append(line)
    
    return '\n'.join(modified_lines)

def process_ordinances():
    """Process all ordinance files to standardize headers."""
    
    ordinances_dir = Path("Ordinances")
    
    if not ordinances_dir.exists():
        print("Ordinances directory not found!")
        return
    
    changed_files = []
    
    for md_file in sorted(ordinances_dir.glob("*.md")):
        # Skip stub files
        if "STUB" in md_file.name:
            print(f"Skipping stub file: {md_file.name}")
            continue
            
        print(f"Processing: {md_file.name}")
        
        # Read file
        content = md_file.read_text(encoding='utf-8')
        original = content
        
        # Standardize headers
        content = standardize_ordinance_headers(content, md_file.name)
        
        # Only write if changed
        if content != original:
            md_file.write_text(content, encoding='utf-8')
            changed_files.append(md_file.name)
            print(f"  ✓ Updated headers")
        else:
            print(f"  - No changes needed")
    
    print(f"\n{'='*50}")
    print(f"Standardized headers in {len(changed_files)} files:")
    for filename in changed_files:
        print(f"  - {filename}")
    
    return changed_files

if __name__ == "__main__":
    changed = process_ordinances()
    if changed:
        print("\n✅ Header standardization complete!")
        print("Review the changes with: git diff")
        print("Or view in GitHub after pushing the branch")