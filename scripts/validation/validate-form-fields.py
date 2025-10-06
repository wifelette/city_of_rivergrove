#!/usr/bin/python3
"""
Validate form field syntax in markdown documents.
Detects unclosed {{filled:}} tags and other form field issues.
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict

# ANSI color codes for terminal output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

class FormFieldValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
    def validate_file(self, filepath: Path) -> bool:
        """Validate a single markdown file for form field issues."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            self.errors.append((filepath, 0, f"Could not read file: {e}"))
            return False
        
        has_errors = False
        
        # Check for unclosed {{filled: tags
        for line_num, line in enumerate(lines, 1):
            # Find all {{filled: occurrences
            if '{{filled:' in line:
                # Check if each opening has a corresponding closing
                open_count = line.count('{{filled:')
                close_count = line.count('}}')
                
                # More sophisticated check for unclosed tags
                remaining = line
                while '{{filled:' in remaining:
                    start = remaining.find('{{filled:')
                    # Look for the closing }} after this opening
                    after_start = remaining[start:]
                    
                    # Find the next }} if it exists
                    close = after_start.find('}}')
                    
                    if close == -1:
                        # No closing tag found
                        self.errors.append((
                            filepath, 
                            line_num, 
                            f"Unclosed {{{{filled:}}}} tag: {line.strip()}"
                        ))
                        has_errors = True
                        break
                    else:
                        # Move past this complete tag
                        remaining = remaining[start + close + 2:]
            
            # Check for orphaned closing brackets
            if '}}' in line and '{{' not in line:
                # Check if this might be a closing for a multi-line tag
                # (for now, we'll warn about these)
                self.warnings.append((
                    filepath,
                    line_num,
                    f"Orphaned closing brackets '}}': {line.strip()}"
                ))
            
            # Check for malformed tags (missing colon)
            if '{{filled' in line and '{{filled:' not in line:
                self.errors.append((
                    filepath,
                    line_num,
                    f"Malformed tag (missing colon after 'filled'): {line.strip()}"
                ))
                has_errors = True
            
            # Check for nested tags (not supported)
            if '{{filled:' in line:
                # Simple check for nested tags
                parts = line.split('{{filled:')
                for i, part in enumerate(parts[1:], 1):
                    if '{{filled:' in part.split('}}')[0] if '}}' in part else part:
                        self.warnings.append((
                            filepath,
                            line_num,
                            f"Possible nested {{{{filled:}}}} tags detected"
                        ))
        
        # Check for old underscore patterns that should be migrated
        for line_num, line in enumerate(lines, 1):
            if '___' in line and '{{filled:' not in line:
                self.warnings.append((
                    filepath,
                    line_num,
                    f"Legacy underscore pattern found - consider using {{{{filled:}}}}: {line.strip()[:80]}..."
                ))
        
        return not has_errors
    
    def validate_directory(self, directory: Path) -> bool:
        """Validate all markdown files in a directory."""
        all_valid = True
        files_checked = 0
        
        for md_file in directory.rglob('*.md'):
            # Skip certain directories
            if any(skip in str(md_file) for skip in ['.git', 'node_modules', 'book']):
                continue
                
            files_checked += 1
            if not self.validate_file(md_file):
                all_valid = False
        
        return all_valid, files_checked
    
    def print_report(self):
        """Print validation report with colored output."""
        if self.errors:
            print(f"\n{RED}❌ ERRORS FOUND:{NC}")
            for filepath, line_num, message in self.errors:
                relative_path = filepath.relative_to(Path.cwd()) if filepath.is_absolute() else filepath
                print(f"  {RED}• {relative_path}:{line_num}{NC}")
                print(f"    {message}")
        
        if self.warnings:
            print(f"\n{YELLOW}⚠️  WARNINGS:{NC}")
            for filepath, line_num, message in self.warnings:
                relative_path = filepath.relative_to(Path.cwd()) if filepath.is_absolute() else filepath
                print(f"  {YELLOW}• {relative_path}:{line_num}{NC}")
                print(f"    {message}")
        
        if not self.errors and not self.warnings:
            print(f"{GREEN}✅ All form field tags are valid!{NC}")
    
    def get_error_count(self) -> int:
        """Return the number of errors found."""
        return len(self.errors)
    
    def get_warning_count(self) -> int:
        """Return the number of warnings found."""
        return len(self.warnings)


def main():
    """Main entry point for the validator."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate form field syntax in markdown documents')
    parser.add_argument('path', nargs='?', default='source-documents',
                       help='File or directory to validate (default: source-documents)')
    parser.add_argument('--fix', action='store_true',
                       help='Attempt to auto-fix simple issues (adds closing brackets)')
    parser.add_argument('--quiet', action='store_true',
                       help='Only show errors, not warnings')
    
    args = parser.parse_args()
    
    path = Path(args.path)
    validator = FormFieldValidator()
    
    if path.is_file():
        print(f"Validating {path}...")
        is_valid = validator.validate_file(path)
        files_checked = 1
    elif path.is_dir():
        print(f"Validating markdown files in {path}...")
        is_valid, files_checked = validator.validate_directory(path)
    else:
        print(f"{RED}Error: {path} not found{NC}")
        sys.exit(1)
    
    # Auto-fix if requested
    if args.fix and validator.errors:
        print(f"\n{BLUE}🔧 Attempting auto-fix...{NC}")
        fixed_count = 0
        
        for filepath, line_num, message in validator.errors:
            if "Unclosed {{filled:" in message:
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Fix the line by adding closing brackets
                    if line_num <= len(lines):
                        line = lines[line_num - 1]
                        if '{{filled:' in line and '}}' not in line:
                            lines[line_num - 1] = line.rstrip() + '}}\n'
                            fixed_count += 1
                            
                            # Write back
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.writelines(lines)
                            
                            print(f"  {GREEN}✓ Fixed line {line_num} in {filepath.name}{NC}")
                except Exception as e:
                    print(f"  {RED}✗ Could not fix {filepath}: {e}{NC}")
        
        if fixed_count > 0:
            print(f"\n{GREEN}Fixed {fixed_count} issue(s). Please review the changes.{NC}")
    
    # Print report
    if not args.quiet or validator.errors:
        validator.print_report()
    
    # Summary
    print(f"\n📊 Checked {files_checked} file(s)")
    error_count = validator.get_error_count()
    warning_count = validator.get_warning_count()
    
    if error_count > 0:
        print(f"{RED}   {error_count} error(s) found{NC}")
    if warning_count > 0 and not args.quiet:
        print(f"{YELLOW}   {warning_count} warning(s) found{NC}")
    
    # Exit with error code if errors found
    sys.exit(1 if error_count > 0 else 0)


if __name__ == '__main__':
    main()