#!/usr/bin/python3
"""
mdBook preprocessor to automatically add cross-reference links between documents.
Converts references like "Ordinance #16" or "Resolution #72" into clickable links.
"""

import json
import sys
import re
from pathlib import Path

# Map of document references to their file paths
# This will be expanded as more documents are added
DOCUMENT_MAP = {
    # Ordinances
    "ordinance #16": "/ordinances/1974-Ord-16-Parks.md",
    "ordinance 16": "/ordinances/1974-Ord-16-Parks.md",
    "ord. #16": "/ordinances/1974-Ord-16-Parks.md",
    "ord #16": "/ordinances/1974-Ord-16-Parks.md",
    
    "ordinance #28": "/ordinances/1978-Ord-28-Parks.md",
    "ordinance 28": "/ordinances/1978-Ord-28-Parks.md",
    "ord. #28": "/ordinances/1978-Ord-28-Parks.md",
    "ord #28": "/ordinances/1978-Ord-28-Parks.md",
    
    "ordinance #52": "/ordinances/1987-Ord-52-Flood.md",
    "ordinance 52": "/ordinances/1987-Ord-52-Flood.md",
    "ord. #52": "/ordinances/1987-Ord-52-Flood.md",
    "ord #52": "/ordinances/1987-Ord-52-Flood.md",
    
    "ordinance #57-93": "/ordinances/1993-Ord-57-93-Manufactured-Homes.md",
    "ordinance 57-93": "/ordinances/1993-Ord-57-93-Manufactured-Homes.md",
    
    "ordinance #59-97a": "/ordinances/1998-Ord-59-97A-Land-Development-Amendment.md",
    "ordinance 59-97a": "/ordinances/1998-Ord-59-97A-Land-Development-Amendment.md",
    
    "ordinance #61-98": "/ordinances/1998-Ord-61-98-Land-Development-Amendment.md",
    "ordinance 61-98": "/ordinances/1998-Ord-61-98-Land-Development-Amendment.md",
    
    "ordinance #62-98": "/ordinances/1998-Ord-62-98-Flood-and-Land-Development-Amendment.md",
    "ordinance 62-98": "/ordinances/1998-Ord-62-98-Flood-and-Land-Development-Amendment.md",
    
    "ordinance #68-2000": "/ordinances/2000-Ord-68-2000-Metro-Compliance.md",
    "ordinance 68-2000": "/ordinances/2000-Ord-68-2000-Metro-Compliance.md",
    
    "ordinance #69-2000": "/ordinances/2000-Ord-69-2000-Title-3-Compliance-STUB.md",
    "ordinance 69-2000": "/ordinances/2000-Ord-69-2000-Title-3-Compliance-STUB.md",
    
    "ordinance #70-2001": "/ordinances/2001-Ord-70-2001-WQRA.md",  # Referenced but not yet digitized
    "ordinance 70-2001": "/ordinances/2001-Ord-70-2001-WQRA.md",
    "ordinance no. 70-2001": "/ordinances/2001-Ord-70-2001-WQRA.md",
    
    "ordinance #71-2002": "/ordinances/2002-Ord-71-2002-Gates.md",
    "ordinance 71-2002": "/ordinances/2002-Ord-71-2002-Gates.md",
    
    "ordinance #72-2002": "/ordinances/2002-Ord-72-2002-Penalties-and-Abatement-Amendment.md",
    "ordinance 72-2002": "/ordinances/2002-Ord-72-2002-Penalties-and-Abatement-Amendment.md",
    
    "ordinance #88-2017": "/ordinances/2017-Ord-88-2017-Docks.md",
    "ordinance 88-2017": "/ordinances/2017-Ord-88-2017-Docks.md",
    "ordinance no. 88-2017": "/ordinances/2017-Ord-88-2017-Docks.md",
    
    # Resolutions
    "resolution #22": "/resolutions/1976-Res-22-PC.md",
    "resolution 22": "/resolutions/1976-Res-22-PC.md",
    "res. #22": "/resolutions/1976-Res-22-PC.md",
    "res #22": "/resolutions/1976-Res-22-PC.md",
    
    "resolution #72": "/resolutions/1984-Res-72-Municipal-Services.md",
    "resolution 72": "/resolutions/1984-Res-72-Municipal-Services.md",
    "res. #72": "/resolutions/1984-Res-72-Municipal-Services.md",
    "res #72": "/resolutions/1984-Res-72-Municipal-Services.md",
}

def create_link_pattern():
    """Create a regex pattern that matches all document references."""
    # Build pattern from document map keys
    # Sort by length (longest first) to avoid partial matches
    patterns = sorted(DOCUMENT_MAP.keys(), key=len, reverse=True)
    
    # Escape special regex characters and create alternation
    escaped_patterns = [re.escape(p) for p in patterns]
    
    # Create pattern that captures the reference and optional year in parentheses
    # This handles cases like "Ordinance #16 (1974)"
    pattern = r'\b(' + '|'.join(escaped_patterns) + r')(?:\s*\(\d{4}\))?'
    
    return re.compile(pattern, re.IGNORECASE)

def add_cross_references(content, current_path):
    """Add cross-reference links to the content."""
    pattern = create_link_pattern()
    
    def replace_reference(match):
        """Replace a reference with a markdown link."""
        full_match = match.group(0)
        reference = match.group(1).lower()
        
        if reference in DOCUMENT_MAP:
            link_path = DOCUMENT_MAP[reference]
            
            # Don't link to self
            if current_path and link_path in current_path:
                return full_match
            
            # Check if this is already inside a link
            # (Simple check - could be improved)
            start_pos = match.start()
            if start_pos > 0 and content[start_pos-1] == '[':
                return full_match
            
            # Create markdown link
            return f'[{full_match}]({link_path})'
        
        return full_match
    
    return pattern.sub(replace_reference, content)

def process_chapter(chapter):
    """Process a single chapter to add cross-references."""
    if 'Chapter' in chapter:
        content = chapter['Chapter']['content']
        path = chapter['Chapter'].get('path', '')
        
        # Add cross-references
        new_content = add_cross_references(content, path)
        
        chapter['Chapter']['content'] = new_content
    
    # Process sub-items recursively
    if 'Chapter' in chapter and 'sub_items' in chapter['Chapter']:
        for sub_item in chapter['Chapter']['sub_items']:
            process_chapter(sub_item)

def main():
    """Main preprocessor function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "supports":
            # Tell mdbook we support HTML renderer
            sys.exit(0)
    
    # Read the book data from stdin
    context, book = json.load(sys.stdin)
    
    # Process all sections
    for section in book['sections']:
        process_chapter(section)
    
    # Output the processed book
    print(json.dumps(book))

if __name__ == '__main__':
    main()