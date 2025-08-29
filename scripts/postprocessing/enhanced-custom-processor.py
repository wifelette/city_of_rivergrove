#!/usr/bin/env python3
"""
Enhanced custom processor for City of Rivergrove documents.
Handles special formatting beyond standard list processing:
- Tables with proper styling
- WHEREAS clauses
- Definition lists with bold terms
- Complex nested structures
- Document-specific formatting rules
"""

import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup
import json

class DocumentProcessor:
    def __init__(self):
        # Document-specific rules can be defined here
        self.document_rules = {
            'sign': ['definitions', 'whereas', 'tables'],
            'fee': ['tables', 'fee_schedule'],
            'wqra': ['tables', 'complex_nesting'],
            'land-development': ['nested_quotes', 'whereas'],
        }
    
    def identify_document_type(self, filepath):
        """Identify document type from filename"""
        filename = filepath.name.lower()
        
        if 'sign' in filename or '81-2011' in filename:
            return 'sign'
        elif 'fee' in filename or '259' in filename or '300' in filename:
            return 'fee'
        elif 'wqra' in filename or '70-2001' in filename:
            return 'wqra'
        elif 'land-development' in filename or '54-89' in filename or '59-97' in filename:
            return 'land-development'
        else:
            return 'standard'
    
    def process_standard_lists(self, soup):
        """Process standard numbered, letter, and roman numeral lists"""
        
        # Process (1), (2), (3) style lists
        for p in soup.find_all('p'):
            text = p.get_text()
            
            # Check for numbered items
            if re.search(r'\(\d+\)', text):
                lines = text.split('\n')
                numbered_items = []
                
                for line in lines:
                    match = re.match(r'^(\((\d+)\))\s+(.+)$', line.strip())
                    if match:
                        numbered_items.append({
                            'marker': match.group(1),
                            'number': match.group(2),
                            'text': match.group(3)
                        })
                
                if len(numbered_items) > 1:
                    ol = soup.new_tag('ol', attrs={'class': 'custom-numbered-list'})
                    for item in numbered_items:
                        li = soup.new_tag('li')
                        marker_span = soup.new_tag('span', attrs={'class': 'custom-list-marker'})
                        marker_span.string = item['marker']
                        li.append(marker_span)
                        li.append(' ' + item['text'])
                        ol.append(li)
                    p.replace_with(ol)
        
        return soup
    
    def process_letter_lists(self, soup):
        """Process (a), (b), (c) style lists"""
        
        for p in soup.find_all('p'):
            text = p.get_text()
            
            # Check for letter markers
            match = re.match(r'^(\(([a-z])\))\s+(.+)$', text.strip(), re.IGNORECASE)
            if match:
                div = soup.new_tag('div', attrs={'class': 'letter-item'})
                
                marker_span = soup.new_tag('span', attrs={'class': 'letter-marker'})
                marker_span.string = match.group(1)
                div.append(marker_span)
                
                content_span = soup.new_tag('span', attrs={'class': 'letter-content'})
                content_span.string = ' ' + match.group(3)
                div.append(content_span)
                
                p.replace_with(div)
        
        return soup
    
    def process_whereas_clauses(self, soup):
        """Style WHEREAS clauses specially"""
        
        for p in soup.find_all('p'):
            text = p.get_text()
            
            if text.strip().startswith('WHEREAS,'):
                p['class'] = p.get('class', []) + ['whereas-clause']
                
                # Bold the WHEREAS part
                html = str(p)
                html = html.replace('WHEREAS,', '<span class="whereas-marker">WHEREAS,</span>')
                new_p = BeautifulSoup(html, 'html.parser').find('p')
                if new_p:
                    p.replace_with(new_p)
        
        return soup
    
    def process_definition_lists(self, soup):
        """Process definition lists with bold terms"""
        
        # Look for patterns like **Term**—Definition
        for p in soup.find_all('p'):
            html = str(p)
            
            # Pattern for definition lists
            if '**' in html and '—' in html:
                # Extract the term and definition
                pattern = r'\*\*([^*]+)\*\*—(.+)'
                match = re.search(pattern, html)
                
                if match:
                    div = soup.new_tag('div', attrs={'class': 'definition-item'})
                    
                    term_span = soup.new_tag('span', attrs={'class': 'definition-term'})
                    term_span.string = match.group(1)
                    div.append(term_span)
                    
                    separator_span = soup.new_tag('span', attrs={'class': 'definition-separator'})
                    separator_span.string = '—'
                    div.append(separator_span)
                    
                    def_span = soup.new_tag('span', attrs={'class': 'definition-text'})
                    def_span.string = match.group(2)
                    div.append(def_span)
                    
                    p.replace_with(div)
        
        return soup
    
    def enhance_tables(self, soup):
        """Enhance table formatting and add responsive wrappers"""
        
        for table in soup.find_all('table'):
            # Check if this is a fee schedule table
            is_fee_schedule = False
            
            # Look for fee-related headers
            headers = table.find_all('th')
            for header in headers:
                if 'fee' in header.get_text().lower() or 'deposit' in header.get_text().lower():
                    is_fee_schedule = True
                    break
            
            # Wrap table in responsive container
            wrapper = soup.new_tag('div', attrs={'class': 'table-wrapper'})
            if is_fee_schedule:
                wrapper['class'] = wrapper.get('class', []) + ['fee-schedule-table']
            
            table.wrap(wrapper)
            
            # Add striped rows class
            table['class'] = table.get('class', []) + ['formatted-table']
            
            # Process table footnotes
            # Look for superscript numbers in cells
            for cell in table.find_all(['td', 'th']):
                text = cell.get_text()
                if re.search(r'[¹²³⁴⁵]', text) or re.search(r'\*+\d*', text):
                    cell['class'] = cell.get('class', []) + ['has-footnote']
        
        return soup
    
    def process_nested_quotes(self, soup):
        """Process nested quoted sections (like in Land Development ordinances)"""
        
        # Look for blockquotes containing section references
        for blockquote in soup.find_all('blockquote'):
            # Check if it contains section formatting
            text = blockquote.get_text()
            if 'Section' in text:
                blockquote['class'] = blockquote.get('class', []) + ['section-quote']
        
        return soup
    
    def process_form_fields(self, soup):
        """Process form field markers for blank and filled fields"""
        
        # Process [BLANK] markers - convert to styled empty fields
        for p in soup.find_all(['p', 'li', 'td', 'div']):
            html = str(p)
            
            # Pattern for blank field markers from preprocessing
            if '[BLANK' in html:
                # Replace different blank sizes
                replacements = [
                    (r'\[BLANK:short\]', '<span class="form-field-blank form-field-blank-short" title="Blank in source document"></span>'),
                    (r'\[BLANK:medium\]', '<span class="form-field-blank form-field-blank-medium" title="Blank in source document"></span>'),
                    (r'\[BLANK:long\]', '<span class="form-field-blank form-field-blank-long" title="Blank in source document"></span>'),
                    (r'\[BLANK\]', '<span class="form-field-blank" title="Blank in source document"></span>'),
                ]
                
                for pattern, replacement in replacements:
                    html = re.sub(pattern, replacement, html)
                
                # Parse the modified HTML and replace the element
                new_elem = BeautifulSoup(html, 'html.parser')
                new_elem = new_elem.find(p.name)  # Get the same type of element
                if new_elem:
                    p.replace_with(new_elem)
        
        # Process [FILLED:text] markers - convert to styled filled fields
        for p in soup.find_all(['p', 'li', 'td', 'div']):
            html = str(p)
            
            # Pattern for filled field markers
            if '[FILLED:' in html:
                # Replace filled field markers with styled spans
                pattern = r'\[FILLED:([^\]]+)\]'
                replacement = r'<span class="form-field-filled" title="Hand-filled in source document">\1</span>'
                html = re.sub(pattern, replacement, html)
                
                # Parse the modified HTML and replace the element
                new_elem = BeautifulSoup(html, 'html.parser')
                new_elem = new_elem.find(p.name)  # Get the same type of element
                if new_elem:
                    p.replace_with(new_elem)
        
        return soup
    
    def add_custom_css(self, soup):
        """Add custom CSS for special formatting"""
        
        # Check if we've already added our custom CSS
        if soup.find('style', id='enhanced-formatting-styles'):
            return soup
        
        head = soup.find('head')
        if head:
            style = soup.new_tag('style', id='enhanced-formatting-styles')
            style.string = """
            /* Enhanced formatting for special document types */
            
            /* WHEREAS Clauses */
            .whereas-clause {
                margin: 1.5em 0;
                padding-left: 2em;
                position: relative;
            }
            
            .whereas-marker {
                font-weight: bold;
                color: #2c3e50;
            }
            
            /* Definition Lists */
            .definition-item {
                margin: 1.2em 0;
                padding: 0.8em;
                background: linear-gradient(to right, #f8f9fa 0%, transparent 100%);
                border-left: 3px solid #0969da;
            }
            
            .definition-term {
                font-weight: bold;
                color: #0969da;
                margin-right: 0.3em;
            }
            
            .definition-separator {
                margin: 0 0.3em;
                color: #6c757d;
            }
            
            .definition-text {
                color: #333;
            }
            
            /* Enhanced Tables */
            .table-wrapper {
                overflow-x: auto;
                margin: 1.5em 0;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }
            
            .fee-schedule-table {
                background: linear-gradient(to bottom, #f8f9fa 0%, white 100%);
                padding: 1em;
            }
            
            .formatted-table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                background: white;
            }
            
            .formatted-table thead {
                background: linear-gradient(135deg, #0969da 0%, #0856b6 100%);
                color: white;
            }
            
            .formatted-table th {
                padding: 12px 16px;
                text-align: left;
                font-weight: 600;
                border-bottom: 2px solid #0856b6;
            }
            
            .formatted-table td {
                padding: 10px 16px;
                border-bottom: 1px solid #e9ecef;
            }
            
            .formatted-table tbody tr:hover {
                background: #f8f9fa;
            }
            
            .formatted-table tbody tr:nth-child(even) {
                background: rgba(0, 105, 218, 0.02);
            }
            
            /* Cells with footnotes */
            .has-footnote {
                position: relative;
            }
            
            .has-footnote sup {
                color: #0969da;
                font-weight: bold;
            }
            
            /* Section Quotes */
            .section-quote {
                border-left: 4px solid #0969da;
                padding-left: 1.5em;
                margin: 1.5em 0;
                background: #f8f9fa;
                padding: 1em 1.5em;
                border-radius: 0 8px 8px 0;
            }
            
            /* Custom Numbered Lists */
            .custom-numbered-list {
                list-style: none;
                counter-reset: none;
                padding-left: 0;
            }
            
            .custom-numbered-list li {
                margin: 0.8em 0;
                padding-left: 2.5em;
                position: relative;
            }
            
            .custom-numbered-list .custom-list-marker {
                position: absolute;
                left: 0;
                font-weight: bold;
                color: #0969da;
            }
            
            /* Letter Items */
            .letter-item {
                margin: 0.8em 0;
                padding-left: 2.5em;
                position: relative;
            }
            
            .letter-marker {
                position: absolute;
                left: 0;
                font-weight: bold;
                color: #495057;
            }
            
            /* Nested structures */
            .nested-section {
                border-left: 2px solid #dee2e6;
                padding-left: 1em;
                margin-left: 1em;
                margin-top: 0.5em;
            }
            
            /* Form Fields - Blank fields */
            .form-field-blank {
                display: inline-block;
                border-bottom: 1px solid #999;
                min-width: 60px;
                height: 1.2em;
                margin: 0 2px;
                position: relative;
                cursor: help;
                vertical-align: baseline;
            }
            
            .form-field-blank-short {
                min-width: 40px;
            }
            
            .form-field-blank-medium {
                min-width: 80px;
            }
            
            .form-field-blank-long {
                min-width: 120px;
            }
            
            .form-field-blank:hover {
                background-color: #f0f0f0;
                border-bottom-color: #666;
            }
            
            /* Form Fields - Filled fields */
            .form-field-filled {
                display: inline;
                padding: 2px 4px;
                background-color: #e3f2fd;
                border-bottom: 2px solid #1976d2;
                color: #0d47a1;
                font-weight: 500;
                cursor: help;
                border-radius: 2px 2px 0 0;
            }
            
            .form-field-filled:hover {
                background-color: #bbdefb;
                border-bottom-color: #0d47a1;
            }
            
            /* Print styles */
            @media print {
                .table-wrapper {
                    box-shadow: none;
                    page-break-inside: avoid;
                }
                
                .formatted-table {
                    font-size: 0.9em;
                }
                
                .whereas-clause,
                .definition-item,
                .section-quote {
                    page-break-inside: avoid;
                }
                
                .form-field-blank {
                    border-bottom: 1px solid #666;
                    background: none;
                }
                
                .form-field-filled {
                    background-color: #f0f0f0;
                    border-bottom: 1px solid #333;
                    font-weight: bold;
                }
            }
            """
            head.append(style)
        
        return soup
    
    def process_html_file(self, filepath):
        """Process a single HTML file with all enhancements"""
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Identify document type
        doc_type = self.identify_document_type(filepath)
        
        # Apply standard processing
        soup = self.process_standard_lists(soup)
        soup = self.process_letter_lists(soup)
        
        # Apply document-specific processing
        if doc_type in self.document_rules:
            rules = self.document_rules[doc_type]
            
            if 'whereas' in rules:
                soup = self.process_whereas_clauses(soup)
            
            if 'definitions' in rules:
                soup = self.process_definition_lists(soup)
            
            if 'tables' in rules or 'fee_schedule' in rules:
                soup = self.enhance_tables(soup)
            
            if 'nested_quotes' in rules:
                soup = self.process_nested_quotes(soup)
        
        # Always enhance tables if present
        if soup.find_all('table'):
            soup = self.enhance_tables(soup)
        
        # Process form fields (blank and filled)
        soup = self.process_form_fields(soup)
        
        # Add custom CSS
        soup = self.add_custom_css(soup)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        print(f"  ✓ Enhanced processing for {filepath.name} (type: {doc_type})")
        
        return doc_type

def main():
    """Process all HTML files in the book directory"""
    book_dir = Path("book")
    
    if not book_dir.exists():
        print("Error: book directory not found")
        sys.exit(1)
    
    processor = DocumentProcessor()
    
    # Process all HTML files
    html_files = list(book_dir.glob("**/*.html"))
    
    print(f"Enhanced processing {len(html_files)} HTML files...")
    
    # Track document types processed
    doc_types = {}
    
    for filepath in html_files:
        try:
            doc_type = processor.process_html_file(filepath)
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
        except Exception as e:
            print(f"  ✗ Error processing {filepath.name}: {e}")
    
    # Summary
    print(f"\n✅ Enhanced processing complete")
    print(f"Document types processed:")
    for doc_type, count in sorted(doc_types.items()):
        print(f"  - {doc_type}: {count} files")

if __name__ == "__main__":
    main()