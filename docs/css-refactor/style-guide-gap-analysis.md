# Style Guide Gap Analysis and Enhancement Plan

**Date:** January 2025  
**Current Coverage:** ~40-50% of CSS components

## Executive Summary

The current style guide documents core design tokens and basic components well but is missing critical document-specific patterns, enhanced elements, and interactive features essential for content creators and developers.

## Current State Assessment

### ✅ What's Currently Documented

#### Design Tokens
- Color palette (primary, secondary, warning, purple, backgrounds)
- Typography hierarchy (H1-H6)
- Spacing system (padding scale)
- CSS variables usage examples

#### Basic Components
- Buttons (default, primary, secondary, sizes)
- Navigation controls (view toggles, sort toggles)
- Search input
- Document cards (ordinances, resolutions)
- Simple cards
- Basic tables with footnotes
- Document links
- Document notes (basic example)
- Relationship badges

#### Documentation
- Code examples
- CSS variable usage
- Component structure
- Import structure
- Architecture overview

### ❌ Critical Gaps Identified

## High Priority - Document-Specific Patterns

### 1. Form Fields
**CSS Classes:** `form-field-filled`, `form-field-empty`, size variations
- Blue background filled fields with tooltips
- Empty fields with hover states
- Size variations (short, medium, long)
- Context behavior (in headings, tables)
- Markdown syntax: `{{filled:text}}`, `{{empty:size}}`

### 2. Document Notes Components
**CSS Classes:** `document-note`, `note-type-label`, `note-content`
- Note type labels with badges
- Page references (`{{page:n}}` syntax)
- Label separators
- Stamp/handwritten text formatting
- Proper H3 header syntax with page refs

### 3. Enhanced Lists
**CSS Classes:** `letter-item`, `definition-item`, `custom-numbered-list`
- Letter lists: (a), (b), (c) style
- Definition items: Section markers in resolutions
- Custom numbered lists: Roman numerals, custom starts
- Nested numbering patterns

### 4. WHEREAS Clauses
**CSS Classes:** `whereas-clause`, `whereas-marker`
- Special formatting for resolution preambles
- Auto-highlighted WHEREAS text

### 5. Signature Blocks
**CSS Classes:** `signature-block`, `signature-line`, `attestation-block`
- Signature lines with proper spacing
- Attestation blocks
- Signature titles and dates
- City seal placement

## Medium Priority - UI Components

### 6. Enhanced Tables
**CSS Classes:** `formatted-table`, `fee-schedule-table`, `table-wrapper`
- Header styling with background colors
- Row hover effects
- Alternating row colors
- Fee schedule specific formatting
- Tables with footnotes (`has-footnote`)

### 7. Navigation Sidebar
**CSS Classes:** `sidebar`, `nav-header`, `nav-stats`
- Chapter navigation structure
- Sidebar scrollbox behavior
- Resize handle functionality
- Active/selected states
- Document count display

### 8. Relationships Panel
**CSS Classes:** `right-panel`, `relationship-section`, `relationship-item`
- Collapsed/expanded states
- Panel toggle button
- Current document display
- Color-coded relationship types
- Relationship counts badges

### 9. Interactive Controls
**CSS Classes:** `dropdown`, `toggle-switch`, `section-selector`
- Section selector dropdown
- Toggle switches with sliders
- Dropdown arrows and states
- Active/inactive states

## Low Priority - Additional Patterns

### 10. Responsive Patterns
- Mobile-specific styles
- Tablet breakpoints
- Print styles (`@media print`)
- Dark mode variations

### 11. Auto-Generated Elements
- Page references (`page-ref`)
- Cross-reference links
- Section quotes (`section-quote`)
- Nested sections (`nested-section`)

## Implementation Plan

### Phase 1: Critical Document Patterns (Immediate)
1. **Form Fields Section** - All states, sizes, contexts
2. **Document Notes Section** - Complete syntax guide
3. **Enhanced Lists Section** - All list types
4. **WHEREAS Clauses** - Resolution formatting

### Phase 2: Essential Components (Week 1)
5. **Signature Blocks** - All signature patterns
6. **Enhanced Tables** - All table types
7. **Navigation Sidebar** - Complete documentation
8. **Relationships Panel** - All states

### Phase 3: Polish & Completeness (Week 2)
9. **Interactive Controls** - All control types
10. **Responsive Behaviors** - All breakpoints
11. **Print & Theme Styles** - Special contexts
12. **Auto-Generated Content** - Postprocessor patterns

## Style Guide Structure Improvements

### Navigation & Organization
1. **Add Table of Contents**
   - Sticky sidebar navigation
   - Collapsible sections
   - Search functionality
   - Quick jump links

2. **Reorganize Sections**
   - Foundation (variables, tokens, typography)
   - Layout Components (page structure, navigation)
   - Content Components (cards, tables, lists)
   - Document Components (form fields, notes, signatures)
   - Interactive Components (dropdowns, toggles, panels)
   - Patterns & States (responsive, print, themes)

### Content Improvements
3. **Remove outdated artifacts**
   - Phase 5 references
   - Implementation metrics
   - Development timeline references

4. **Add practical features**
   - "Copy Code" buttons
   - Live/interactive examples
   - Markdown syntax alongside HTML
   - Visual indicators for auto-generated patterns

### Technical Enhancements
5. **Improve examples**
   - Use real document content
   - Show both source and rendered output
   - Include context/usage notes
   - Add accessibility notes

## Success Metrics

- [ ] 100% of production CSS classes documented
- [ ] All postprocessor-generated patterns included
- [ ] Examples for every component variant
- [ ] Searchable/navigable interface
- [ ] Clear markdown → HTML mapping for content creators
- [ ] Accessibility guidelines for each component

## Notes for Implementation

1. **Priority on document patterns** - These are most critical for content editors
2. **Use real examples** from actual documents
3. **Include both markdown syntax and rendered output** for postprocessor patterns
4. **Visual indicators** for auto-generated vs manual patterns
5. **Consider making searchable** for quick lookup

## Files to Reference

- CSS components: `theme/css/components/`
- Document styles: `theme/css/documents/`
- Postprocessors: `scripts/postprocessing/`
- Visual tests: `tests/visual/specs/`
- Example documents: `book/` (rendered HTML)