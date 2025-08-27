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
    
    # Remove existing files in destination
    for file in dest_dir.glob("*.md"):
        file.unlink()
    
    # Copy all .md files from source to destination
    copied_files = []
    for file in source_dir.glob("*.md"):
        # Map filename: remove # from ordinance files
        dest_name = file.name.replace("#", "")
        dest_file = dest_dir / dest_name
        shutil.copy2(file, dest_file)
        copied_files.append(f"{file.name} -> {dest_name}")
    
    print(f"Synced {len(copied_files)} ordinance files:")
    for filename in sorted(copied_files):
        print(f"  - {filename}")
    
    return True

if __name__ == "__main__":
    if sync_ordinances():
        print("✓ Ordinances synced successfully")
    else:
        print("✗ Failed to sync ordinances")
        sys.exit(1)