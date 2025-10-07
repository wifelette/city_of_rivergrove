#!/usr/bin/env python3
"""
Sync meeting documents from source-documents/Meetings/ to src/ directories.
Handles transcripts, agendas, and minutes, organizing them by type.
"""

import os
import shutil
from pathlib import Path
import re

def sync_meetings():
    """
    Sync all meeting documents from source to appropriate src directories.
    
    Source structure: source-documents/Meetings/YYYY/YYYY-MM/YYYY-MM-DD-Type.md
    Target structure: 
        - src/transcripts/YYYY-MM-DD-Transcript.md
        - src/agendas/YYYY-MM-DD-Agenda.md  
        - src/minutes/YYYY-MM-DD-Minutes.md
    """
    
    source_base = Path("source-documents/Meetings")
    
    # Define target directories
    targets = {
        'Transcript': Path("src/transcripts"),
        'Agenda': Path("src/agendas"),
        'Minutes': Path("src/minutes")
    }
    
    # Create target directories if they don't exist
    for target_dir in targets.values():
        target_dir.mkdir(parents=True, exist_ok=True)
    
    # Track what we process
    processed = {
        'Transcript': 0,
        'Agenda': 0,
        'Minutes': 0
    }
    
    # Clear existing files in target directories
    for doc_type, target_dir in targets.items():
        for old_file in target_dir.glob("*.md"):
            old_file.unlink()
            print(f"  Removed old file: {old_file.name}")
    
    # Walk through the source directory structure
    if not source_base.exists():
        print(f"  ⚠️  Source directory does not exist: {source_base}")
        return
    
    # Find all .md files in the Meetings directory structure
    for md_file in source_base.rglob("*.md"):
        # Parse the filename to determine document type
        filename = md_file.name
        
        # Match pattern: YYYY-MM-DD-Type.md
        match = re.match(r'^(\d{4}-\d{2}-\d{2})-(Transcript|Agenda|Minutes)\.md$', filename)
        if match:
            date_part = match.group(1)
            doc_type = match.group(2)
            
            # Copy to appropriate target directory
            if doc_type in targets:
                target_path = targets[doc_type] / filename
                shutil.copy2(md_file, target_path)
                processed[doc_type] += 1
                print(f"  ✓ Copied {doc_type}: {filename}")
        else:
            print(f"  ⚠️  Skipped (unrecognized format): {filename}")
    
    # Print summary
    print(f"\n  Summary:")
    print(f"    • Transcripts synced: {processed['Transcript']}")
    print(f"    • Agendas synced: {processed['Agenda']}")
    print(f"    • Minutes synced: {processed['Minutes']}")
    
    return processed

def main():
    """Main entry point for the script."""
    print("📄 Syncing meeting documents...")
    sync_meetings()
    print("  ✅ Meeting documents sync complete")

if __name__ == "__main__":
    main()