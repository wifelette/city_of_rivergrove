#!/usr/bin/env python3
"""
Sync Airtable Public Metadata with local document repository.
Handles both full sync and incremental updates with smart caching.
Reports mismatches between Airtable and local files for correction.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import re

# Load environment variables for Airtable API
from dotenv import load_dotenv
load_dotenv()

# Initialize Airtable API
from pyairtable import Api
api = Api(os.environ['AIRTABLE_API_KEY'])
base = api.base(os.environ['AIRTABLE_BASE_ID'])
table = base.table(os.environ.get('AIRTABLE_TABLE_NAME', 'Public Metadata'))

class AirtableSync:
    def __init__(self, cache_file='book/airtable-metadata.json', 
                 relationships_file='book/relationships.json'):
        self.cache_file = Path(cache_file)
        self.relationships_file = Path(relationships_file)
        self.cache_max_age_hours = 24
        self.mismatches = {
            'missing_in_airtable': [],
            'missing_locally': [],
            'filename_conflicts': []
        }
        
    def extract_document_info(self, filename: str) -> Dict:
        """Extract type, year, and number from local document filename."""
        # Remove path and extension
        name = Path(filename).stem
        
        # Match patterns like:
        # 2024-Res-#300-Fee-Schedule-Modification
        # 1978-Ord-#28-Parks
        # 1997-07-07-RE-2.040h-permitting-adus
        # 1974-City-Charter (special case)
        
        info = {
            'type': None,
            'year': None,
            'number': None,
            'normalized_key': name.lower().replace('#', '').replace('-', '')
        }
        
        # Extract year (first 4 digits)
        year_match = re.match(r'^(\d{4})', name)
        if year_match:
            info['year'] = int(year_match.group(1))
        
        # Determine type and extract number
        if '-Ord-' in name:
            info['type'] = 'ordinance'
            # Extract number after Ord-# (handle patterns like #74-2004, #73-2003A, #28, etc.)
            num_match = re.search(r'-Ord-#?(\d+(?:-\d+)?[A-Z]?)', name)
            if num_match:
                info['number'] = num_match.group(1)
        elif '-Res-' in name:
            info['type'] = 'resolution'
            # Extract number after Res-# (handle patterns like #300-2024, #259, #41425, etc.)  
            num_match = re.search(r'-Res-#?(\d+(?:-\d+)?)', name)
            if num_match:
                info['number'] = num_match.group(1)
        elif '-RE-' in name:
            info['type'] = 'interpretation'
            # For interpretations, use the full pattern after RE- as "number"
            re_match = re.search(r'-RE-(.+)', name)
            if re_match:
                info['number'] = re_match.group(1)
        elif 'City-Charter' in name:
            info['type'] = 'other'
            info['number'] = ''
        
        return info
    
    def match_documents_by_url(self, airtable_record: Dict, local_file: str) -> bool:
        """Check if an Airtable record matches a local document by URL."""
        # If Airtable has a mdURL, use it for exact matching
        md_url = airtable_record.get('md_url', '')
        if md_url:
            # Extract the path from URL and compare with local filename
            # The URL contains the full path like .../Ordinances/2001-Ord-#70-2001-WQRA.md
            if local_file in md_url:
                return True
            
            # Special case for 54-89C: URL has 54-89-C but file is 54-89C
            if '54-89-C' in md_url and '54-89C' in local_file:
                return True
            
            # Also try matching just the filename from the URL
            airtable_filename = airtable_record.get('filename')
            if airtable_filename and airtable_filename == local_file:
                return True
        
        # Fall back to the old matching logic if no URL
        # This ensures backward compatibility
        return False
    
    def match_documents(self, airtable_record: Dict, local_doc_info: Dict) -> bool:
        """Check if an Airtable record matches a local document (legacy method)."""
        # This is the fallback for records without URLs
        # Keep the complex logic for backward compatibility
        
        # Match by type first
        if airtable_record.get('type') != local_doc_info.get('type'):
            return False
        
        # Special handling for "other" type (City Charter)
        if local_doc_info['type'] == 'other':
            return airtable_record.get('year') == local_doc_info.get('year')
            
        # For ordinances and resolutions, match by doc number
        if local_doc_info['type'] in ['ordinance', 'resolution']:
            airtable_num = str(airtable_record.get('doc_number', '')).replace('#', '').strip().upper()
            local_num = str(local_doc_info.get('number', '')).replace('#', '').strip().upper()
            
            # Special case for 54-89C matching 54-89-C or vice versa
            # Remove all hyphens for comparison if one ends with a letter
            if (airtable_num and airtable_num[-1].isalpha()) or (local_num and local_num[-1].isalpha()):
                airtable_clean = airtable_num.replace('-', '')
                local_clean = local_num.replace('-', '')
                if airtable_clean == local_clean:
                    return True
            
            # Handle year in doc number
            if '-' in airtable_num and '-' not in local_num:
                airtable_base = airtable_num.split('-')[0]
                if airtable_base == local_num:
                    return True
            elif '-' in local_num and '-' not in airtable_num:
                local_base = local_num.split('-')[0]
                if local_base == airtable_num:
                    return True
            
            # Exact match
            return airtable_num == local_num
        
        # For interpretations, match by year
        elif local_doc_info['type'] == 'interpretation':
            return airtable_record.get('year') == local_doc_info.get('year')
        
        return False
    
    def load_local_documents(self) -> Dict[str, Dict]:
        """Load all local documents from relationships.json."""
        if not self.relationships_file.exists():
            print(f"  ⚠️  relationships.json not found at {self.relationships_file}")
            return {}
            
        with open(self.relationships_file, 'r') as f:
            data = json.load(f)
            
        documents = {}
        for key, doc in data.get('documents', {}).items():
            if 'file' in doc:
                # Extract document info from filename
                doc_info = self.extract_document_info(doc['file'])
                
                documents[key] = {
                    'key': key,
                    'type': doc.get('type'),
                    'year': doc.get('year'),
                    'title': doc.get('title'),
                    'file': doc.get('file'),
                    'extracted_info': doc_info
                }
                
        return documents
    
    def fetch_airtable_records(self, filter_formula: Optional[str] = None) -> List[Dict]:
        """
        Fetch records from Airtable Public Metadata table.
        """
        try:
            print("  ☁️  Fetching from Airtable API...")
            
            if filter_formula:
                print(f"    Using filter: {filter_formula}")
                records = table.all(formula=filter_formula)
            else:
                records = table.all()
            
            print(f"  ✓ Retrieved {len(records)} records from Airtable")
            return [self.process_airtable_record(r) for r in records]
            
        except Exception as e:
            print(f"  ❌ Error fetching from Airtable: {e}")
            print("  📝 Check your API credentials and table name")
            
            # Return empty list to allow script to continue
            # This will show all local docs as "missing in Airtable"
            return []
    
    def process_airtable_record(self, record: Dict) -> Dict:
        """Process raw Airtable record into our cache format."""
        fields = record.get('fields', {})
        
        # Extract type - handle it being a list
        doc_type = fields.get('type', [])
        if isinstance(doc_type, list) and len(doc_type) > 0:
            doc_type = doc_type[0].lower()
        elif isinstance(doc_type, str):
            doc_type = doc_type.lower()
        else:
            doc_type = 'unknown'
        
        # Extract year and doc_number (if they exist)
        year = fields.get('year')
        doc_number = fields.get('doc_number', '')
        
        # Extract filename from mdURL if available
        md_url = fields.get('mdURL', '')
        filename = None
        if md_url:
            # Extract filename from URL like .../blob/main/Ordinances/2001-Ord-#70-2001-WQRA.md
            parts = md_url.split('/blob/main/')
            if len(parts) == 2:
                path = parts[1]
                filename = Path(path).name
        
        # Handle fields that might be lists
        digitized = fields.get('digitized', [False])
        if isinstance(digitized, list):
            digitized = digitized[0] if digitized else False
            
        passed_date = fields.get('passed_date', [None])
        if isinstance(passed_date, list):
            passed_date = passed_date[0] if passed_date else None
        
        return {
            'airtable_id': record.get('id'),
            'display_name': fields.get('display_name'),
            'short_title': fields.get('short_title'),
            'type': doc_type,
            'year': year,
            'doc_number': doc_number,
            'md_url': md_url,
            'file_url': fields.get('fileURL', ''),
            'filename': filename,
            'status': fields.get('status', 'Unknown'),
            'special_state': fields.get('special_state'),
            'digitized': digitized,
            'passed_date': passed_date,
            'last_updated': fields.get('last_updated', datetime.now().isoformat())
        }
    
    def should_refresh_cache(self, force: bool = False) -> bool:
        """Check if cache needs refreshing."""
        if force:
            return True
            
        if not self.cache_file.exists():
            print("  ℹ️  No cache file found, will create new one")
            return True
            
        # Check age
        cache_age = time.time() - self.cache_file.stat().st_mtime
        max_age_seconds = self.cache_max_age_hours * 3600
        
        if cache_age > max_age_seconds:
            age_hours = cache_age / 3600
            print(f"  ⏰ Cache is {age_hours:.1f} hours old (max: {self.cache_max_age_hours})")
            return True
            
        print(f"  ✓ Cache is fresh ({cache_age/3600:.1f} hours old)")
        return False
    
    def load_cache(self) -> Dict:
        """Load existing cache file."""
        if not self.cache_file.exists():
            return {
                'metadata': {
                    'cache_version': '1.1',
                    'total_records': 0
                },
                'documents': {}
            }
            
        with open(self.cache_file, 'r') as f:
            return json.load(f)
    
    def save_cache(self, data: Dict):
        """Save cache file."""
        # Ensure directory exists
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Update metadata
        data['metadata']['last_updated'] = datetime.now().isoformat()
        data['metadata']['total_records'] = len(data['documents'])
        
        with open(self.cache_file, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def full_sync(self, force: bool = False):
        """Perform full sync of all documents."""
        print("\n📊 Full Airtable Sync")
        print("=" * 50)
        
        if not self.should_refresh_cache(force):
            print("  ℹ️  Using cached data (use --force to refresh)")
            return
        
        # Load local documents
        print("\n📁 Loading local documents...")
        local_docs = self.load_local_documents()
        print(f"  ✓ Found {len(local_docs)} local documents")
        
        # Fetch from Airtable
        print("\n☁️  Fetching from Airtable...")
        airtable_records = self.fetch_airtable_records()
        print(f"  ✓ Found {len(airtable_records)} Airtable records")
        
        # Process and match records
        cache_data = {
            'metadata': {
                'cache_version': '1.1',
                'last_full_sync': datetime.now().isoformat()
            },
            'documents': {}
        }
        
        # Track what we've matched
        matched_local = set()
        matched_airtable = set()
        
        # Match Airtable records to local files
        print("\n🔍 Attempting to match records...")
        for record in airtable_records:
            # Try to find matching local document
            local_match = None
            
            # First try URL-based matching (most accurate)
            if record.get('md_url'):
                for local_key, local_doc in local_docs.items():
                    if self.match_documents_by_url(record, local_doc['file']):
                        local_match = local_doc
                        matched_local.add(local_key)
                        print(f"  ✅ Matched by URL: {record['display_name']} → {local_match['file']}")
                        break
            
            # If no URL match, fall back to legacy matching
            if not local_match:
                for local_key, local_doc in local_docs.items():
                    if self.match_documents(record, local_doc['extracted_info']):
                        local_match = local_doc
                        matched_local.add(local_key)
                        print(f"  ✅ Matched by pattern: {record['display_name']} → {local_match['file']}")
                        break
            
            if local_match:
                # Store with local filename as key for consistency
                cache_key = local_match['file'].replace('.md', '')
                cache_data['documents'][cache_key] = record
                matched_airtable.add(record['airtable_id'])
            else:
                # Document in Airtable but not locally
                if record.get('md_url'):
                    print(f"  ❓ No match: {record['display_name']} (URL: {record.get('md_url')})")
                else:
                    print(f"  ❓ No match: {record['display_name']} (Type: {record['type']}, Year: {record['year']}, Num: {record.get('doc_number')})")
                self.mismatches['missing_locally'].append({
                    'airtable_id': record['airtable_id'],
                    'display_name': record['display_name'],
                    'type': record['type'],
                    'year': record['year'],
                    'doc_number': record.get('doc_number'),
                    'md_url': record.get('md_url', '')
                })
        
        # Find local documents not in Airtable
        for local_key, local_doc in local_docs.items():
            if local_key not in matched_local:
                self.mismatches['missing_in_airtable'].append({
                    'file': local_doc['file'],
                    'type': local_doc['type'],
                    'title': local_doc['title']
                })
        
        # Save cache
        self.save_cache(cache_data)
        
        # Report results
        self.report_sync_results(
            len(local_docs),
            len(airtable_records),
            len(matched_local)
        )
    
    def incremental_update(self, filename: str, create_if_missing: bool = False):
        """Update cache for a single document."""
        print(f"\n📄 Incremental Update: {filename}")
        print("=" * 50)
        
        # Load existing cache
        cache = self.load_cache()
        
        # Extract document info from filename
        doc_info = self.extract_document_info(filename)
        
        # Search for this document in Airtable
        print(f"  🔍 Searching Airtable for: {doc_info}")
        
        # Get all records and search through them
        all_records = self.fetch_airtable_records()
        matching_records = [
            r for r in all_records 
            if self.match_documents(r, doc_info)
        ]
        
        if matching_records:
            record = matching_records[0]
            print(f"  ✓ Found in Airtable: {record['display_name']}")
            
            # Update cache
            cache_key = filename.replace('.md', '')
            cache['documents'][cache_key] = record
            cache['metadata']['last_partial_update'] = datetime.now().isoformat()
            
            # Track incremental updates
            if 'incremental_updates' not in cache['metadata']:
                cache['metadata']['incremental_updates'] = []
            cache['metadata']['incremental_updates'].append({
                'filename': filename,
                'updated_at': datetime.now().isoformat()
            })
            
            # Keep only last 50 incremental updates
            cache['metadata']['incremental_updates'] = \
                cache['metadata']['incremental_updates'][-50:]
            
            self.save_cache(cache)
            print("  ✓ Cache updated")
            
        elif create_if_missing:
            print(f"  ⚠️  Not found in Airtable")
            print(f"     Creating provisional entry")
            
            # Create provisional entry
            cache_key = filename.replace('.md', '')
            cache['documents'][cache_key] = {
                'filename': filename,
                'display_name': self.generate_display_name(filename),
                'status': 'Draft',
                'provisional': True,
                'created_at': datetime.now().isoformat()
            }
            
            self.save_cache(cache)
            print("  ✓ Provisional entry created")
            
        else:
            print(f"  ❌ Not found in Airtable and --create-if-missing not set")
            sys.exit(1)
    
    def generate_display_name(self, filename: str) -> str:
        """Generate a display name from filename."""
        name = Path(filename).stem
        
        # Extract parts from filename pattern
        # e.g., "2024-Res-#300-Fee-Schedule-Modification"
        parts = name.split('-')
        
        if 'Ord' in name:
            doc_type = "Ordinance"
        elif 'Res' in name:
            doc_type = "Resolution"
        elif 'RE' in name:
            doc_type = "Interpretation"
        else:
            doc_type = "Document"
        
        # Try to extract number and year
        year_match = re.match(r'^(\d{4})', name)
        
        # Look for number after Ord/Res, not just any digits
        # Pattern: YYYY-Ord-#NUMBER-... or YYYY-Res-#NUMBER-...
        if 'Ord' in name or 'Res' in name:
            num_match = re.search(r'(?:Ord|Res)-#?(\d+(?:-\d+)?[A-Z]?)', name)
        else:
            num_match = re.search(r'#?(\d+)', name)
        
        if year_match and num_match:
            year = year_match.group(1)
            num = num_match.group(1)
            
            # Get topic from remaining parts
            # Find where the number ends to get the topic
            num_end_idx = name.find(num) + len(num)
            remaining = name[num_end_idx:].lstrip('-')
            topic = remaining.replace('-', ' ').title() if remaining else "Unknown"
            
            return f"{doc_type} #{num} - {topic} ({year})"
        
        # Fallback to cleaned filename
        return name.replace('-', ' ').replace('#', '').title()
    
    def report_sync_results(self, local_count: int, airtable_count: int, matched_count: int):
        """Report sync results and mismatches."""
        print("\n" + "=" * 50)
        print("📊 SYNC RESULTS")
        print("=" * 50)
        
        print(f"\n✅ Successfully Matched: {matched_count} documents")
        print(f"   Local documents: {local_count}")
        print(f"   Airtable records: {airtable_count}")
        
        # Report mismatches
        if self.mismatches['missing_in_airtable']:
            print(f"\n⚠️  LOCAL DOCUMENTS NOT IN AIRTABLE: {len(self.mismatches['missing_in_airtable'])}")
            print("   These need to be added to Airtable:")
            for doc in self.mismatches['missing_in_airtable'][:5]:
                print(f"   - {doc['file']} ({doc['type']})")
            if len(self.mismatches['missing_in_airtable']) > 5:
                print(f"   ... and {len(self.mismatches['missing_in_airtable']) - 5} more")
        
        if self.mismatches['missing_locally']:
            print(f"\n⚠️  AIRTABLE RECORDS WITHOUT LOCAL FILES: {len(self.mismatches['missing_locally'])}")
            print("   These may need to be removed from Airtable or files need to be added:")
            for doc in self.mismatches['missing_locally'][:5]:
                print(f"   - {doc['display_name']}")
                print(f"     Type: {doc['type']}, Year: {doc['year']}, Number: {doc.get('doc_number', 'N/A')}")
            if len(self.mismatches['missing_locally']) > 5:
                print(f"   ... and {len(self.mismatches['missing_locally']) - 5} more")
        
        # Save mismatch report
        if self.mismatches['missing_in_airtable'] or self.mismatches['missing_locally']:
            report_file = Path('logs/airtable-mismatches.json')
            report_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'summary': {
                        'matched': matched_count,
                        'missing_in_airtable': len(self.mismatches['missing_in_airtable']),
                        'missing_locally': len(self.mismatches['missing_locally'])
                    },
                    'details': self.mismatches
                }, f, indent=2)
            
            print(f"\n📝 Detailed mismatch report saved to: {report_file}")
            print("   Review and correct these mismatches to ensure data consistency")
    
    def reconcile(self):
        """Run reconciliation report comparing cache to current state."""
        print("\n🔍 Reconciliation Report")
        print("=" * 50)
        
        # Force a full sync to get fresh data
        self.full_sync(force=True)
        
        # Load cache to check for provisional entries
        cache = self.load_cache()
        provisional_count = 0
        
        for doc_key, doc_data in cache.get('documents', {}).items():
            if doc_data.get('provisional'):
                if provisional_count == 0:
                    print("\n📝 PROVISIONAL ENTRIES (need Airtable records):")
                provisional_count += 1
                print(f"   - {doc_key}: {doc_data.get('display_name')}")
        
        if provisional_count > 0:
            print(f"\n   Total provisional entries: {provisional_count}")
        else:
            print("\n✅ No provisional entries found")
        
        print("\n" + "=" * 50)
        print("Reconciliation complete")

def main():
    parser = argparse.ArgumentParser(description='Sync Airtable metadata with local documents')
    parser.add_argument('--mode', choices=['full', 'single'], default='full',
                       help='Sync mode: full or single document')
    parser.add_argument('--file', help='Filename for single document update')
    parser.add_argument('--force', action='store_true', 
                       help='Force refresh even if cache is fresh')
    parser.add_argument('--if-stale', action='store_true',
                       help='Only sync if cache is stale')
    parser.add_argument('--create-if-missing', action='store_true',
                       help='Create provisional entry if not found in Airtable')
    parser.add_argument('--reconcile', action='store_true',
                       help='Run reconciliation report')
    parser.add_argument('--cache-file', default='book/airtable-metadata.json',
                       help='Path to cache file')
    
    args = parser.parse_args()
    
    # Initialize syncer
    syncer = AirtableSync(cache_file=args.cache_file)
    
    # Handle reconciliation mode
    if args.reconcile:
        syncer.reconcile()
        return
    
    # Handle sync modes
    if args.mode == 'single':
        if not args.file:
            print("Error: --file required for single mode")
            sys.exit(1)
        syncer.incremental_update(args.file, args.create_if_missing)
    else:
        # Full sync
        if args.if_stale and not syncer.should_refresh_cache():
            print("Cache is fresh, skipping sync")
            return
        syncer.full_sync(force=args.force)

if __name__ == '__main__':
    main()