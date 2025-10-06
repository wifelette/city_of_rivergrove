#!/usr/bin/python3
"""
Fix Airtable URLs after repository reorganization.
Updates mdURL and fileURL fields to reflect the new source-documents/ structure.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pyairtable import Api

# Load environment variables
load_dotenv()

# Initialize Airtable API
api = Api(os.environ['AIRTABLE_API_KEY'])
base = api.base(os.environ['AIRTABLE_BASE_ID'])
table = base.table(os.environ.get('AIRTABLE_TABLE_NAME', 'Governing_Metadata'))

def fix_url(url):
    """Fix a single URL by adding source-documents/ to the path."""
    if not url:
        return url
    
    # These are the patterns that need fixing
    old_patterns = [
        '/blob/main/Interpretations/',
        '/blob/main/Ordinances/',
        '/blob/main/Resolutions/',
        '/blob/main/Other/'
    ]
    
    new_patterns = [
        '/blob/main/source-documents/Interpretations/',
        '/blob/main/source-documents/Ordinances/',
        '/blob/main/source-documents/Resolutions/',
        '/blob/main/source-documents/Other/'
    ]
    
    # Check if URL already has source-documents (already fixed)
    if '/source-documents/' in url:
        return url
    
    # Apply the fix
    fixed_url = url
    for old, new in zip(old_patterns, new_patterns):
        if old in url:
            fixed_url = url.replace(old, new)
            break
    
    return fixed_url

def main(dry_run=False):
    """Main function to update all Airtable records."""
    if dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
    print("🔧 Fixing Airtable URLs after repository reorganization")
    print("=" * 60)
    
    # Fetch all records
    print("\n📊 Fetching records from Airtable...")
    try:
        records = table.all()
        print(f"✅ Found {len(records)} records")
    except Exception as e:
        print(f"❌ Error fetching records: {e}")
        sys.exit(1)
    
    # Track statistics
    updated_count = 0
    already_correct = 0
    errors = []
    
    print("\n🔄 Processing records...")
    for record in records:
        record_id = record['id']
        fields = record.get('fields', {})
        display_name = fields.get('display_name', 'Unknown')
        
        # Get current URLs
        md_url = fields.get('mdURL', '')
        file_url = fields.get('fileURL', '')
        
        # Fix URLs
        new_md_url = fix_url(md_url)
        new_file_url = fix_url(file_url)
        
        # Check if update is needed
        if new_md_url == md_url and new_file_url == file_url:
            already_correct += 1
            print(f"  ✓ {display_name} - URLs already correct")
            continue
        
        # Prepare update
        updates = {}
        if new_md_url != md_url:
            updates['mdURL'] = new_md_url
            print(f"  📝 {display_name}")
            print(f"     Old MD: {md_url}")
            print(f"     New MD: {new_md_url}")
        
        if new_file_url != file_url:
            updates['fileURL'] = new_file_url
            if new_md_url == md_url:  # Only print if we didn't already
                print(f"  📝 {display_name}")
            print(f"     Old PDF: {file_url}")
            print(f"     New PDF: {new_file_url}")
        
        # Update record in Airtable (skip if dry run)
        if dry_run:
            updated_count += 1
            print(f"     🔍 Would update (dry run)")
        else:
            try:
                table.update(record_id, updates)
                updated_count += 1
                print(f"     ✅ Updated successfully")
            except Exception as e:
                errors.append((display_name, str(e)))
                print(f"     ❌ Error updating: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"✅ Updated: {updated_count} records")
    print(f"✓  Already correct: {already_correct} records")
    
    if errors:
        print(f"❌ Errors: {len(errors)} records")
        for name, error in errors:
            print(f"   - {name}: {error}")
    
    print("\n✨ URL fix complete!")
    
    # Verify by checking one example
    if updated_count > 0:
        print("\n🔍 Verification - fetching first updated record...")
        try:
            # Get fresh data for verification
            sample = table.all(max_records=1, formula="{mdURL} != ''")
            if sample:
                fields = sample[0].get('fields', {})
                print(f"  Sample record: {fields.get('display_name')}")
                print(f"  Current mdURL: {fields.get('mdURL', 'Not set')}")
                if '/source-documents/' in fields.get('mdURL', ''):
                    print("  ✅ URLs successfully updated with source-documents/ path")
                else:
                    print("  ⚠️  URL doesn't contain source-documents/ - may need manual review")
        except Exception as e:
            print(f"  Could not verify: {e}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix Airtable URLs after repository reorganization")
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')
    args = parser.parse_args()
    
    if args.dry_run:
        main(dry_run=True)
    else:
        # Add confirmation prompt for actual updates
        print("This script will update all Airtable URLs to include 'source-documents/' in the path.")
        print("This is necessary after the repository reorganization.")
        print("\nTip: Use --dry-run flag to preview changes without updating")
        response = input("\nProceed with updates? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            main(dry_run=False)
        else:
            print("Cancelled.")