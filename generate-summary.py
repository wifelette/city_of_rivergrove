#!/usr/bin/env python3
"""
Generate SUMMARY.md for mdBook from the documents in src/ directory.
This script automatically creates the table of contents based on existing files.
"""

import re
from pathlib import Path
from datetime import datetime

def extract_title_from_file(filepath):
    """Extract a clean title from the markdown file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        
        # Look for a heading that starts with "AN ORDINANCE" or "A RESOLUTION"
        subject_match = re.search(r'^###?\s+AN?\s+(ORDINANCE|RESOLUTION)\s+(.+)$', content, re.MULTILINE | re.IGNORECASE)
        if subject_match:
            title = subject_match.group(2).strip()
            # Clean up common patterns
            title = re.sub(r'^(ESTABLISHING|CREATING|AMENDING|ADOPTING|PROVIDING|DEFINING|RELATING TO)\s+', '', title, flags=re.IGNORECASE)
            # Remove "THE CITY OF..." prefix if present
            title = re.sub(r'^THE CITY OF.+?\s+(ORDINANCE|CODE)', '', title, flags=re.IGNORECASE)
            # Remove any markdown links
            title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)
            # Remove extra text after "as follows:" or similar
            title = re.sub(r'\s+(as follows|by substituting).+$', '', title, flags=re.IGNORECASE)
            return title.title()
        
        # Otherwise look for any heading that's not just a number or "EXHIBIT"
        headings = re.findall(r'^###?\s+(.+)$', content, re.MULTILINE)
        for heading in headings:
            heading = heading.strip()
            # Skip exhibit labels, numbers, and ordinance/resolution numbers
            if re.match(r'^(EXHIBIT|ORDINANCE|RESOLUTION|#)', heading, re.IGNORECASE):
                continue
            if re.match(r'^\d+', heading):
                continue
            # This looks like a real title
            return heading.title()
    except:
        pass
    
    # Fall back to filename-based title
    name = filepath.stem
    # Remove date prefix and doc type prefix
    name = re.sub(r'^\d{4}-\d{2}-\d{2}-RE-', '', name)
    name = re.sub(r'^\d{4}-(Ord|Res)-#?\d+[-\w]*-', '', name)
    name = name.replace('-', ' ').replace('_', ' ')
    return name.title()

def parse_document_name(filename):
    """Parse a document filename to extract year, number, and title."""
    stem = Path(filename).stem
    
    # Try to extract year from the beginning (YYYY format)
    year_match = re.match(r'^(\d{4})-(.+)', stem)
    if year_match:
        year = year_match.group(1)
        rest = year_match.group(2)
    else:
        year = "0000"  # Unknown year
        rest = stem
    
    # Try to extract ordinance/resolution number
    num_match = re.search(r'(Ord|Res)-#?(\d+[-\w]*)', rest)
    if num_match:
        doc_type = num_match.group(1)
        num = num_match.group(2)
    else:
        doc_type = ""
        num = ""
    
    # Clean up the title part
    title = rest
    title = re.sub(r'^(Ord|Res)-#?\d+[-\w]*-?', '', title)
    title = title.replace('-', ' ').strip()
    # Remove duplicate numbers at the end of titles
    title = re.sub(r'\s+\d+[-\w]*$', '', title)
    
    return {
        'year': int(year),
        'number': num,
        'type': doc_type,
        'title': title,
        'filename': filename
    }

def generate_summary():
    """Generate the SUMMARY.md file."""
    
    src_dir = Path("src")
    
    # Start with the introduction
    summary = ["# Summary\n"]
    summary.append("[Introduction](./introduction.md)\n")
    
    # Process Ordinances
    ord_dir = src_dir / "ordinances"
    if ord_dir.exists():
        ordinances = []
        for md_file in sorted(ord_dir.glob("*.md")):
            doc = parse_document_name(md_file.name)
            doc['full_title'] = extract_title_from_file(md_file)
            ordinances.append(doc)
        
        # Sort by year, then by number
        ordinances.sort(key=lambda x: (x['year'], x['number']))
        
        if ordinances:
            summary.append("\n---\n\n# Ordinances\n")
            for doc in ordinances:
                year = doc['year'] if doc['year'] != 0 else "Unknown"
                num = f"#{doc['number']}" if doc['number'] else ""
                title = doc['title'] or doc['full_title']
                
                # Style E format: #70 - WQRA (Year)
                # Use the extracted title from the file content if available
                clean_title = doc['full_title'] if doc['full_title'] else title
                if num:
                    display = f"{num} - {clean_title} ({year})"
                else:
                    display = f"{clean_title} ({year})"
                
                summary.append(f"- [{display}](./ordinances/{doc['filename']})\n")
    
    # Process Resolutions
    res_dir = src_dir / "resolutions"
    if res_dir.exists():
        resolutions = []
        for md_file in sorted(res_dir.glob("*.md")):
            doc = parse_document_name(md_file.name)
            doc['full_title'] = extract_title_from_file(md_file)
            resolutions.append(doc)
        
        resolutions.sort(key=lambda x: (x['year'], x['number']))
        
        if resolutions:
            summary.append("\n---\n\n# Resolutions\n")
            for doc in resolutions:
                year = doc['year'] if doc['year'] != 0 else "Unknown"
                num = f"#{doc['number']}" if doc['number'] else ""
                title = doc['title'] or doc['full_title']
                
                # Style E format
                clean_title = doc['full_title'] if doc['full_title'] else title
                if num:
                    display = f"{num} - {clean_title} ({year})"
                else:
                    display = f"{clean_title} ({year})"
                
                summary.append(f"- [{display}](./resolutions/{doc['filename']})\n")
    
    # Process Interpretations
    interp_dir = src_dir / "interpretations"
    if interp_dir.exists():
        interpretations = []
        for md_file in sorted(interp_dir.glob("*.md")):
            # Parse date from filename (YYYY-MM-DD format)
            name = md_file.stem
            date_match = re.match(r'^(\d{4}-\d{2}-\d{2})-(.+)', name)
            if date_match:
                date_str = date_match.group(1)
                rest = date_match.group(2)
                # Clean up the title
                rest = re.sub(r'^RE-', '', rest)
                rest = rest.replace('-', ' ').strip()
            else:
                date_str = ""
                rest = name.replace('-', ' ')
            
            interpretations.append({
                'date': date_str,
                'title': rest,
                'filename': md_file.name
            })
        
        # Sort by date
        interpretations.sort(key=lambda x: x['date'])
        
        if interpretations:
            summary.append("\n---\n\n# Planning Commission Interpretations\n")
            for doc in interpretations:
                # Extract just the year from date
                year = doc['date'][:4] if doc['date'] else "Unknown"
                # Style E format for interpretations
                display = f"{doc['title'].title()} ({doc['date']})"
                
                summary.append(f"- [{display}](./interpretations/{doc['filename']})\n")
    
    # Process Transcripts
    trans_dir = src_dir / "transcripts"
    if trans_dir.exists():
        transcripts = []
        for md_file in sorted(trans_dir.glob("*.md")):
            name = md_file.stem
            # Clean up the name for display
            clean_name = name.replace('-', ' ').replace('_', ' ')
            transcripts.append({
                'name': clean_name,
                'filename': md_file.name
            })
        
        if transcripts:
            summary.append("\n---\n\n# Council Meeting Transcripts\n")
            for doc in transcripts:
                summary.append(f"- [{doc['name']}](./transcripts/{doc['filename']})\n")
    
    # Write the SUMMARY.md file
    summary_file = src_dir / "SUMMARY.md"
    summary_file.write_text(''.join(summary), encoding='utf-8')
    print(f"Generated SUMMARY.md with {len(summary)} lines")

if __name__ == "__main__":
    generate_summary()