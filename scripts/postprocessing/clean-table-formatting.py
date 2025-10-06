#!/usr/bin/python3
"""
Clean up table formatting in markdown files:
1. Convert ALL CAPS text in tables to Title Case
2. Add line breaks before parenthetical content in table cells
"""

import re
import sys
from pathlib import Path

def title_case_preserve_acronyms(text):
    """Convert to title case while preserving common acronyms."""
    # Common acronyms and Roman numerals to preserve in uppercase
    preserve_upper = ['I', 'II', 'III', 'IV', 'V', 'VI', 'WQRA', 'ORS', 'FEMA']
    
    # Words to keep lowercase (unless at start)
    keep_lower = ['and', 'or', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by']
    
    # Split into words, preserving commas attached to words
    words = re.findall(r"[A-Za-z]+(?:,)?", text)
    result = []
    
    for i, word in enumerate(words):
        # Check if word has comma attached
        has_comma = word.endswith(',')
        clean_word = word.rstrip(',')
        
        # Check if this should be preserved as uppercase
        if clean_word.upper() in preserve_upper:
            result_word = clean_word.upper()
        # Keep lowercase for conjunctions/prepositions (unless first word)
        elif i > 0 and clean_word.lower() in keep_lower:
            result_word = clean_word.lower()
        else:
            # Title case the word
            result_word = clean_word.capitalize()
        
        # Re-attach comma if needed
        if has_comma:
            result_word += ','
        
        result.append(result_word)
    
    return ' '.join(result)

def clean_table_cell(cell):
    """Clean up a single table cell."""
    # Skip empty cells or cells that are just whitespace
    cell = cell.strip()
    if not cell:
        return cell
    
    # Check if cell has bold text with parenthetical content
    # Pattern: **TEXT** (MORE TEXT) - allow lowercase articles/conjunctions
    match = re.match(r'(\*\*[A-Za-z\s,]+\*\*)\s*(\([^)]+\))', cell)
    if match:
        bold_part = match.group(1)
        paren_part = match.group(2)
        
        # Extract text from bold markers
        bold_text = bold_part[2:-2]  # Remove ** from both ends
        
        # Only convert if mostly uppercase (more than 50% of letters)
        uppercase_count = sum(1 for c in bold_text if c.isupper())
        letter_count = sum(1 for c in bold_text if c.isalpha())
        
        if letter_count > 0 and uppercase_count / letter_count > 0.5:
            # Convert to title case
            bold_text_clean = title_case_preserve_acronyms(bold_text)
            # Add line break before parenthetical
            return f"**{bold_text_clean}**<br>{paren_part}"
        else:
            # Not mostly caps, just add line break
            return f"{bold_part}<br>{paren_part}"
    
    # Check if entire cell is bold and all caps
    if cell.startswith('**') and cell.endswith('**'):
        inner_text = cell[2:-2]
        if inner_text.isupper():
            clean_text = title_case_preserve_acronyms(inner_text)
            return f"**{clean_text}**"
    
    return cell

def process_table_line(line):
    """Process a single table line."""
    if '|' not in line:
        return line
    
    # Split by | preserving the delimiters
    parts = line.split('|')
    
    # Skip if this is a separator line (contains ---)
    if any('---' in part for part in parts):
        return line
    
    # Process each cell (skip first and last empty parts from split)
    cleaned_parts = []
    for i, part in enumerate(parts):
        if i == 0 or i == len(parts) - 1:
            # Keep empty first/last parts (table boundaries)
            cleaned_parts.append(part)
        elif i == 1:  # First content column - apply cleaning
            cleaned_parts.append(' ' + clean_table_cell(part) + ' ')
        else:  # Other columns - preserve as is
            cleaned_parts.append(part)
    
    return '|'.join(cleaned_parts)

def process_file(filepath, dry_run=False):
    """Process a single markdown file."""
    path = Path(filepath)
    if not path.exists() or not path.suffix == '.md':
        return None
    
    content = path.read_text()
    lines = content.split('\n')
    
    # Track if we made changes
    changed = False
    result_lines = []
    
    # Track if we're in a table
    in_table = False
    
    for line in lines:
        if '|' in line:
            in_table = True
            processed_line = process_table_line(line)
            if processed_line != line:
                changed = True
            result_lines.append(processed_line)
        else:
            # Not a table line
            if in_table and line.strip() == '':
                # Empty line after table, reset flag
                in_table = False
            result_lines.append(line)
    
    if changed:
        new_content = '\n'.join(result_lines)
        if not dry_run:
            path.write_text(new_content)
        return {'file': str(filepath), 'changed': True}
    return None

def main(filepath=None, dry_run=False):
    """Process specified file or scan for files needing cleaning."""
    if filepath:
        # Process single file
        result = process_file(filepath, dry_run)
        if result:
            print(f"✓ Cleaned table formatting in {filepath}")
        else:
            print(f"No changes needed in {filepath}")
    else:
        # Scan all source directories
        src_dirs = ['Ordinances', 'Resolutions', 'Interpretations', 'Other']
        changed_files = []
        
        for dir_path in src_dirs:
            if Path(dir_path).exists():
                for file in Path(dir_path).glob('*.md'):
                    result = process_file(file, dry_run)
                    if result:
                        changed_files.append(result['file'])
        
        # Print report
        if changed_files:
            print("\n" + "="*60)
            print(f"TABLE FORMATTING CLEANUP {'(DRY RUN)' if dry_run else ''}")
            print("="*60)
            print(f"Files with table formatting cleaned: {len(changed_files)}\n")
            
            for filepath in changed_files:
                print(f"  ✓ {filepath}")
            
            print("\n" + "="*60)
            if dry_run:
                print("This was a DRY RUN - no files were modified")
                print("Run without --dry-run to apply changes")
            else:
                print(f"Successfully cleaned {len(changed_files)} files")
            print("="*60 + "\n")
        else:
            print("\n✅ No table formatting changes needed\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Clean table formatting in markdown files')
    parser.add_argument('file', nargs='?', help='Specific file to process')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    args = parser.parse_args()
    
    main(filepath=args.file, dry_run=args.dry_run)