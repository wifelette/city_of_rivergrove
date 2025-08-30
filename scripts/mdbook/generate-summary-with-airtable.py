#!/usr/bin/env python3
"""
Generate SUMMARY.md for mdBook from documents in src/ directory with Airtable metadata integration.
This enhanced version uses Airtable metadata for better titles and information.
"""

import re
import json
from pathlib import Path
from datetime import datetime

def load_airtable_metadata():
    """Load Airtable metadata from cache file."""
    metadata_file = Path("src/airtable-metadata.json")
    if not metadata_file.exists():
        # Fallback to book directory
        metadata_file = Path("book/airtable-metadata.json")
    
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r') as f:
                data = json.load(f)
                return data.get('documents', {})
        except Exception as e:
            print(f"Warning: Could not load Airtable metadata: {e}")
    
    return {}

def get_document_key(filepath):
    """Get the document key for Airtable lookup from filepath."""
    # Remove extension and convert to key format
    stem = Path(filepath).stem
    
    # The metadata keys have # but src files don't
    # Need to add # back for Ord and Res files
    if '-Ord-' in stem:
        # Add # after Ord- (e.g., 2001-Ord-70-2001-WQRA -> 2001-Ord-#70-2001-WQRA)
        stem = re.sub(r'(-Ord-)(\d)', r'\1#\2', stem)
    elif '-Res-' in stem:
        # Add # after Res- (e.g., 2018-Res-259-Planning -> 2018-Res-#259-Planning)
        stem = re.sub(r'(-Res-)(\d)', r'\1#\2', stem)
    
    return stem

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
        elif 'Park Hours' in topic:
            return 'Park Hours'
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
    """Generate the SUMMARY.md file with Airtable metadata integration."""
    
    src_dir = Path("src")
    
    # Load Airtable metadata
    airtable_data = load_airtable_metadata()
    print(f"Loaded {len(airtable_data)} Airtable metadata records")
    
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
            
            # Check Airtable metadata
            doc_key = get_document_key(md_file)
            airtable_info = airtable_data.get(doc_key, {})
            
            # Get title from Airtable or fallback to filename
            if airtable_info.get('short_title'):
                title = airtable_info['short_title']
            elif airtable_info.get('display_name'):
                # Extract just the title part from display name
                display = airtable_info['display_name']
                title = re.sub(r'^(Ordinance|Resolution|Interpretation)\s+#?\d+\s*-?\s*', '', display)
            elif "Charter" in name or "charter" in name:
                title = "City Charter"
            else:
                title = name.replace('-', ' ').replace('_', ' ')
            
            others.append({
                'filename': md_file.name,
                'title': title,
                'year': year,
                'airtable': airtable_info
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
            
            # Get Airtable metadata
            doc_key = get_document_key(md_file)
            airtable_info = airtable_data.get(doc_key, {})
            
            # Use Airtable data if available - prioritize short_title
            if airtable_info:
                if airtable_info.get('short_title'):
                    # Use the exact short_title from Airtable
                    doc['full_title'] = airtable_info['short_title']
                elif airtable_info.get('display_name'):
                    # Extract title from display name as fallback
                    display = airtable_info['display_name']
                    title_part = re.sub(r'^Ordinance\s+#?\d+[-\w]*\s*-?\s*', '', display)
                    title_part = re.sub(r'\s*\(\d{4}\)$', '', title_part)  # Remove year
                    doc['full_title'] = title_part.strip() if title_part else extract_title_from_file(md_file)
                else:
                    # Fall back to extracting from file
                    doc['full_title'] = extract_title_from_file(md_file)
                
                # Use Airtable year if available
                if airtable_info.get('year'):
                    doc['year'] = airtable_info['year']
                
                # Use Airtable doc number if available
                # Handle compound numbers like "259-2018"
                if airtable_info.get('doc_number'):
                    doc_num = str(airtable_info['doc_number'])
                    # For resolutions, use the full number as-is
                    doc['number'] = doc_num
                    doc['display_number'] = doc_num  # Store for display formatting
                
                doc['status'] = airtable_info.get('status', 'Unknown')
                doc['special_state'] = airtable_info.get('special_state')
            else:
                doc['full_title'] = extract_title_from_file(md_file)
                doc['status'] = 'Unknown'
                doc['special_state'] = None
            
            ordinances.append(doc)
        
        # Sort by year, then by number
        ordinances.sort(key=lambda x: (x['year'], x['number']))
        
        if ordinances:
            summary.append("\n---\n\n# Ordinances\n")
            for doc in ordinances:
                year = doc['year'] if doc['year'] != 0 else "Unknown"
                num = f"#{doc['number']}" if doc['number'] else ""
                title = doc.get('full_title') or doc.get('title', 'Unknown')
                
                # Style E format: #70 - WQRA (Year)
                # Clean up the display number - remove duplicates
                clean_num = re.sub(r'^#(\d+)-.+', r'#\1', num) if num else ""
                
                # Add special state indicator if needed
                status_indicator = ""
                if doc.get('special_state') == 'Repealed':
                    status_indicator = " [REPEALED]"
                elif doc.get('special_state') == 'Superseded':
                    status_indicator = " [SUPERSEDED]"
                
                if clean_num:
                    display = f"{clean_num} - {title} ({year}){status_indicator}"
                else:
                    display = f"{title} ({year}){status_indicator}"
                
                summary.append(f"- [{display}](./ordinances/{doc['filename']})\n")
    
    # Process Resolutions
    res_dir = src_dir / "resolutions"
    if res_dir.exists():
        resolutions = []
        for md_file in sorted(res_dir.glob("*.md")):
            doc = parse_document_name(md_file.name)
            
            # Get Airtable metadata
            doc_key = get_document_key(md_file)
            airtable_info = airtable_data.get(doc_key, {})
            
            # Use Airtable data if available - prioritize short_title
            if airtable_info:
                if airtable_info.get('short_title'):
                    # Use the exact short_title from Airtable
                    doc['full_title'] = airtable_info['short_title']
                elif airtable_info.get('display_name'):
                    # Extract title from display name as fallback
                    display = airtable_info['display_name']
                    title_part = re.sub(r'^Resolution\s+#?\d+[-\w]*\s*-?\s*', '', display)
                    title_part = re.sub(r'\s*\(\d{4}\)$', '', title_part)  # Remove year
                    doc['full_title'] = title_part.strip() if title_part else extract_title_from_file(md_file)
                else:
                    # Fall back to extracting from file
                    doc['full_title'] = extract_title_from_file(md_file)
                
                # Use Airtable year if available
                if airtable_info.get('year'):
                    doc['year'] = airtable_info['year']
                
                # Use Airtable doc number if available
                # Handle compound numbers like "259-2018"
                if airtable_info.get('doc_number'):
                    doc_num = str(airtable_info['doc_number'])
                    # For resolutions, use the full number as-is
                    doc['number'] = doc_num
                    doc['display_number'] = doc_num  # Store for display formatting
                
                doc['status'] = airtable_info.get('status', 'Unknown')
            else:
                doc['full_title'] = extract_title_from_file(md_file)
                doc['status'] = 'Unknown'
            
            resolutions.append(doc)
        
        resolutions.sort(key=lambda x: (x['year'], x['number']))
        
        if resolutions:
            summary.append("\n---\n\n# Resolutions\n")
            for doc in resolutions:
                year = doc['year'] if doc['year'] != 0 else "Unknown"
                title = doc.get('full_title') or doc.get('title', 'Unknown')
                
                # Use display_number if available (for compound numbers like 259-2018)
                if doc.get('display_number'):
                    num = f"#{doc['display_number']}"
                elif doc.get('number'):
                    num = f"#{doc['number']}"
                else:
                    num = ""
                
                if num:
                    display = f"{num} - {title} ({year})"
                else:
                    display = f"{title} ({year})"
                
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
            
            # Get Airtable metadata
            doc_key = get_document_key(md_file)
            airtable_info = airtable_data.get(doc_key, {})
            
            # Use Airtable title if available
            if airtable_info.get('short_title'):
                title = airtable_info['short_title']
            elif airtable_info.get('display_name'):
                # Extract title from display name
                display = airtable_info['display_name']
                title = re.sub(r'^PC Interpretation\s*-?\s*', '', display)
            else:
                title = rest
            
            interpretations.append({
                'date': date_str,
                'title': title,
                'filename': md_file.name,
                'airtable': airtable_info
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
    
    # Process Meetings (Agendas, Minutes, Transcripts)
    meetings_added = False
    
    # Check for meetings metadata
    meetings_metadata_file = Path('book/meetings-metadata.json')
    meetings_metadata = {}
    if meetings_metadata_file.exists():
        with open(meetings_metadata_file, 'r') as f:
            data = json.load(f)
            meetings_metadata = data.get('meetings', {})
    
    # Process Agendas
    agendas_dir = src_dir / "agendas"
    if agendas_dir.exists():
        agendas = []
        for md_file in sorted(agendas_dir.glob("*.md")):
            # Check if in metadata
            file_key = md_file.stem
            if file_key in meetings_metadata:
                display = meetings_metadata[file_key].get('display_name', md_file.stem)
            else:
                display = md_file.stem.replace('-', ' ').replace('_', ' ')
            agendas.append({
                'display': display,
                'filename': md_file.name
            })
        
        if agendas:
            if not meetings_added:
                summary.append("\n---\n\n# Council Meetings\n")
                meetings_added = True
            summary.append("\n## Agendas\n")
            for doc in agendas:
                summary.append(f"- [{doc['display']}](./agendas/{doc['filename']})\n")
    
    # Process Minutes
    minutes_dir = src_dir / "minutes"
    if minutes_dir.exists():
        minutes = []
        for md_file in sorted(minutes_dir.glob("*.md")):
            # Check if in metadata
            file_key = md_file.stem
            if file_key in meetings_metadata:
                display = meetings_metadata[file_key].get('display_name', md_file.stem)
            else:
                display = md_file.stem.replace('-', ' ').replace('_', ' ')
            minutes.append({
                'display': display,
                'filename': md_file.name
            })
        
        if minutes:
            if not meetings_added:
                summary.append("\n---\n\n# Council Meetings\n")
                meetings_added = True
            summary.append("\n## Minutes\n")
            for doc in minutes:
                summary.append(f"- [{doc['display']}](./minutes/{doc['filename']})\n")
    
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
            if not meetings_added:
                summary.append("\n---\n\n# Council Meetings\n")
                meetings_added = True
            summary.append("\n## Transcripts\n")
            for doc in transcripts:
                summary.append(f"- [{doc['name']}](./transcripts/{doc['filename']})\n")
    
    # Write the SUMMARY.md file
    summary_file = src_dir / "SUMMARY.md"
    summary_file.write_text(''.join(summary), encoding='utf-8')
    print(f"Generated SUMMARY.md with {len(summary)} lines using Airtable metadata")

if __name__ == "__main__":
    generate_summary()