#!/usr/bin/env python3
"""
Generate SUMMARY.md for mdBook from the documents in src/ directory.
This script automatically creates the table of contents based on existing files.
"""

import re
from pathlib import Path
from datetime import datetime

def extract_title_from_file(filepath):
    """Extract a clean, concise title from the markdown file or filename."""
    # First try to get a short title from the filename
    stem = Path(filepath).stem
    
    # Extract the topic from filename (e.g., "1974-Ord-#16-Parks" -> "Parks")
    filename_match = re.search(r'-([^-]+)$', stem)
    if filename_match:
        topic = filename_match.group(1)
        # Clean up the topic
        topic = topic.replace('-', ' ').replace('_', ' ')
        
        # Handle special cases - be more descriptive
        if 'WQRA' in topic:
            return 'Water Quality Resource Area'
        elif 'FEMA' in topic:
            return 'FEMA Flood Map'
        elif 'Land Development' in topic and 'Amendment' in topic:
            return 'Land Development Amendment'
        elif 'Land Development' in topic:
            return 'Land Development'
        elif 'Sewer' in topic:
            return 'Sewer Services'
        elif 'Metro Compliance' in topic:
            return 'Metro Compliance'
        elif 'Title 3' in topic:
            return 'Title 3 Compliance'
        elif 'Gates' in topic:
            return 'Gates Ordinance'
        elif 'Penalties' in topic:
            return 'Penalties & Abatement'
        elif 'Conditional Use' in topic:
            return 'Conditional Use'
        elif 'Tree Cutting' in topic:
            return 'Tree Cutting'
        elif 'Sign' in topic:
            return 'Sign Ordinance'
        elif 'Docks' in topic:
            return 'Docks Amendment'
        elif 'Parks' in topic:
            return 'Parks Advisory'
        elif 'Flood' in topic and 'Amendment' in stem:
            return 'Flood & Land Development'
        elif 'Flood' in topic:
            return 'Flood Prevention'
        elif 'Manufactured' in topic:
            return 'Manufactured Homes'
        elif 'Municipal Services' in topic:
            return 'Municipal Services'
        elif 'PC' in topic or 'Planning' in topic:
            return 'Planning Commission'
        else:
            # Return cleaned topic title
            return topic.title()
    
    # Fall back to extracting from file content
    try:
        content = filepath.read_text(encoding='utf-8')
        
        # Look for a heading that starts with "AN ORDINANCE" or "A RESOLUTION"
        subject_match = re.search(r'^###?\s+AN?\s+(ORDINANCE|RESOLUTION)\s+(.+)$', content, re.MULTILINE | re.IGNORECASE)
        if subject_match:
            title = subject_match.group(2).strip()
            # Keep titles very short
            title = re.sub(r'^(ESTABLISHING|CREATING|AMENDING|ADOPTING|PROVIDING|DEFINING|RELATING TO)\s+', '', title, flags=re.IGNORECASE)
            # Truncate at first comma or "AND"
            title = re.sub(r'\s+(,|AND|TO).+$', '', title, flags=re.IGNORECASE)
            # Remove articles
            title = re.sub(r'^(THE|A|AN)\s+', '', title, flags=re.IGNORECASE)
            # Keep it short
            words = title.split()[:3]  # Max 3 words
            return ' '.join(words).title()
    except:
        pass
    
    # Ultimate fallback
    name = filepath.stem
    name = re.sub(r'^\d{4}-(Ord|Res)-#?\d+[-\w]*-', '', name)
    name = name.replace('-', ' ').replace('_', ' ')
    return name.title()[:20]  # Limit to 20 characters

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
    
    # Process Other/Foundational Documents
    other_dir = src_dir / "other"
    if other_dir.exists():
        others = []
        for md_file in sorted(other_dir.glob("*.md")):
            # Extract year and title from filename
            name = md_file.stem
            year_match = re.search(r'(\d{4})', name)
            year = year_match.group(1) if year_match else ""
            
            # Get title from filename
            if "Charter" in name or "charter" in name:
                title = "City Charter"
            else:
                title = name.replace('-', ' ').replace('_', ' ')
            
            others.append({
                'filename': md_file.name,
                'title': title,
                'year': year
            })
        
        if others:
            summary.append("\n---\n\n# Foundational Documents\n")
            for doc in others:
                if doc['year']:
                    display = f"{doc['title']} ({doc['year']})"
                else:
                    display = doc['title']
                summary.append(f"- [{display}](./other/{doc['filename']})\n")
    
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
                # Clean up the display number - remove duplicates
                clean_num = re.sub(r'^#(\d+)-.+', r'#\1', num) if num else ""
                
                # Use the extracted title
                clean_title = doc['full_title'] if doc['full_title'] else title
                if clean_num:
                    display = f"{clean_num} - {clean_title} ({year})"
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
                # Clean up the display number - remove duplicates
                clean_num = re.sub(r'^#(\d+)-.+', r'#\1', num) if num else ""
                
                clean_title = doc['full_title'] if doc['full_title'] else title
                if clean_num:
                    display = f"{clean_num} - {clean_title} ({year})"
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
    
    # Process Meeting Documents (Agendas, Minutes, Transcripts)
    
    # Process Agendas
    agenda_dir = src_dir / "agendas"
    if agenda_dir.exists():
        agendas = []
        for md_file in sorted(agenda_dir.glob("*.md")):
            name = md_file.stem
            # Parse date from filename (YYYY-MM-DD-Agenda format)
            date_match = re.match(r'^(\d{4}-\d{2}-\d{2})-Agenda', name)
            if date_match:
                date_str = date_match.group(1)
                # Convert to readable format
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    display_date = date_obj.strftime('%B %d, %Y')
                except:
                    display_date = date_str
            else:
                display_date = name.replace('-', ' ')
            
            agendas.append({
                'date': date_str if date_match else name,
                'display': display_date,
                'filename': md_file.name
            })
        
        # Sort by date
        agendas.sort(key=lambda x: x['date'], reverse=True)
        
        if agendas:
            summary.append("\n---\n\n# Meeting Agendas\n")
            for doc in agendas:
                summary.append(f"- [{doc['display']}](./agendas/{doc['filename']})\n")
    
    # Process Minutes
    minutes_dir = src_dir / "minutes"
    if minutes_dir.exists():
        minutes = []
        for md_file in sorted(minutes_dir.glob("*.md")):
            name = md_file.stem
            # Parse date from filename (YYYY-MM-DD-Minutes format)
            date_match = re.match(r'^(\d{4}-\d{2}-\d{2})-Minutes', name)
            if date_match:
                date_str = date_match.group(1)
                # Convert to readable format
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    display_date = date_obj.strftime('%B %d, %Y')
                except:
                    display_date = date_str
            else:
                display_date = name.replace('-', ' ')
            
            minutes.append({
                'date': date_str if date_match else name,
                'display': display_date,
                'filename': md_file.name
            })
        
        # Sort by date
        minutes.sort(key=lambda x: x['date'], reverse=True)
        
        if minutes:
            summary.append("\n---\n\n# Meeting Minutes\n")
            for doc in minutes:
                summary.append(f"- [{doc['display']}](./minutes/{doc['filename']})\n")
    
    # Process Transcripts
    trans_dir = src_dir / "transcripts"
    if trans_dir.exists():
        transcripts = []
        for md_file in sorted(trans_dir.glob("*.md")):
            name = md_file.stem
            # Parse date from filename (YYYY-MM-DD-Transcript format)
            date_match = re.match(r'^(\d{4}-\d{2}-\d{2})-Transcript', name)
            if date_match:
                date_str = date_match.group(1)
                # Convert to readable format
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    display_date = date_obj.strftime('%B %d, %Y')
                except:
                    display_date = date_str
            else:
                display_date = name.replace('-', ' ')
            
            transcripts.append({
                'date': date_str if date_match else name,
                'display': display_date,
                'filename': md_file.name
            })
        
        # Sort by date
        transcripts.sort(key=lambda x: x['date'], reverse=True)
        
        if transcripts:
            summary.append("\n---\n\n# Meeting Transcripts\n")
            for doc in transcripts:
                summary.append(f"- [{doc['display']}](./transcripts/{doc['filename']})\n")
    
    # Write the SUMMARY.md file
    summary_file = src_dir / "SUMMARY.md"
    summary_file.write_text(''.join(summary), encoding='utf-8')
    print(f"Generated SUMMARY.md with {len(summary)} lines")

if __name__ == "__main__":
    generate_summary()