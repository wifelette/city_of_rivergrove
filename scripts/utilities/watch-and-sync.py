#!/usr/bin/python3
"""
Watch for changes in Ordinances/ directory and automatically sync to src/ordinances/
"""

import os
import shutil
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class OrdinanceHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_sync = {}
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        file_path = Path(event.src_path)
        if file_path.suffix != '.md':
            return
            
        # Debounce - don't sync the same file too frequently
        now = time.time()
        if file_path in self.last_sync and now - self.last_sync[file_path] < 1:
            return
        self.last_sync[file_path] = now
        
        print(f"📝 {file_path.name} changed, syncing...")
        self.sync_file(file_path)
        
    def sync_file(self, source_file):
        """Sync a single file to src/ordinances/"""
        source_path = Path(source_file)
        dest_dir = Path("src/ordinances")
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        # Map the filename (remove # from ordinance files)
        dest_name = source_path.name.replace("#", "")
        dest_path = dest_dir / dest_name
        
        try:
            shutil.copy2(source_path, dest_path)
            print(f"✅ Synced {source_path.name} -> {dest_name}")
            
            # Trigger mdBook rebuild (if mdbook serve is running, it should auto-rebuild)
            # But we can also trigger it manually to be sure
            subprocess.run(["mdbook", "build"], capture_output=True)
            
        except Exception as e:
            print(f"❌ Error syncing {source_path.name}: {e}")

def main():
    ordinances_dir = Path("Ordinances")
    if not ordinances_dir.exists():
        print(f"❌ Directory {ordinances_dir} does not exist")
        return
    
    print(f"👀 Watching {ordinances_dir} for changes...")
    print("💡 Edit files in Ordinances/ and they'll automatically sync to src/ordinances/")
    print("🔄 mdBook will rebuild automatically")
    print("Press Ctrl+C to stop")
    
    event_handler = OrdinanceHandler()
    observer = Observer()
    observer.schedule(event_handler, str(ordinances_dir), recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n👋 File watcher stopped")
    
    observer.join()

if __name__ == "__main__":
    main()