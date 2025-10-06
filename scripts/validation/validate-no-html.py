#!/usr/bin/python3
"""
Validate that markdown source files don't contain HTML tags.

We process everything through markdown and our custom processors.
HTML in source files would bypass our processing pipeline and could
break consistency, so we prevent it.

Exceptions:
- HTML comments (<!-- -->) are allowed for notes
- <br> tags might be needed in some cases (but should be rare)
"""

import sys
import re
from pathlib import Path
from typing import List, Tuple

# HTML tags that should NEVER appear in our markdown files
FORBIDDEN_TAGS = [
    'div', 'span', 'table', 'tr', 'td', 'th', 'ul', 'ol', 'li',
    'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'img',
    'strong', 'em', 'b', 'i', 'code', 'pre', 'blockquote',
    'section', 'article', 'nav', 'header', 'footer', 'aside',
    'style', 'script', 'link', 'meta'
]

# Tags that might be acceptable in rare cases
ALLOWED_TAGS = ['br']  # Line breaks might be necessary

def find_html_tags(content: str, filename: str) -> List[Tuple[int, str, str]]:
    """Find HTML tags in content.
    
    Returns list of (line_number, tag, line_content) tuples.
    """
    issues = []
    lines = content.split('\n')
    
    # Pattern to find HTML tags (but not comments)
    tag_pattern = re.compile(r'<(?!--)[^>]+>')
    
    for i, line in enumerate(lines, 1):
        # Skip HTML comments
        if '<!--' in line and '-->' in line:
            continue
            
        # Find all HTML-like tags in the line
        matches = tag_pattern.findall(line)
        for match in matches:
            # Extract tag name
            tag_match = re.match(r'</?(\w+)', match)
            if tag_match:
                tag_name = tag_match.group(1).lower()
                
                # Check if it's a forbidden tag
                if tag_name in FORBIDDEN_TAGS:
                    issues.append((i, tag_name, line.strip()))
                elif tag_name not in ALLOWED_TAGS:
                    # Unknown tag - probably shouldn't be there
                    issues.append((i, tag_name, line.strip()))
    
    return issues

def validate_file(filepath: Path) -> bool:
    """Validate a single markdown file.
    
    Returns True if valid, False if HTML found.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return False
    
    issues = find_html_tags(content, str(filepath))
    
    if issues:
        print(f"\n❌ {filepath}")
        for line_num, tag, line_content in issues:
            print(f"   Line {line_num}: <{tag}> tag found")
            print(f"   {line_content[:80]}...")
        return False
    
    return True

def validate_directory(directory: Path) -> Tuple[int, int]:
    """Validate all markdown files in a directory.
    
    Returns (valid_count, invalid_count).
    """
    valid = 0
    invalid = 0
    
    for filepath in directory.rglob('*.md'):
        # Skip generated directories
        if '/src/' in str(filepath) or '/book/' in str(filepath):
            continue
            
        if validate_file(filepath):
            valid += 1
        else:
            invalid += 1
    
    return valid, invalid

def main():
    """Main validation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Validate markdown files contain no HTML')
    parser.add_argument('path', nargs='?', default='source-documents',
                      help='File or directory to validate')
    parser.add_argument('--quiet', action='store_true',
                      help='Only show errors')
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if not path.exists():
        print(f"Error: {path} does not exist")
        sys.exit(1)
    
    print("🔍 Validating markdown files for HTML content...")
    print("=" * 50)
    
    if path.is_file():
        if path.suffix == '.md':
            if validate_file(path):
                if not args.quiet:
                    print(f"✅ {path} - No HTML found")
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            print(f"Error: {path} is not a markdown file")
            sys.exit(1)
    else:
        valid, invalid = validate_directory(path)
        
        print("\n" + "=" * 50)
        print(f"📊 Results:")
        print(f"   ✅ Valid files: {valid}")
        print(f"   ❌ Files with HTML: {invalid}")
        
        if invalid > 0:
            print("\n⚠️  HTML tags found in source files!")
            print("   This could bypass our processing pipeline.")
            print("   Consider using markdown syntax instead:")
            print("   • Use **text** for bold, not <strong>")
            print("   • Use *text* for italic, not <em>")
            print("   • Use [text](url) for links, not <a>")
            print("   • Use markdown lists, not <ul>/<ol>")
            sys.exit(1)
        else:
            if not args.quiet:
                print("\n✅ All files are clean - no HTML found!")
            sys.exit(0)

if __name__ == '__main__':
    main()