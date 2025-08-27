#!/usr/bin/env python3
"""
Script to add cross-reference links between documents in the src directory.
Run this before building with mdBook.
"""

import re
from pathlib import Path
import os

# Build document map from actual files
def build_document_map():
    """Build a map of references to file paths from the actual files in src."""
    doc_map = {}
    src_dir = Path("src")
    
    # Process ordinances
    ord_dir = src_dir / "ordinances"
    if ord_dir.exists():
        for file in ord_dir.glob("*.md"):
            # Extract ordinance number from filename
            filename = file.stem
            
            # Parse different filename patterns
            if match := re.match(r'(\d{4})-Ord-(\d+(?:-\d+)?(?:[A-Z])?)', filename):
                year, ord_num = match.groups()
                # Remove leading zeros
                ord_num = ord_num.lstrip('0')
                
                # Add various reference patterns (all lowercase for matching)
                # The regex search is case-insensitive, so we only need lowercase keys
                # Convert ord_num to lowercase for the keys
                ord_num_lower = ord_num.lower()
                doc_map[f"ordinance #{ord_num_lower}"] = f"../ordinances/{filename}.md"
                doc_map[f"ordinance {ord_num_lower}"] = f"../ordinances/{filename}.md"
                doc_map[f"ord. #{ord_num_lower}"] = f"../ordinances/{filename}.md"
                doc_map[f"ord #{ord_num_lower}"] = f"../ordinances/{filename}.md"
                doc_map[f"ordinance no. {ord_num_lower}"] = f"../ordinances/{filename}.md"
                
                # Add year-specific variations if applicable
                if "-" in ord_num_lower:
                    base_num = ord_num_lower.split("-")[0]
                    doc_map[f"ordinance #{base_num}"] = f"../ordinances/{filename}.md"
                    doc_map[f"ordinance {base_num}"] = f"../ordinances/{filename}.md"
    
    # Process resolutions
    res_dir = src_dir / "resolutions"
    if res_dir.exists():
        for file in res_dir.glob("*.md"):
            filename = file.stem
            
            # Parse resolution filename
            if match := re.match(r'(\d{4})-Res-(\d+)', filename):
                year, res_num = match.groups()
                res_num = res_num.lstrip('0')
                
                # Add various reference patterns
                doc_map[f"resolution #{res_num}"] = f"../resolutions/{filename}.md"
                doc_map[f"resolution {res_num}"] = f"../resolutions/{filename}.md"
                doc_map[f"res. #{res_num}"] = f"../resolutions/{filename}.md"
                doc_map[f"res #{res_num}"] = f"../resolutions/{filename}.md"
    
    # Add some known references to documents not yet digitized
    # These will become valid links once the documents are added
    doc_map["ordinance #70-2001"] = "../ordinances/2001-Ord-70-2001-WQRA.md"
    doc_map["ordinance 70-2001"] = "../ordinances/2001-Ord-70-2001-WQRA.md"
    doc_map["ordinance no. 70-2001"] = "../ordinances/2001-Ord-70-2001-WQRA.md"
    doc_map["ord. #70-2001"] = "../ordinances/2001-Ord-70-2001-WQRA.md"
    
    # Add specific mapping for 54-89 with -C suffix
    doc_map["ordinance #54-89"] = "../ordinances/1989-Ord-54-89-C-Land-Development.md"
    doc_map["ordinance 54-89"] = "../ordinances/1989-Ord-54-89-C-Land-Development.md"
    doc_map["ordinance no. 54-89"] = "../ordinances/1989-Ord-54-89-C-Land-Development.md"
    doc_map["ord. #54-89"] = "../ordinances/1989-Ord-54-89-C-Land-Development.md"
    
    return doc_map

def add_cross_references(content, doc_map, current_file):
    """Add cross-reference links to the content."""
    
    # Build regex pattern from document map
    patterns = sorted(doc_map.keys(), key=len, reverse=True)
    escaped_patterns = [re.escape(p) for p in patterns]
    pattern = r'\b(' + '|'.join(escaped_patterns) + r')(?:\s*\(\d{4}\))?'
    regex = re.compile(pattern, re.IGNORECASE)
    
    def replace_reference(match):
        """Replace a reference with a markdown link."""
        full_match = match.group(0)
        reference = match.group(1).lower()
        
        if reference in doc_map:
            link_path = doc_map[reference]
            
            # Don't link to self
            if current_file.name in link_path:
                return full_match
            
            # Check if already in a link or heading
            start_pos = match.start()
            # Look back for [ or # (heading)
            lookback = content[max(0, start_pos-10):start_pos]
            if '[' in lookback or '#' in lookback[-2:]:
                return full_match
            
            # Check if we're in a code block
            lines_before = content[:start_pos].split('\n')
            in_code = False
            for line in lines_before:
                if line.strip().startswith('```'):
                    in_code = not in_code
            if in_code:
                return full_match
            
            # Create markdown link
            return f'[{full_match}]({link_path})'
        
        return full_match
    
    return regex.sub(replace_reference, content)

def process_markdown_files():
    """Process all markdown files in src directory."""
    src_dir = Path("src")
    doc_map = build_document_map()
    
    print(f"Built document map with {len(doc_map)} reference patterns")
    
    processed_count = 0
    link_count = 0
    
    # Process all .md files recursively
    for md_file in src_dir.rglob("*.md"):
        # Skip SUMMARY.md
        if md_file.name == "SUMMARY.md":
            continue
        
        # Read file content
        content = md_file.read_text(encoding='utf-8')
        original_content = content
        
        # Add cross-references
        content = add_cross_references(content, doc_map, md_file)
        
        # Only write if content changed
        if content != original_content:
            md_file.write_text(content, encoding='utf-8')
            
            # Count links added
            links_added = content.count('](../') - original_content.count('](../')
            link_count += links_added
            
            print(f"  Processed {md_file.relative_to(src_dir)} - added {links_added} links")
            processed_count += 1
    
    print(f"\nProcessed {processed_count} files, added {link_count} total cross-reference links")

if __name__ == "__main__":
    # Change to repository root
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    process_markdown_files()