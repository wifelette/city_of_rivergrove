#!/usr/bin/env python3
"""
CSS Compilation Script
Compiles modular CSS files into a single custom.css that mdBook can handle natively.
This prevents CSS from being deleted during mdBook's build process.
"""

import os
import sys
from pathlib import Path

def compile_css():
    """Compile all modular CSS files into a single custom.css file."""
    
    # Get the repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    # Define paths
    theme_css_dir = repo_root / "theme" / "css"
    output_file = repo_root / "custom.css"
    
    # Check if theme/css directory exists
    if not theme_css_dir.exists():
        print(f"❌ Error: {theme_css_dir} does not exist")
        return False
    
    # Define the CSS files in the correct order (dependencies first)
    # Based on the import order in main.css
    css_files = [
        # Base Layer - Variables and foundational styles
        "base/variables.css",
        "base/typography.css",
        
        # Layout Layer - Page structure and mdBook overrides
        "layout/mdbook-overrides.css",
        "layout/page-structure.css",
        "layout/responsive.css",
        
        # Components Layer - Reusable UI components
        "components/cards.css",
        "components/footnotes.css",
        "components/tables.css",
        "components/navigation.css",
        "components/relationships-panel.css",
        "components/form-controls.css",
        "components/form-fields.css",
        
        # Documents Layer - Document-specific styling
        "documents/document-notes.css",
        "documents/enhanced-elements.css",
        
        # Typography overrides (if it exists)
        "rivergrove-typography.css"
    ]
    
    # Start building the compiled CSS
    compiled_css = []
    
    # Add header
    compiled_css.append("/* COMPILED CSS - DO NOT EDIT DIRECTLY */")
    compiled_css.append("/* This file is auto-generated from theme/css/ modules */")
    compiled_css.append("/* Edit source files in theme/css/ and run compile-css.py */")
    compiled_css.append("")
    
    # Add Google Fonts import at the top (needed for signature styling)
    compiled_css.append("/* Google Fonts for signature styling */")
    compiled_css.append("@import url('https://fonts.googleapis.com/css2?family=Dancing+Script:wght@500&display=swap');")
    compiled_css.append("")
    
    # Process each CSS file
    for css_file in css_files:
        file_path = theme_css_dir / css_file
        
        if not file_path.exists():
            print(f"⚠️  Warning: {css_file} not found, skipping")
            continue
        
        # Read the CSS file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add section header
        compiled_css.append(f"/* ========== {css_file.upper()} ========== */")
        
        # Remove any @import statements as we're inlining everything
        # But preserve Google Fonts imports (they can't be inlined)
        lines = content.split('\n')
        filtered_lines = []
        for line in lines:
            if line.strip().startswith('@import'):
                # Skip file imports but keep external font imports
                if 'fonts.googleapis.com' not in line:
                    continue
                # Skip if we already added this Google Font import
                if 'Dancing+Script' in line:
                    continue
            filtered_lines.append(line)
        
        compiled_css.append('\n'.join(filtered_lines))
        compiled_css.append("")  # Add spacing between sections
    
    # Write the compiled CSS
    output_content = '\n'.join(compiled_css)
    
    # Check if output would be different from existing
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        if existing_content == output_content:
            print("✅ CSS already up to date")
            return True
    
    # Write the new compiled CSS
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)
    
    print(f"✅ Compiled CSS written to {output_file}")
    
    # Also ensure it's copied to book/ if book exists
    book_css = repo_root / "book" / "custom.css"
    if (repo_root / "book").exists():
        with open(book_css, 'w', encoding='utf-8') as f:
            f.write(output_content)
        print(f"✅ Also copied to {book_css}")
    
    return True

if __name__ == "__main__":
    success = compile_css()
    sys.exit(0 if success else 1)