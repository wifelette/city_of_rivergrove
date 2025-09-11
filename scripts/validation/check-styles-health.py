#!/usr/bin/env python3
"""
Check that CSS styles are properly loaded and HTML has correct structure.
This catches the "disappearing styles" issue early.
"""

import sys
import os
from pathlib import Path
from bs4 import BeautifulSoup
import json
import subprocess

# Colors for output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def check_css_import_path():
    """Check that custom.css has the correct import path"""
    custom_css = Path('book/custom.css')
    if not custom_css.exists():
        return False, "book/custom.css not found"
    
    content = custom_css.read_text()
    if '@import url(\'./theme/main.css\')' in content or '@import url("./theme/main.css")' in content:
        return True, "CSS import path is correct"
    elif '@import url(\'./theme/css/main.css\')' in content:
        return False, "CSS import path is WRONG: points to ./theme/css/main.css instead of ./theme/main.css"
    else:
        return False, "CSS import statement not found or malformed"

def check_theme_directory():
    """Check that theme directory exists in book with correct structure"""
    theme_dir = Path('book/theme')
    if not theme_dir.exists():
        return False, "book/theme directory not found"
    
    required_dirs = ['base', 'components', 'documents', 'layout']
    missing = []
    for dir_name in required_dirs:
        if not (theme_dir / dir_name).exists():
            missing.append(dir_name)
    
    if missing:
        return False, f"Missing subdirectories in book/theme: {', '.join(missing)}"
    
    # Check for key CSS files
    key_files = [
        'main.css',
        'components/form-fields.css',
        'documents/document-notes.css',
        'documents/enhanced-elements.css'
    ]
    
    missing_files = []
    for file_path in key_files:
        if not (theme_dir / file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        return False, f"Missing CSS files: {', '.join(missing_files)}"
    
    return True, "Theme directory structure is correct"

def check_html_structure(sample_files=None):
    """Check that HTML files have the expected custom classes"""
    book_dir = Path('book')
    
    # Default sample files to check
    if sample_files is None:
        sample_files = [
            'resolutions/1984-Res-72-Municipal-Services.html',
            'ordinances/1987-Ord-52-Flood.html'
        ]
    
    issues = []
    
    for file_path in sample_files:
        full_path = book_dir / file_path
        if not full_path.exists():
            continue
            
        with open(full_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        # Check for form field classes
        form_fields = soup.find_all(class_='form-field-filled')
        if not form_fields:
            issues.append(f"{file_path}: No form-field-filled classes found")
        
        # Check for Document Notes structure if expected
        doc_notes_h2 = soup.find('h2', string='Document Notes')
        if doc_notes_h2:
            # Should be wrapped in document-note div
            parent = doc_notes_h2.parent
            if not parent or 'document-note' not in parent.get('class', []):
                issues.append(f"{file_path}: Document Notes not wrapped in document-note div")
        
        # Check for definition-item structure (Section markers)
        # Look for "Section 1." type text
        section_markers = soup.find_all(class_='definition-marker')
        section_text = soup.find_all(string=lambda text: text and text.strip().startswith('Section '))
        
        # If we have section text but no markers, postprocessor hasn't run
        if section_text and not section_markers:
            issues.append(f"{file_path}: Found 'Section' text but no definition-marker classes")
    
    if issues:
        return False, "HTML structure issues:\n  " + "\n  ".join(issues)
    
    return True, "HTML structure looks correct"

def check_server_running():
    """Check if mdbook serve is running and warn about using dev-server.sh"""
    try:
        result = subprocess.run(['pgrep', '-f', 'mdbook serve'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            # mdbook is running, check if it's via dev-server
            ps_result = subprocess.run(['ps', '-p', result.stdout.strip(), '-o', 'command='],
                                      capture_output=True, text=True)
            if 'dev-server' not in ps_result.stdout:
                return False, "Plain 'mdbook serve' is running - use ./dev-server.sh instead!"
            return True, "dev-server.sh is running correctly"
        return None, "No mdbook server running"
    except:
        return None, "Could not check server status"

def run_checks(verbose=False):
    """Run all style health checks"""
    print(f"{BLUE}🔍 Checking CSS and HTML health...{NC}\n")
    
    all_passed = True
    checks = [
        ("CSS Import Path", check_css_import_path),
        ("Theme Directory", check_theme_directory),
        ("HTML Structure", check_html_structure),
        ("Server Check", check_server_running)
    ]
    
    for check_name, check_func in checks:
        passed, message = check_func()
        
        if passed is None:
            # Skip/info status
            if verbose:
                print(f"  ℹ️  {check_name}: {message}")
        elif passed:
            print(f"  {GREEN}✓{NC} {check_name}: {message}")
        else:
            print(f"  {RED}✗{NC} {check_name}: {message}")
            all_passed = False
    
    print()
    
    if not all_passed:
        print(f"{YELLOW}⚠️  Style issues detected!{NC}")
        print(f"\nTo fix, run: {GREEN}./scripts/fix-styles.sh{NC}")
        print(f"For development, always use: {GREEN}./dev-server.sh{NC}")
        return 1
    else:
        print(f"{GREEN}✅ All style checks passed!{NC}")
        return 0

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Check CSS and HTML health')
    parser.add_argument('-v', '--verbose', action='store_true', 
                       help='Show all checks including info messages')
    parser.add_argument('--fix', action='store_true',
                       help='Automatically run fix-styles.sh if issues found')
    args = parser.parse_args()
    
    exit_code = run_checks(verbose=args.verbose)
    
    if exit_code != 0 and args.fix:
        print(f"\n{BLUE}Running fix-styles.sh...{NC}")
        subprocess.run(['./scripts/fix-styles.sh'])
        print(f"\n{BLUE}Re-checking...{NC}")
        exit_code = run_checks(verbose=args.verbose)
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()