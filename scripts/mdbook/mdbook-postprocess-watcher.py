#!/usr/bin/python3
"""
Smart watcher for mdBook rebuilds that automatically runs post-processors.

This solves the issue where mdBook's internal rebuild bypasses our custom processors,
causing form fields to lose styling and cross-references to disappear.

Instead of a fixed wait time, this watches for actual file changes in the book/ 
directory and runs post-processors when mdBook finishes rebuilding.
"""

import os
import sys
import time
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
import json

class MdBookWatcher:
    def __init__(self, book_dir="book", verbose=False):
        self.book_dir = Path(book_dir)
        self.verbose = verbose
        self.html_files = {}
        self.last_rebuild = None
        self.rebuild_in_progress = False
        self.rebuild_complete_threshold = 0.5  # seconds of no changes to consider rebuild done
        
        # Post-processors to run after rebuild
        self.postprocessors = [
            "scripts/postprocessing/custom-list-processor.py",
            "scripts/postprocessing/enhanced-custom-processor.py"
        ]
        
    def log(self, message):
        """Log with timestamp if verbose."""
        if self.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    def get_html_files(self):
        """Get all HTML files in book directory."""
        html_files = {}
        for html_file in self.book_dir.glob("**/*.html"):
            # Skip print.html and 404.html as they're special
            if html_file.name in ["print.html", "404.html"]:
                continue
            html_files[str(html_file)] = self.get_file_hash(html_file)
        return html_files
    
    def get_file_hash(self, filepath):
        """Get a quick hash of file content (first 1KB for speed)."""
        try:
            with open(filepath, 'rb') as f:
                # Only read first 1KB for speed
                content = f.read(1024)
                return hashlib.md5(content).hexdigest()
        except:
            return None
    
    def detect_changes(self):
        """Check if any HTML files have changed."""
        current_files = self.get_html_files()
        
        if not self.html_files:
            # First run - initialize
            self.html_files = current_files
            return False
        
        # Check for changes
        changed = False
        for filepath, file_hash in current_files.items():
            if filepath not in self.html_files or self.html_files[filepath] != file_hash:
                changed = True
                self.log(f"Changed: {Path(filepath).name}")
        
        # Check for deleted files
        for filepath in self.html_files:
            if filepath not in current_files:
                changed = True
                self.log(f"Deleted: {Path(filepath).name}")
        
        self.html_files = current_files
        return changed
    
    def run_postprocessors(self):
        """Run all post-processing scripts."""
        print("🎨 Running post-processors to restore custom formatting...", flush=True)
        
        for script in self.postprocessors:
            if Path(script).exists():
                try:
                    self.log(f"Running {script}")
                    result = subprocess.run(
                        ["python3", script],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    if result.returncode != 0 and self.verbose:
                        print(f"  ⚠️  {script} had issues: {result.stderr}", flush=True)
                except subprocess.TimeoutExpired:
                    print(f"  ⚠️  {script} timed out", flush=True)
                except Exception as e:
                    print(f"  ❌ Error running {script}: {e}", flush=True)
        
        print("✅ Post-processing complete - custom formatting restored", flush=True)
    
    def watch(self, check_interval=0.1):
        """
        Watch for mdBook rebuilds and run post-processors when complete.
        
        Strategy:
        1. Check for HTML file changes frequently
        2. When changes detected, mark rebuild as in progress
        3. When no changes for threshold time, consider rebuild complete
        4. Run post-processors once after rebuild completes
        """
        print("👁️  Watching for mdBook rebuilds...", flush=True)
        print(f"   • Monitoring: {self.book_dir}", flush=True)
        print(f"   • Post-processors will run automatically after rebuilds", flush=True)
        if not self.verbose:
            print("   • Run with --verbose for detailed logging", flush=True)
        print(flush=True)
        
        last_change_time = None
        
        try:
            while True:
                if self.detect_changes():
                    # Changes detected
                    last_change_time = time.time()
                    
                    if not self.rebuild_in_progress:
                        self.rebuild_in_progress = True
                        self.log("mdBook rebuild detected...")
                
                elif self.rebuild_in_progress and last_change_time:
                    # Check if rebuild is complete (no changes for threshold time)
                    time_since_change = time.time() - last_change_time
                    
                    if time_since_change >= self.rebuild_complete_threshold:
                        # Rebuild appears complete
                        self.rebuild_in_progress = False
                        self.last_rebuild = time.time()
                        
                        print(f"\n🔄 mdBook rebuild detected at {datetime.now().strftime('%H:%M:%S')}", flush=True)
                        self.run_postprocessors()
                        print(flush=True)
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Watcher stopped")
            sys.exit(0)

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Watch for mdBook rebuilds and run post-processors')
    parser.add_argument('--book-dir', default='book', help='Path to book directory (default: book)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--interval', type=float, default=0.1, 
                       help='Check interval in seconds (default: 0.1)')
    parser.add_argument('--threshold', type=float, default=0.5,
                       help='Seconds of no changes to consider rebuild complete (default: 0.5)')
    
    args = parser.parse_args()
    
    # Check if book directory exists
    if not Path(args.book_dir).exists():
        print(f"❌ Book directory not found: {args.book_dir}")
        print("   Make sure mdbook has been built at least once")
        sys.exit(1)
    
    # Check if we're in the right directory
    if not Path("book.toml").exists():
        print("⚠️  Warning: book.toml not found in current directory")
        print("   This script should be run from the repository root")
    
    watcher = MdBookWatcher(args.book_dir, args.verbose)
    watcher.rebuild_complete_threshold = args.threshold
    watcher.watch(args.interval)

if __name__ == "__main__":
    main()