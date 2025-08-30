#!/usr/bin/env python3
"""
Update document counts in introduction.md based on actual files in src/ directories.
"""

import re
from pathlib import Path

def count_documents():
    """Count documents in each category."""
    src_dir = Path("src")
    
    counts = {
        'ordinances': 0,
        'resolutions': 0, 
        'interpretations': 0,
        'transcripts': 0,
        'other': 0
    }
    
    for category in counts.keys():
        dir_path = src_dir / category
        if dir_path.exists():
            # Count .md files, excluding SUMMARY.md
            md_files = [f for f in dir_path.glob("*.md") if f.name != "SUMMARY.md"]
            counts[category] = len(md_files)
    
    return counts

def update_introduction_counts(counts):
    """Update the document counts in introduction.md."""
    intro_file = Path("src/introduction.md")
    
    if not intro_file.exists():
        print("❌ introduction.md not found")
        return False
    
    content = intro_file.read_text(encoding='utf-8')
    
    # Update patterns for each document type
    updates = [
        (r'<p class="doc-count">\d+ documents</p>', 
         f'<p class="doc-count">{counts["ordinances"]} documents</p>', 
         'Ordinances'),
        
        (r'<p class="doc-count">\d+ documents</p>', 
         f'<p class="doc-count">{counts["resolutions"]} documents</p>', 
         'Resolutions'),
         
        (r'<p class="doc-count">\d+ documents</p>', 
         f'<p class="doc-count">{counts["interpretations"]} documents</p>', 
         'Interpretations'),
         
        (r'<p class="doc-count">\d+ transcripts</p>', 
         f'<p class="doc-count">{counts["transcripts"]} transcripts</p>', 
         'Transcripts'),
         
        (r'<p class="doc-count">\d+ document</p>', 
         f'<p class="doc-count">{counts["other"]} document</p>', 
         'Other')
    ]
    
    # Apply updates in order (they appear in the file in this sequence)
    updated_content = content
    
    # More precise approach: find and replace specific sections
    sections = [
        ('ordinances', counts['ordinances'], 'documents'),
        ('resolutions', counts['resolutions'], 'documents'), 
        ('interpretations', counts['interpretations'], 'documents'),
        ('transcripts', counts['transcripts'], 'transcripts'),
        ('other', counts['other'], 'document' if counts['other'] == 1 else 'documents')
    ]
    
    # Find each card section and update its count
    for section_type, count, unit in sections:
        # Look for the card section and update its count
        if section_type == 'ordinances':
            pattern = r'(<h3><a href="ordinances/[^"]*">Ordinances</a></h3>.*?<p class="doc-count">)\d+( documents</p>)'
        elif section_type == 'resolutions': 
            pattern = r'(<h3><a href="resolutions/[^"]*">Resolutions</a></h3>.*?<p class="doc-count">)\d+( documents</p>)'
        elif section_type == 'interpretations':
            pattern = r'(<h3><a href="interpretations/[^"]*">Planning Interpretations</a></h3>.*?<p class="doc-count">)\d+( documents</p>)'
        elif section_type == 'transcripts':
            pattern = r'(<h3><a href="transcripts/[^"]*">Meeting Records</a></h3>.*?<p class="doc-count">)\d+( transcripts</p>)'
        elif section_type == 'other':
            pattern = r'(<h3><a href="other/[^"]*">Other Documents</a></h3>.*?<p class="doc-count">)\d+( documents?</p>)'
        
        replacement = f'\\g<1>{count}\\g<2>'
        updated_content = re.sub(pattern, replacement, updated_content, flags=re.DOTALL)
    
    # Write updated content back
    if updated_content != content:
        intro_file.write_text(updated_content, encoding='utf-8')
        return True
    
    return False

def main():
    """Main function to update document counts."""
    print("📊 Updating document counts in introduction.md...")
    
    # Count actual documents
    counts = count_documents()
    
    print(f"   Found:")
    print(f"   • Ordinances: {counts['ordinances']}")
    print(f"   • Resolutions: {counts['resolutions']}")  
    print(f"   • Interpretations: {counts['interpretations']}")
    print(f"   • Transcripts: {counts['transcripts']}")
    print(f"   • Other: {counts['other']}")
    
    # Update the file
    if update_introduction_counts(counts):
        print("✅ Document counts updated successfully")
    else:
        print("ℹ️  No changes needed")

if __name__ == "__main__":
    main()