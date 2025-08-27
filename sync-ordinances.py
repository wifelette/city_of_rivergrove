#!/usr/bin/env python3
"""
Sync ordinances from the main Ordinances directory to src/ordinances for mdBook
"""

import os
import shutil
import sys
from pathlib import Path

def sync_ordinances():
    """Copy all files from Ordinances/ to src/ordinances/"""
    source_dir = Path("Ordinances")
    dest_dir = Path("src/ordinances")
    
    if not source_dir.exists():
        print(f"Source directory {source_dir} does not exist")
        return False
    
    # Create destination directory if it doesn't exist
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Track changes
    updated_files = []
    removed_files = []
    
    # Get existing destination files
    existing_dest_files = {f.name: f for f in dest_dir.glob("*.md")}
    
    # Copy all .md files from source to destination
    processed_dest_names = set()
    for file in source_dir.glob("*.md"):
        # Map filename: remove # from ordinance files
        dest_name = file.name.replace("#", "")
        dest_file = dest_dir / dest_name
        processed_dest_names.add(dest_name)
        
        # Check if file needs updating
        needs_update = False
        if not dest_file.exists():
            needs_update = True
        else:
            # Compare file contents
            with open(file, 'r') as f1, open(dest_file, 'r') as f2:
                if f1.read() != f2.read():
                    needs_update = True
        
        if needs_update:
            shutil.copy2(file, dest_file)
            updated_files.append(f"{file.name} -> {dest_name}")
    
    # Remove files that no longer exist in source
    for dest_name in existing_dest_files:
        if dest_name not in processed_dest_names:
            existing_dest_files[dest_name].unlink()
            removed_files.append(dest_name)
    
    # Print results
    if updated_files or removed_files:
        if updated_files:
            print(f"  Updated {len(updated_files)} ordinance file(s):")
            for filename in sorted(updated_files):
                print(f"    ✓ {filename}")
        if removed_files:
            print(f"  Removed {len(removed_files)} ordinance file(s):")
            for filename in sorted(removed_files):
                print(f"    ✗ {filename}")
    else:
        print(f"  No changes needed ({len(list(source_dir.glob('*.md')))} files already in sync)")
    
    return True

if __name__ == "__main__":
    if sync_ordinances():
        print("✓ Ordinances synced successfully")
    else:
        print("✗ Failed to sync ordinances")
        sys.exit(1)