#!/usr/bin/env python3
"""
Generate relationships.json file by analyzing document cross-references.
This creates a comprehensive mapping of document relationships including:
- Amendments
- References
- Interpretations
- Related documents
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Set

def extract_document_references(content: str) -> Dict[str, Set[str]]:
    """Extract all document references from markdown content."""
    references = {
        'ordinances': set(),
        'resolutions': set(),
        'interpretations': set()
    }
    
    # Find ordinance references (various patterns)
    # Pattern 1: Ordinance #XX or Ordinance No. XX
    ord_patterns = [
        r'Ordinance\s+(?:No\.|#)\s*(\d+[-\w]*)',
        r'Ord\.\s+(?:No\.|#)\s*(\d+[-\w]*)',
        r'#(\d+[-\w]*)\s*(?:ordinance|Ordinance)',
    ]
    
    for pattern in ord_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            references['ordinances'].add(match)
    
    # Find resolution references
    res_patterns = [
        r'Resolution\s+(?:No\.|#)\s*(\d+[-\w]*)',
        r'Res\.\s+(?:No\.|#)\s*(\d+[-\w]*)',
    ]
    
    for pattern in res_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            references['resolutions'].add(match)
    
    # Find section references (which might be interpretations)
    section_patterns = [
        r'Section\s+(\d+\.\d+[A-Z]?)',
        r'§\s*(\d+\.\d+[A-Z]?)',
    ]
    
    for pattern in section_patterns:
        matches = re.findall(pattern, content)
        for match in matches:
            references['interpretations'].add(match)
    
    return references

def parse_document_id(filepath: Path) -> Dict:
    """Parse document ID and type from filepath."""
    name = filepath.stem
    
    # Ordinances: Pattern YYYY-Ord-XX-Topic (# removed in src)
    if 'Ord-' in name:
        match = re.search(r'(\d{4})-Ord-(\d+[-\w]*)', name)
        if match:
            return {
                'type': 'ordinance',
                'id': match.group(2),
                'year': match.group(1),
                'file': filepath.name
            }
    
    # Resolutions: Pattern YYYY-Res-XX-Topic (# removed in src)
    if 'Res-' in name:
        match = re.search(r'(\d{4})-Res-(\d+[-\w]*)', name)
        if match:
            return {
                'type': 'resolution',
                'id': match.group(2),
                'year': match.group(1),
                'file': filepath.name
            }
    
    # Interpretations: Pattern YYYY-MM-DD-RE-section
    if 'RE-' in name or filepath.parent.name == 'interpretations':
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', name)
        section_match = re.search(r'RE-(.+)', name)
        
        return {
            'type': 'interpretation',
            'date': date_match.group(1) if date_match else None,
            'section': section_match.group(1) if section_match else None,
            'file': filepath.name
        }
    
    # Meeting documents: Transcripts, Agendas, Minutes
    if 'Transcript' in name or filepath.parent.name == 'transcripts':
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', name)
        return {
            'type': 'transcript',
            'date': date_match.group(1) if date_match else name.replace('-Transcript', ''),
            'file': filepath.name
        }
    
    if 'Agenda' in name or filepath.parent.name == 'agendas':
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', name)
        return {
            'type': 'agenda',
            'date': date_match.group(1) if date_match else name.replace('-Agenda', ''),
            'file': filepath.name
        }
    
    if 'Minutes' in name or filepath.parent.name == 'minutes':
        date_match = re.match(r'(\d{4}-\d{2}-\d{2})', name)
        return {
            'type': 'minutes',
            'date': date_match.group(1) if date_match else name.replace('-Minutes', ''),
            'file': filepath.name
        }
    
    # Other documents: Pattern YYYY-Topic (e.g., 1974-City-Charter)
    if filepath.parent.name == 'other':
        year_match = re.match(r'(\d{4})-(.+)', name)
        if year_match:
            return {
                'type': 'other',
                'id': name,
                'year': year_match.group(1),
                'file': filepath.name
            }
    
    return None

def identify_amendments(doc_id: str, content: str) -> List[str]:
    """Identify if this document amends another."""
    amendments = []
    
    # Look for explicit amendment language
    amend_patterns = [
        r'amend(?:s|ing)?\s+Ordinance\s+(?:No\.|#)\s*(\d+[-\w]*)',
        r'amendment\s+to\s+Ordinance\s+(?:No\.|#)\s*(\d+[-\w]*)',
    ]
    
    for pattern in amend_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        amendments.extend(matches)
    
    return list(set(amendments))

def build_relationships():
    """Build comprehensive document relationships."""
    relationships = {}
    all_documents = {}
    
    # Load meetings metadata to filter meeting documents
    meetings_metadata = {}
    meetings_metadata_file = Path('book/meetings-metadata.json')
    if meetings_metadata_file.exists():
        try:
            with open(meetings_metadata_file, 'r') as f:
                data = json.load(f)
                meetings_metadata = data.get('meetings', {})
        except:
            pass
    
    # Process all markdown files from src directory
    for dir_name in ['ordinances', 'resolutions', 'interpretations', 'other', 'transcripts', 'agendas', 'minutes']:
        dir_path = Path('src') / dir_name
        if not dir_path.exists():
            continue
        
        for md_file in dir_path.glob('*.md'):
            # For meeting documents, only include if they have metadata
            if dir_name in ['transcripts', 'agendas', 'minutes']:
                # Try both exact match and lowercase for backwards compatibility
                file_key = md_file.stem
                file_key_lower = md_file.stem.lower()
                if file_key not in meetings_metadata and file_key_lower not in meetings_metadata:
                    print(f"  Skipping {md_file.name} - no metadata entry")
                    continue
            
            doc_info = parse_document_id(md_file)
            if not doc_info:
                continue
            
            # Read content
            try:
                content = md_file.read_text(encoding='utf-8')
            except:
                continue
            
            # Extract title from content
            title_match = re.search(r'^###?\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else md_file.stem
            
            # Store document info
            doc_key = f"{doc_info['type']}-{doc_info.get('id') or doc_info.get('date') or doc_info.get('section') or 'unknown'}"
            all_documents[doc_key] = {
                'type': doc_info['type'],
                'id': doc_info.get('id'),
                'date': doc_info.get('date'),
                'year': doc_info.get('year'),
                'section': doc_info.get('section'),
                'title': title,
                'file': doc_info['file']
            }
            
            # Extract references
            refs = extract_document_references(content)
            
            # Check for amendments
            if doc_info['type'] == 'ordinance':
                amendments = identify_amendments(doc_info['id'], content)
                if amendments:
                    refs['amends'] = amendments
            
            # Store relationships
            if any(refs.values()):
                relationships[doc_key] = {
                    'references': list(refs.get('ordinances', [])),
                    'resolutions': list(refs.get('resolutions', [])),
                    'interpretations': list(refs.get('interpretations', [])),
                    'amends': refs.get('amends', [])
                }
    
    # Build reverse relationships (referenced_by)
    relationships_copy = dict(relationships)
    for doc_key, doc_refs in relationships_copy.items():
        # Add referenced_by for ordinances
        for ord_id in doc_refs.get('references', []):
            ref_key = f"ordinance-{ord_id}"
            if ref_key in relationships:
                if 'referenced_by' not in relationships[ref_key]:
                    relationships[ref_key]['referenced_by'] = []
                relationships[ref_key]['referenced_by'].append(doc_key)
        
        # Add amended_by for documents that are amended
        for ord_id in doc_refs.get('amends', []):
            ref_key = f"ordinance-{ord_id}"
            if ref_key not in relationships:
                relationships[ref_key] = {}
            if 'amended_by' not in relationships[ref_key]:
                relationships[ref_key]['amended_by'] = []
            relationships[ref_key]['amended_by'].append(doc_key)
    
    # Identify related documents (same topic/theme)
    topics = {}
    for doc_key, doc in all_documents.items():
        # Extract topic from title
        title_lower = doc['title'].lower()
        
        # Common topics
        if any(word in title_lower for word in ['flood', 'water', 'wqra']):
            topic = 'water_environmental'
        elif any(word in title_lower for word in ['park', 'recreation']):
            topic = 'parks_recreation'
        elif any(word in title_lower for word in ['land', 'development', 'zone', 'zoning']):
            topic = 'land_development'
        elif any(word in title_lower for word in ['gate', 'access']):
            topic = 'access_control'
        elif any(word in title_lower for word in ['penalty', 'penalties', 'enforcement', 'abate']):
            topic = 'enforcement'
        elif any(word in title_lower for word in ['dock', 'river', 'marine']):
            topic = 'waterfront'
        else:
            topic = 'general'
        
        if topic not in topics:
            topics[topic] = []
        topics[topic].append(doc_key)
    
    # Add related documents to relationships
    for topic, doc_keys in topics.items():
        if len(doc_keys) > 1:
            for doc_key in doc_keys:
                if doc_key not in relationships:
                    relationships[doc_key] = {}
                # Add other documents in same topic as related
                related = [dk for dk in doc_keys if dk != doc_key]
                if related:
                    relationships[doc_key]['related'] = related
    
    # Create final output structure
    output = {
        'documents': all_documents,
        'relationships': relationships,
        'topics': topics,
        'metadata': {
            'generated': str(Path(__file__).stat().st_mtime),
            'total_documents': len(all_documents),
            'total_relationships': len(relationships)
        }
    }
    
    return output

def main():
    """Generate the relationships JSON file."""
    print("🔍 Analyzing document relationships...")
    
    relationships = build_relationships()
    
    # Write to JSON file
    output_path = Path('src/relationships.json')
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(relationships, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Generated relationships.json with {relationships['metadata']['total_documents']} documents")
    print(f"   Found {relationships['metadata']['total_relationships']} documents with relationships")
    print(f"   Topics identified: {len(relationships['topics'])}")
    
    # Print sample relationships
    print("\n📊 Sample relationships:")
    for doc_key, rels in list(relationships['relationships'].items())[:3]:
        if doc_key in relationships['documents']:
            doc = relationships['documents'][doc_key]
            print(f"\n   {doc.get('id', doc.get('date'))} - {doc['title'][:30]}...")
            if rels.get('amends'):
                print(f"      Amends: {rels['amends']}")
            if rels.get('amended_by'):
                print(f"      Amended by: {rels['amended_by']}")
            if rels.get('references'):
                print(f"      References: {rels['references'][:3]}")
            if rels.get('referenced_by'):
                print(f"      Referenced by: {rels['referenced_by'][:3]}")

if __name__ == "__main__":
    main()