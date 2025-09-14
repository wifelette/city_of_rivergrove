#!/usr/bin/env python3
"""
Unified title resolution utility for the City of Rivergrove documentation system.

This module provides a consistent way to determine document titles across all scripts,
implementing a clear hierarchy:
1. Airtable short_title (highest priority)
2. Airtable display_name (extracted title portion)
3. Document front matter title
4. First H1 in document content
5. Filename-based inference (lowest priority)
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class TitleResolver:
    """Unified title resolution for documents."""
    
    def __init__(self, airtable_cache_path: str = "book/airtable-metadata.json"):
        """Initialize with optional Airtable cache path."""
        self.airtable_cache_path = Path(airtable_cache_path)
        self.airtable_data = self._load_airtable_cache()
        
    def _load_airtable_cache(self) -> Dict:
        """Load Airtable metadata cache."""
        if self.airtable_cache_path.exists():
            try:
                with open(self.airtable_cache_path, 'r') as f:
                    data = json.load(f)
                    return data.get('documents', {})
            except Exception as e:
                logger.warning(f"Could not load Airtable cache: {e}")
        return {}
    
    def get_document_key(self, filepath: Path) -> str:
        """Get the document key for Airtable lookup from filepath."""
        # Remove extension to get the key
        return filepath.stem
    
    def extract_title_from_display_name(self, display_name: str) -> str:
        """Extract clean title from Airtable display name."""
        # Remove document type prefix (Ordinance #123 -, Resolution #456 -, etc.)
        title = re.sub(r'^(Ordinance|Resolution|Interpretation)\s+#?\d+[-\w]*\s*-?\s*', '', display_name)
        # Remove year suffix (2024)
        title = re.sub(r'\s*\(\d{4}\)$', '', title)
        return title.strip()
    
    def extract_title_from_front_matter(self, content: str) -> Optional[str]:
        """Extract title from markdown front matter."""
        # Look for YAML front matter
        if content.startswith('---'):
            front_matter_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
            if front_matter_match:
                front_matter = front_matter_match.group(1)
                title_match = re.search(r'^title:\s*(.+)$', front_matter, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()
                    # Remove quotes if present
                    title = title.strip('"\'')
                    return title
        return None
    
    def strip_markdown_links(self, text: str) -> str:
        """Remove markdown links from text, keeping only the link text."""
        # Replace [text](url) with just text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        return text
    
    def extract_title_from_h1(self, content: str) -> Optional[str]:
        """Extract title from first H1 heading."""
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_match:
            title = h1_match.group(1).strip()
            # Strip any markdown links from the title
            title = self.strip_markdown_links(title)
            # Clean up common prefixes
            title = re.sub(r'^(Ordinance|Resolution)\s+#?\d+[-\w]*\s*-?\s*', '', title)
            return title
        return None
    
    def extract_title_from_content(self, content: str) -> Optional[str]:
        """Extract title from document content (AN ORDINANCE/RESOLUTION pattern)."""
        subject_match = re.search(
            r'^###?\s+AN?\s+(ORDINANCE|RESOLUTION)\s+(.+)$', 
            content, 
            re.MULTILINE | re.IGNORECASE
        )
        if subject_match:
            title = subject_match.group(2).strip()
            # Keep titles concise
            title = re.sub(r'^(ESTABLISHING|CREATING|AMENDING|ADOPTING|PROVIDING|DEFINING|RELATING TO)\s+', '', title, flags=re.IGNORECASE)
            # Truncate at first comma or "AND"
            title = re.sub(r'\s+(,|AND|TO).+$', '', title, flags=re.IGNORECASE)
            # Remove articles
            title = re.sub(r'^(THE|A|AN)\s+', '', title, flags=re.IGNORECASE)
            # Limit to 3 words
            words = title.split()[:3]
            return ' '.join(words).title()
        return None
    
    def extract_title_from_filename(self, filepath: Path) -> str:
        """Extract title from filename as last resort."""
        stem = filepath.stem
        
        # Extract topic from end of filename
        topic_match = re.search(r'-([^-]+)$', stem)
        if topic_match:
            topic = topic_match.group(1)
            topic = topic.replace('-', ' ').replace('_', ' ')
            
            # Handle special cases
            special_cases = {
                'WQRA': 'Water Quality Resource Area',
                'FEMA': 'FEMA Flood Map',
                'PC': 'Planning Commission',
            }
            
            for key, value in special_cases.items():
                if key in topic:
                    return value
            
            return topic.title()
        
        # Ultimate fallback - clean up filename
        name = re.sub(r'^\d{4}-(Ord|Res|RE)-#?\d+[-\w]*-', '', stem)
        name = name.replace('-', ' ').replace('_', ' ')
        return name.title()[:30]  # Limit length
    
    def resolve_title(self, filepath: Path, content: Optional[str] = None) -> tuple[str, str]:
        """
        Resolve document title using the defined hierarchy.
        
        Returns:
            tuple: (title, source) where source indicates where the title came from
        """
        # 1. Check Airtable short_title (highest priority)
        doc_key = self.get_document_key(filepath)
        airtable_info = self.airtable_data.get(doc_key, {})
        
        if airtable_info.get('short_title'):
            return (airtable_info['short_title'], 'airtable_short_title')
        
        # 2. Check Airtable display_name
        if airtable_info.get('display_name'):
            title = self.extract_title_from_display_name(airtable_info['display_name'])
            if title:
                return (title, 'airtable_display_name')
        
        # Load content if not provided
        if content is None and filepath.exists():
            try:
                content = filepath.read_text(encoding='utf-8')
            except Exception as e:
                logger.warning(f"Could not read file {filepath}: {e}")
                content = ""
        
        if content:
            # 3. Check front matter
            title = self.extract_title_from_front_matter(content)
            if title:
                return (title, 'front_matter')
            
            # 4. Check first H1
            title = self.extract_title_from_h1(content)
            if title:
                return (title, 'h1_heading')
            
            # 5. Check document content pattern
            title = self.extract_title_from_content(content)
            if title:
                return (title, 'content_pattern')
        
        # 6. Fallback to filename
        title = self.extract_title_from_filename(filepath)
        return (title, 'filename')
    
    def get_title_with_warning(self, filepath: Path, content: Optional[str] = None) -> str:
        """
        Get title and log warning if falling back to non-preferred source.
        """
        title, source = self.resolve_title(filepath, content)
        
        # Warn if we're using fallback sources
        if source in ['content_pattern', 'filename']:
            logger.info(f"Using {source} for {filepath.name} - consider adding to Airtable")
        
        return title

# Convenience function for simple usage
def get_document_title(filepath: Path, airtable_cache: str = "book/airtable-metadata.json") -> str:
    """Simple function to get a document title."""
    resolver = TitleResolver(airtable_cache)
    return resolver.get_title_with_warning(filepath)