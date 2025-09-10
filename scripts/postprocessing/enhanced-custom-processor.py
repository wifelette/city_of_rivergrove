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
            
            # Check if table is already wrapped
            parent = table.parent
            if not (parent and parent.name == 'div' and 'table-wrapper' in parent.get('class', [])):
                # Wrap table in responsive container only if not already wrapped
                wrapper = soup.new_tag('div', attrs={'class': 'table-wrapper'})
                if is_fee_schedule:
                    wrapper['class'] = wrapper.get('class', []) + ['fee-schedule-table']
                
                table.wrap(wrapper)
            
            # Add striped rows class if not already present
            existing_classes = table.get('class', [])
            if 'formatted-table' not in existing_classes:
                table['class'] = existing_classes + ['formatted-table']
            
            # Process table footnotes
            # Look for superscript numbers in cells
            for cell in table.find_all(['td', 'th']):
                text = cell.get_text()
                if re.search(r'[¹²³⁴⁵]', text) or re.search(r'\*+\d*', text):
                    existing_classes = cell.get('class', [])
                    if 'has-footnote' not in existing_classes:
                        cell['class'] = existing_classes + ['has-footnote']
        
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
    
    def process_document_notes(self, soup):
        """Process document notes sections with special styling"""
        
        # Find all h2 elements that might be note sections
        note_headers = [
            'Document Notes',
            'Digitization Notes', 
            'Source Document Notes',
            'Historical Notes',
            'Handwritten notations',
            'Handwritten Notations'
        ]
        
        # Process h2 elements - need to collect them first to avoid modifying during iteration
        h2_elements = list(soup.find_all('h2'))
        
        for h2 in h2_elements:
            # Skip if already processed (inside document-note div)
            if h2.parent and 'document-note' in h2.parent.get('class', []):
                continue
                
            header_text = h2.get_text().strip()
            
            # Check if this is a notes section (partial match allowed)
            is_notes_section = False
            for note_header in note_headers:
                if note_header.lower() in header_text.lower() or \
                   ('handwritten' in header_text.lower() and 'notation' in header_text.lower()):
                    is_notes_section = True
                    break
            
            if is_notes_section:
                # Create a new div with document-note class
                note_div = soup.new_tag('div', attrs={'class': 'document-note'})
                
                # Create a new h2 with standardized text
                new_h2 = soup.new_tag('h2')
                new_h2.string = 'Document Notes'
                note_div.append(new_h2)
                
                # Collect all following siblings until we find an h2 that's NOT a note type
                current = h2.next_sibling
                elements_to_move = []
                
                # List of headers that are note type labels (not section breaks)
                note_type_headers = ['handwritten note', 'stamp', 'digitization note', 
                                   'editor note', 'historical note', 'source note']
                
                while current:
                    next_sibling = current.next_sibling
                    
                    # Check if this is an h2
                    if hasattr(current, 'name'):
                        if current.name == 'h2':
                            # Check if it's a note type header (should be included)
                            h2_text = current.get_text().strip().lower().rstrip(':')
                            is_note_type = any(note_type in h2_text for note_type in note_type_headers)
                            
                            if not is_note_type:
                                # This is a different section, stop here
                                break
                        elif current.name == 'hr':
                            break
                        
                        if current.name:  # Collect the element
                            elements_to_move.append(current.extract())
                    
                    current = next_sibling
                
                # Move all collected elements into the note div
                for elem in elements_to_move:
                    note_div.append(elem)
                
                # Process H3 headers within the note div as note type labels
                import re
                for h3 in note_div.find_all('h3'):
                    # Get the header text and check for page reference
                    h3_text = h3.get_text().strip()
                    page_ref = None
                    
                    # Check if the header itself contains a page reference
                    page_match = re.search(r'\[page (\d+)\]', h3_text)
                    if page_match:
                        page_ref = page_match.group(1)
                        # Remove the page reference from the label text
                        label_text = re.sub(r'\s*\[page \d+\]\s*', '', h3_text).strip().rstrip(':')
                    else:
                        label_text = h3_text.rstrip(':')
                    
                    # Create a new structure with label
                    note_item = soup.new_tag('div', attrs={'class': 'note-item'})
                    
                    # Create content div for following content
                    content_div = soup.new_tag('div', attrs={'class': 'note-content'})
                    
                    # Collect content between this h3 and the next h3/h2 or end
                    current = h3.next_sibling
                    
                    while current and (not hasattr(current, 'name') or (current.name != 'h3' and current.name != 'h2')):
                        next_sib = current.next_sibling
                        if hasattr(current, 'name') and current.name:
                            content_div.append(current.extract())
                        current = next_sib
                    
                    # Create the label span with page reference if found
                    label_span = soup.new_tag('span', attrs={'class': 'note-type-label'})
                    if page_ref:
                        # Add the label text as a text node
                        label_span.append(label_text)
                        # Add separator
                        separator = soup.new_tag('span', attrs={'class': 'label-separator'})
                        separator.string = ' · '
                        label_span.append(separator)
                        # Add page reference
                        page_span = soup.new_tag('span', attrs={'class': 'label-page-ref'})
                        page_span.string = f'PAGE {page_ref}'
                        label_span.append(page_span)
                    else:
                        label_span.string = label_text
                    
                    note_item.append(label_span)
                    note_item.append(content_div)
                    
                    # Replace the h3 with the note item
                    h3.replace_with(note_item)
                
                # Process paragraphs to wrap page references in spans
                import re
                for p in note_div.find_all('p'):
                    # Get the current HTML content of the paragraph
                    p_html = str(p)
                    
                    # Skip if already processed (has note-item class)
                    if p.parent and 'note-item' in p.parent.get('class', []):
                        continue
                        
                    # Check if this paragraph starts with a bold label (e.g., **Handwritten Notes:**)
                    if '<strong>' in p_html and '</strong>:' in p_html:
                        # Extract the label and content - handle both inline and multi-line
                        # Match pattern: <p><strong>Label</strong>:\nContent</p>
                        label_match = re.match(r'^<p><strong>([^<]+)</strong>:\s*(.*?)</p>$', p_html, re.DOTALL)
                        if label_match:
                            label_text = label_match.group(1)
                            content_text = label_match.group(2)
                            
                            # Create a new structure with label and content
                            new_p = soup.new_tag('div', attrs={'class': 'note-item'})
                            
                            # Create the label span
                            label_span = soup.new_tag('span', attrs={'class': 'note-type-label'})
                            label_span.string = label_text
                            new_p.append(label_span)
                            
                            # Create the content div
                            content_div = soup.new_tag('div', attrs={'class': 'note-content'})
                            # Parse the content HTML to preserve any formatting
                            content_soup = BeautifulSoup(content_text, 'html.parser')
                            for elem in content_soup:
                                if hasattr(elem, 'name'):
                                    content_div.append(elem)
                                else:
                                    content_div.append(str(elem))
                            new_p.append(content_div)
                            
                            # Replace the original paragraph
                            p.replace_with(new_p)
                            p = new_p  # Update reference for page ref processing below
                    
                    # Process page references (skip if already processed)
                    if hasattr(p, 'find_all'):
                        p_html = str(p)
                        new_p_html = p_html  # Default to no change
                        # Only wrap if not already wrapped
                        if 'page-ref' not in p_html:
                            # Replace [page X] patterns with wrapped versions
                            new_p_html = re.sub(
                                r'(\[page \d+\])',
                                r'<span class="page-ref">\1</span>',
                                p_html
                            )
                        # If we made changes, replace the element
                        if new_p_html != p_html:
                            if p.name == 'div':
                                new_p = BeautifulSoup(new_p_html, 'html.parser').div
                            else:
                                new_p = BeautifulSoup(new_p_html, 'html.parser').p
                            if new_p:
                                p.replace_with(new_p)
                
                # Replace the original h2 with the note div
                h2.replace_with(note_div)
        
        # Also process any existing document-note divs to add page-ref spans and style labels
        import re
        for note_div in soup.find_all('div', class_='document-note'):
            for p in note_div.find_all('p'):
                # Get the current HTML content of the paragraph
                p_html = str(p)
                
                # Skip if already processed (has note-item class)
                if 'note-item' in p.parent.get('class', []):
                    continue
                    
                # Check if this paragraph starts with a bold label (e.g., **Handwritten Notes:**)
                if '<strong>' in p_html and '</strong>' in p_html:
                    # Extract the label and content - handle both inline and multi-line
                    label_match = re.search(r'<strong>([^<]+)</strong>:\s*(.*)', p_html, re.DOTALL)
                    if label_match:
                        label_text = label_match.group(1)
                        content_text = label_match.group(2)
                        
                        # Create a new structure with label and content
                        new_p = soup.new_tag('div', attrs={'class': 'note-item'})
                        
                        # Create the label span
                        label_span = soup.new_tag('span', attrs={'class': 'note-type-label'})
                        label_span.string = label_text
                        new_p.append(label_span)
                        
                        # Create the content div
                        content_div = soup.new_tag('div', attrs={'class': 'note-content'})
                        # Parse the content HTML to preserve any formatting
                        content_soup = BeautifulSoup(content_text, 'html.parser')
                        for elem in content_soup:
                            if hasattr(elem, 'name'):
                                content_div.append(elem)
                            else:
                                content_div.append(str(elem))
                        new_p.append(content_div)
                        
                        # Replace the original paragraph
                        p.replace_with(new_p)
                        p = new_p  # Update reference for page ref processing below
                
                # Process page references (skip if already processed)
                if hasattr(p, 'find_all'):
                    p_html = str(p)
                    new_p_html = p_html  # Default to no change
                    # Only wrap if not already wrapped
                    if 'page-ref' not in p_html:
                        # Replace [page X] patterns with wrapped versions
                        new_p_html = re.sub(
                            r'(\[page \d+\])',
                            r'<span class="page-ref">\1</span>',
                            p_html
                        )
                    # If we made changes, replace the element
                    if new_p_html != p_html:
                        if p.name == 'div':
                            new_p = BeautifulSoup(new_p_html, 'html.parser').div
                        else:
                            new_p = BeautifulSoup(new_p_html, 'html.parser').p
                        if new_p:
                            p.replace_with(new_p)
        
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
        
        # Form field processing is handled by sync scripts
        # (no processing needed here)
        
        return soup
    
    def add_custom_css(self, soup):
        """CSS is now in modular files - no need to inject inline styles"""
        # Styles are loaded via theme/css/main.css imports:
        # - documents/document-notes.css
        # - components/form-fields.css  
        # - layout/mdbook-overrides.css
        
        # Remove any old inline styles
        old_style = soup.find('style', id='enhanced-formatting-styles')
        if old_style:
            old_style.decompose()
        
        return soup
    
    
    # DEPRECATED CODE REMOVED - CSS now in modular files
    # All styles moved to:
    # - theme/css/documents/document-notes.css
    # - theme/css/components/form-fields.css
    # - theme/css/layout/mdbook-overrides.css
    
    """
    # Old code kept for reference only:
    style = soup.new_tag('style', id='enhanced-formatting-styles')
    style.string = '''
            /* Enhanced formatting for special document types */
            
            /* Document Notes styling */
            .document-note {
                margin: 30px 0;
                padding: 20px 20px 20px 50px;
                background: white;
                border: 1px solid #e9ecef;
                border-radius: 6px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04);
                position: relative;
            }
            
            .document-note::before {
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: #6c757d;
                border-radius: 6px 6px 0 0;
            }
            
            .document-note::after {
                content: "📝";
                position: absolute;
                left: 18px;
                top: 20px;
                font-size: 18px;
                opacity: 0.7;
            }
            
            .document-note h2 {
                margin-top: 0;
                margin-bottom: 15px;
                font-size: 1.1em;
                color: #495057;
                border: none;
                padding: 0;
            }
            
            .document-note p {
                margin: 8px 0;
                line-height: 1.6;
                color: #212529;
            }
            
            /* Style for page references in document notes */
            .document-note p:has(strong) {
                position: relative;
            }
            
            /* Target text in brackets that looks like page references */
            .page-ref {
                color: #6c757d;
                font-size: 0.9em;
            }
            
            /* Note type labels (e.g., Handwritten text, Stamp) */
            .note-item {
                margin: 12px 0;
            }
            
            .note-type-label {
                display: inline-block;
                padding: 3px 8px;
                margin-bottom: 6px;
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
            
            .label-separator {
                color: #9ca3af;
                margin: 0 2px;
                font-weight: 400;
            }
            
            .label-page-ref {
                color: #6b7280;
                font-weight: 500;
            }
            
            .note-content {
                margin-left: 0;
                line-height: 1.6;
            }
            
            .note-content br {
                display: block;
                margin: 4px 0;
            }
            
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
                background: linear-gradient(135deg, #6c757d 0%, #495057 100%);
                color: white;
            }
            
            .formatted-table th {
                padding: 12px 16px;
                text-align: left;
                font-weight: 600;
                border-bottom: 2px solid #495057;
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
            /* Form field styles are handled by custom-list-processor.py */
            
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
            }
    '''  # End of CSS string
    # head.append(style)  # Commented out - CSS now in modular files
    """
    
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
        
        # Process document notes sections
        soup = self.process_document_notes(soup)
        
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