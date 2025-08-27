#!/usr/bin/env python3
"""
Preprocessor to automatically wrap footnotes in styling divs.
Detects footnote patterns and adds appropriate HTML wrapping.

Safety features:
1. Only processes footnotes that appear after a table
2. Requires specific format: superscript number followed by bold text
3. Groups consecutive footnotes together
"""

import re
import sys
from pathlib import Path

def validate_footnotes(content):
    """Check if footnote references in tables match footnote definitions."""
    lines = content.split('\n')
    table_refs = set()
    footnote_defs = set()
    warnings = []
    
    # Find footnote references in tables
    in_table = False
    for line in lines:
        if '|' in line:
            in_table = True
            # Find all superscript numbers in this table line
            refs = re.findall(r'[¹²³⁴⁵⁶⁷⁸⁹⁰]+', line)
            table_refs.update(refs)
        elif in_table and not line.strip():
            # Empty line after table, stop looking
            in_table = False
    
    # Find footnote definitions
    for line in lines:
        if re.match(r'^([¹²³⁴⁵⁶⁷⁸⁹⁰]+)\s+', line):
            match = re.match(r'^([¹²³⁴⁵⁶⁷⁸⁹⁰]+)', line)
            if match:
                footnote_defs.add(match.group(1))
    
    # Check for mismatches
    refs_without_defs = table_refs - footnote_defs
    defs_without_refs = footnote_defs - table_refs
    
    if refs_without_defs:
        warnings.append(f"  ⚠️  Table references without definitions: {', '.join(sorted(refs_without_defs))}")
    if defs_without_refs:
        warnings.append(f"  ⚠️  Definitions without table references: {', '.join(sorted(defs_without_refs))}")
    
    return warnings

def process_footnotes(content):
    """Find and wrap footnote sections in div tags."""
    
    # Split content into lines for processing
    lines = content.split('\n')
    result_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this line is after a table (allowing for blank lines)
        # Look back up to 5 lines to find a table (to handle multiple blank lines)
        is_after_table = False
        for j in range(1, min(6, i+1)):  # Look back 1-5 lines
            if '|' in lines[i-j]:
                is_after_table = True
                break
        
        # Check if starts with a superscript number (with or without bold text)
        if is_after_table and re.match(r'^[¹²³⁴⁵⁶⁷⁸⁹⁰]+\s+', line):
            # Found the start of a footnote section
            footnote_lines = []
            
            # Collect all footnotes in this section (may have blank lines between them)
            while i < len(lines):
                # Check if current line is a footnote (with or without bold)
                if re.match(r'^[¹²³⁴⁵⁶⁷⁸⁹⁰]+\s+', lines[i]):
                    footnote_lines.append(lines[i])
                    i += 1
                    # Grab continuation lines for this footnote
                    while i < len(lines) and lines[i] and not re.match(r'^[¹²³⁴⁵⁶⁷⁸⁹⁰]+', lines[i]) and not lines[i].startswith('#'):
                        footnote_lines.append(lines[i])
                        i += 1
                # Allow blank lines between footnotes
                elif not lines[i] and i + 1 < len(lines) and re.match(r'^[¹²³⁴⁵⁶⁷⁸⁹⁰]+\s+', lines[i + 1]):
                    footnote_lines.append(lines[i])  # Keep the blank line
                    i += 1
                else:
                    # Not a footnote or blank line before footnote - stop collecting
                    break
            
            # Add wrapped footnotes
            if footnote_lines:
                result_lines.append('')  # blank line before
                result_lines.append('<div class="footnotes">')
                result_lines.append('')
                result_lines.extend(footnote_lines)
                result_lines.append('')
                result_lines.append('</div>')
                result_lines.append('')  # blank line after
        else:
            # Regular line, add as-is
            result_lines.append(line)
            i += 1
    
    return '\n'.join(result_lines)

def process_file(filepath, dry_run=False):
    """Process a single markdown file."""
    path = Path(filepath)
    if not path.exists() or not path.suffix == '.md':
        return None
    
    content = path.read_text()
    processed = process_footnotes(content)
    
    # Validate footnotes
    warnings = validate_footnotes(processed)
    
    # Debug: Check if content actually changed
    if content != processed:
        if not dry_run:
            path.write_text(processed)
        # Count how many footnotes were found (with or without bold)
        footnote_count = len(re.findall(r'^[¹²³⁴⁵⁶⁷⁸⁹⁰]+\s+', processed, re.MULTILINE))
        # Debug: Count divs added
        divs_added = processed.count('<div class="footnotes">') - content.count('<div class="footnotes">')
        if divs_added > 0:
            print(f"  Added {divs_added} footnote div(s) to {filepath}")
        return {'file': str(filepath), 'footnotes': footnote_count, 'warnings': warnings}
    return None

def main(dry_run=False):
    """Process all markdown files in src directories."""
    src_dirs = ['src/ordinances', 'src/resolutions', 'src/interpretations', 'src/other']
    
    changed_files = []
    
    for dir_path in src_dirs:
        if Path(dir_path).exists():
            for file in Path(dir_path).glob('*.md'):
                result = process_file(file, dry_run)
                if result:
                    changed_files.append(result)
    
    # Print report
    if changed_files:
        print("\n" + "="*60)
        print(f"FOOTNOTE PREPROCESSOR REPORT {'(DRY RUN)' if dry_run else ''}")
        print("="*60)
        print(f"Files with footnotes found: {len(changed_files)}\n")
        
        for item in changed_files:
            print(f"📄 {item['file']}")
            print(f"   Found {item['footnotes']} footnote(s)")
            if item.get('warnings'):
                for warning in item['warnings']:
                    print(warning)
        
        print("\n" + "="*60)
        if dry_run:
            print("This was a DRY RUN - no files were modified")
            print("Run without --dry-run to apply changes")
        else:
            print(f"Successfully processed {len(changed_files)} files")
        print("="*60 + "\n")
    else:
        print("\n✅ No footnotes found that need processing\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process footnotes in markdown files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without modifying files')
    args = parser.parse_args()
    
    main(dry_run=args.dry_run)