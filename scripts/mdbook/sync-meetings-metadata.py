#!/usr/bin/python3
"""
Sync meetings metadata from Airtable for the mdBook navigation.
Separate from governing documents to handle different table structure.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from pyairtable import Api

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Airtable API
api = Api(os.environ['AIRTABLE_API_KEY'])
base = api.base(os.environ['AIRTABLE_BASE_ID'])
table = base.table('Meetings_Metadata')

class MeetingsSync:
    def __init__(self, cache_file='book/meetings-metadata.json'):
        self.cache_file = Path(cache_file)
        
    def fetch_meetings_metadata(self):
        """Fetch all records from Meetings_Metadata table."""
        print("\n📊 Fetching Meetings Metadata")
        print("=" * 50)
        
        try:
            records = table.all()
            print(f"  ✓ Retrieved {len(records)} meeting records from Airtable")
            
            # Process records into our format
            meetings = {}
            for record in records:
                fields = record.get('fields', {})
                
                # Extract meeting type
                doc_type = fields.get('meeting_doc_type', [])
                if isinstance(doc_type, list) and len(doc_type) > 0:
                    doc_type = doc_type[0].lower()
                else:
                    doc_type = 'meeting'
                
                # Extract meeting date
                meeting_date = fields.get('meeting_date', [])
                if isinstance(meeting_date, list) and len(meeting_date) > 0:
                    meeting_date = meeting_date[0]
                
                # Try to extract key from URL if available (most reliable)
                md_url = fields.get('mdURL', '')
                if md_url and '/' in md_url:
                    # Extract filename from URL
                    filename = md_url.split('/')[-1]
                    # Remove .md extension to get the key
                    if filename.endswith('.md'):
                        key = filename[:-3]  # Remove .md extension
                    else:
                        key = filename
                else:
                    # Fall back to generating key from meeting_date and doc_type
                    # This is more reliable than display_name which may have wrong dates
                    if meeting_date and doc_type:
                        # Generate a key based on date and type
                        key = f"{meeting_date}-{doc_type.capitalize()}"
                    else:
                        # Last resort: try to use display_name
                        display_name = fields.get('display_name')
                        if isinstance(display_name, str) and '-' in display_name:
                            # e.g., "2018-05-14 - Agenda" -> "2018-05-14-Agenda"
                            key = display_name.replace(' - ', '-').replace(' ', '')
                        else:
                            key = 'unknown'
                
                # Handle display_name that might be a dict with error
                display_name = fields.get('display_name')
                if isinstance(display_name, dict):
                    # Skip records with errors in display_name
                    print(f"  ⚠️  Skipping record with error in display_name: {display_name}")
                    continue
                
                meetings[key] = {
                    'airtable_id': record.get('id'),
                    'display_name': display_name,
                    'short_title': fields.get('short_title'),
                    'meeting_doc_type': doc_type,
                    'meeting_date': meeting_date,
                    'year': fields.get('year'),
                    'md_url': fields.get('mdURL', ''),
                    'file_url': fields.get('fileURL', ''),
                    'status': fields.get('status', 'Unknown'),
                    'last_updated': fields.get('last_updated', datetime.now().isoformat())
                }
            
            return meetings
            
        except Exception as e:
            print(f"  ❌ Error fetching from Airtable: {e}")
            return {}
    
    def save_cache(self, data):
        """Save meetings metadata to cache file."""
        # Ensure directory exists
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        cache_data = {
            'metadata': {
                'cache_version': '1.0',
                'last_sync': datetime.now().isoformat(),
                'total_records': len(data)
            },
            'meetings': data
        }
        
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved {len(data)} meeting records to {self.cache_file}")
    
    def sync(self):
        """Main sync process."""
        meetings = self.fetch_meetings_metadata()
        if meetings:
            self.save_cache(meetings)
        return meetings

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Sync meetings metadata from Airtable')
    parser.add_argument('--cache-file', default='book/meetings-metadata.json',
                       help='Path to cache file')
    args = parser.parse_args()
    
    syncer = MeetingsSync(cache_file=args.cache_file)
    syncer.sync()

if __name__ == '__main__':
    main()