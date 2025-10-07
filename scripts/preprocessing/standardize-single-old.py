#!/usr/bin/env python3
"""
Standardize markdown headers and signatures for a single file.
Usage: python3 standardize-single.py <file_path>
"""

import sys
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
                line = f"# {match.group(1)}"
                seen_first_ordinance = True
                break
        
        # Match "AN ORDINANCE..." titles
        if re.match(r'^#{1,6}\s*(AN ORDINANCE\b.*)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(AN ORDINANCE\b.*)', line, re.IGNORECASE)
            line = f"## {match.group(1)}"
        
        # Match "BEFORE THE CITY COUNCIL..."
        elif re.match(r'^#{1,6}\s*(BEFORE THE CITY COUNCIL\b.*)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(BEFORE THE CITY COUNCIL\b.*)', line, re.IGNORECASE)
            line = f"### {match.group(1)}"
        
        # Match major section headers
        elif re.match(r'^#{1,6}\s*(AMENDMENTS TO\b.*)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(AMENDMENTS TO\b.*)', line, re.IGNORECASE)
            line = f"## {match.group(1)}"
        
        # Match numbered sections
        elif re.match(r'^#{1,6}\s*(Section\s+\d+\..*)', line, re.IGNORECASE):
            match = re.match(r'^#{1,6}\s*(Section\s+\d+\..*)', line, re.IGNORECASE)
            line = f"### {match.group(1)}"
        
        modified_lines.append(line)
    
    return '\n'.join(modified_lines)

def fix_signatures(content):
    """
    Fix signature formatting in a document.
    Converts various formats to standardized: [Signature], Name, Title
    """
    
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Pattern 1: Bold name followed by title on same line
        match = re.match(r'^\*\*([^*]+)\*\*,?\s*(.+?)(\s*\*\*Date\*\*:.*)?$', line)
        if match:
            name = match.group(1).strip()
            title = match.group(2).strip()
            date_part = match.group(3) if match.group(3) else ""
            
            if date_part:
                fixed_lines.append(f"[Signature], {name}, {title}  ")
                fixed_lines.append(date_part.strip() + "  ")
            else:
                # Check if next line has the date
                if i + 1 < len(lines) and '**Date**:' in lines[i + 1]:
                    fixed_lines.append(f"[Signature], {name}, {title}  ")
                    fixed_lines.append(lines[i + 1].strip() + "  ")
                    i += 1
                else:
                    fixed_lines.append(f"[Signature], {name}, {title}  ")
            i += 1
            continue
        
        # Pattern 2: [Signature] followed by bold name
        match = re.match(r'^\[Signature\][,:]?\s*\*\*([^*]+)\*\*,?\s*(.+?)$', line)
        if match:
            name = match.group(1).strip()
            title = match.group(2).strip()
            fixed_lines.append(f"[Signature], {name}, {title}  ")
            
            # Check for date on next line
            if i + 1 < len(lines) and '**Date**:' in lines[i + 1]:
                fixed_lines.append(lines[i + 1].strip() + "  ")
                i += 1
            i += 1
            continue
        
        # Pattern 3: Already correct format - ensure trailing spaces
        if re.match(r'^\[Signature\],\s*.+,\s*.+', line):
            if not line.endswith('  '):
                line = line.rstrip() + '  '
            fixed_lines.append(line)
        # Pattern 4: Date line - ensure trailing spaces
        elif '**Date**:' in line or '**Date:**' in line:
            if not line.endswith('  '):
                line = line.rstrip() + '  '
            fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        
        i += 1
    
    return '\n'.join(fixed_lines)

def process_file(file_path):
    """Process a single file for header standardization and signature fixing."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"Error: File not found: {file_path}")
        return False
    
    if not path.suffix == '.md':
        print(f"Error: Not a markdown file: {file_path}")
        return False
    
    try:
        content = path.read_text(encoding='utf-8')
        original_content = content
        
        # Apply standardizations based on file type
        if 'Ordinances' in str(path) or 'ordinances' in str(path):
            content = standardize_ordinance_headers(content, path.name)
        
        # Apply signature fixing to all document types
        content = fix_signatures(content)
        
        # Only write if changes were made
        if content != original_content:
            path.write_text(content, encoding='utf-8')
            print(f"✓ Standardized: {path.name}")
            return True
        else:
            print(f"  No changes needed: {path.name}")
            return False
            
    except Exception as e:
        print(f"Error processing {path.name}: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 standardize-single.py <file_path>")
        print("Example: python3 standardize-single.py Resolutions/2024-Res-#300-Fee-Schedule-Modification.md")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = process_file(file_path)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()