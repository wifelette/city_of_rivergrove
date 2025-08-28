#!/usr/bin/env python3
"""
Auto-link converter that automatically converts URLs and email addresses
to clickable markdown links in all documents.
"""

import re
import sys
from pathlib import Path

def convert_urls_to_links(content):
    """
    Convert plain URLs to markdown links.
    Matches http://, https://, and www. URLs.
    """
    # Pattern to match URLs that aren't already in markdown link format
    # Negative lookbehind to avoid converting URLs that are already links
    url_pattern = r'(?<!\[)(?<!\()(?:https?://|www\.)[^\s\),]+(?:\.[^\s\),]+)*'
    
    def replace_url(match):
        url = match.group(0)
        # Add https:// to www. URLs
        if url.startswith('www.'):
            full_url = 'https://' + url
        else:
            full_url = url
        # Return as markdown link
        return f'[{url}]({full_url})'
    
    # First, protect already formatted markdown links
    # Store them temporarily and restore after processing
    link_pattern = r'\[([^\]]+)\]\([^\)]+\)'
    protected_links = []
    
    def protect_link(match):
        protected_links.append(match.group(0))
        return f'<<<PROTECTED_LINK_{len(protected_links)-1}>>>'
    
    # Protect existing links
    content = re.sub(link_pattern, protect_link, content)
    
    # Convert URLs to links
    content = re.sub(url_pattern, replace_url, content)
    
    # Restore protected links
    for i, link in enumerate(protected_links):
        content = content.replace(f'<<<PROTECTED_LINK_{i}>>>', link)
    
    return content

def convert_emails_to_links(content):
    """
    Convert plain email addresses to mailto: links.
    """
    # Pattern to match email addresses that aren't already in markdown link format
    # This is a simplified pattern that catches most common email formats
    email_pattern = r'(?<!\[)(?<![:\>/])([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
    
    def replace_email(match):
        email = match.group(1)
        # Return as markdown mailto link
        return f'[{email}](mailto:{email})'
    
    # First, protect already formatted markdown links (including mailto: links)
    link_pattern = r'\[([^\]]+)\]\([^\)]+\)'
    protected_links = []
    
    def protect_link(match):
        protected_links.append(match.group(0))
        return f'<<<PROTECTED_LINK_{len(protected_links)-1}>>>'
    
    # Protect existing links
    content = re.sub(link_pattern, protect_link, content)
    
    # Convert emails to mailto links
    content = re.sub(email_pattern, replace_email, content)
    
    # Restore protected links
    for i, link in enumerate(protected_links):
        content = content.replace(f'<<<PROTECTED_LINK_{i}>>>', link)
    
    return content

def process_file(file_path):
    """Process a single file to convert URLs and emails to links."""
    path = Path(file_path)
    
    if not path.exists():
        print(f"Error: File not found: {file_path}")
        return False
    
    try:
        content = path.read_text(encoding='utf-8')
        original_content = content
        
        # Convert URLs to links
        content = convert_urls_to_links(content)
        
        # Convert emails to links
        content = convert_emails_to_links(content)
        
        # Only write if changes were made
        if content != original_content:
            path.write_text(content, encoding='utf-8')
            print(f"✓ Converted links in: {path.name}")
            
            # Show what was converted for verification
            urls_found = re.findall(r'(?:https?://|www\.)[^\s\),]+', original_content)
            emails_found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', original_content)
            
            if urls_found:
                print(f"  URLs converted: {', '.join(set(urls_found))}")
            if emails_found:
                print(f"  Emails converted: {', '.join(set(emails_found))}")
            
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error processing {path.name}: {e}")
        return False

def main():
    """Main entry point for the auto-link converter."""
    if len(sys.argv) < 2:
        print("Usage: python3 auto-link-converter.py <file_path> [file_path2 ...]")
        print("Example: python3 auto-link-converter.py src/resolutions/*.md")
        sys.exit(1)
    
    success_count = 0
    total_files = len(sys.argv) - 1
    
    for file_path in sys.argv[1:]:
        # Handle glob patterns
        path = Path(file_path)
        if '*' in str(path):
            # Glob pattern - expand it
            parent = path.parent
            pattern = path.name
            for file in parent.glob(pattern):
                if file.suffix == '.md':
                    if process_file(file):
                        success_count += 1
        else:
            # Single file
            if process_file(file_path):
                success_count += 1
    
    if success_count > 0:
        print(f"\n✅ Converted links in {success_count} file(s)")

if __name__ == "__main__":
    main()