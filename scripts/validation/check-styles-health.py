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

def check_css_compiled():
    """Check that custom.css exists and is compiled"""
    custom_css = Path('book/custom.css')
    if not custom_css.exists():
        return False, "book/custom.css not found"

    content = custom_css.read_text()
    # Check for the compiled CSS header
    if '/* COMPILED CSS - DO NOT EDIT DIRECTLY */' in content:
        # Check file size to ensure it has content
        size = custom_css.stat().st_size
        if size > 10000:  # Should be at least 10KB
            return True, f"CSS compiled correctly ({size:,} bytes)"
        else:
            return False, f"CSS file too small ({size} bytes) - may not be fully compiled"
    else:
        return False, "CSS not properly compiled - run compile-css.py"

def check_source_css_modules():
    """Check that source CSS modules exist in theme/css/"""
    theme_dir = Path('theme/css')
    if not theme_dir.exists():
        return False, "theme/css directory not found"

    required_dirs = ['base', 'components', 'documents', 'layout']
    missing = []
    for dir_name in required_dirs:
        if not (theme_dir / dir_name).exists():
            missing.append(dir_name)

    if missing:
        return False, f"Missing CSS module directories: {', '.join(missing)}"

    # Check for key CSS files in source
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
        return False, f"Missing CSS source files: {', '.join(missing_files)}"

    return True, "CSS source modules are correct"

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
    """Check if mdbook serve is running (informational only)"""
    try:
        result = subprocess.run(['pgrep', '-f', 'mdbook serve'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            # mdbook is running - just report it
            ps_result = subprocess.run(['ps', '-p', result.stdout.strip(), '-o', 'command='],
                                      capture_output=True, text=True)
            if '--port 3000' in ps_result.stdout:
                return True, "Development server running on port 3000"
            return True, "mdbook server is running"
        return None, "No mdbook server running"
    except:
        return None, "Could not check server status"

def run_checks(verbose=False, show_details=False):
    """Run all style health checks"""
    if not show_details:
        # Quiet mode for dev-server - just return status
        all_passed = True
        checks = [
            ("Compiled CSS", check_css_compiled),
            ("CSS Source Modules", check_source_css_modules),
            ("HTML Structure", check_html_structure),
            ("Server Check", check_server_running)
        ]

        for check_name, check_func in checks:
            passed, message = check_func()
            if passed is False:
                all_passed = False
                if verbose:
                    print(f"  {RED}✗{NC} {check_name}: {message}")

        if not all_passed:
            print(f"{YELLOW}  ⚠️  Style health check failed - run './scripts/fix-styles.sh'{NC}")
            return 1
        return 0

    # Detailed mode when run directly
    print(f"{BLUE}🔍 Checking CSS and HTML health...{NC}\n")

    all_passed = True
    checks = [
        ("Compiled CSS", check_css_compiled),
        ("CSS Source Modules", check_source_css_modules),
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
    
    # When run directly, show details
    exit_code = run_checks(verbose=args.verbose, show_details=True)

    if exit_code != 0 and args.fix:
        print(f"\n{BLUE}Running fix-styles.sh...{NC}")
        subprocess.run(['./scripts/fix-styles.sh'])
        print(f"\n{BLUE}Re-checking...{NC}")
        exit_code = run_checks(verbose=args.verbose, show_details=True)
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()