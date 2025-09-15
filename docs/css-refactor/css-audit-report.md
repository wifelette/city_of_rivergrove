# CSS Audit Report - Production vs Style Guide

## Executive Summary
Date: 2025-09-14
Total CSS Classes in Production: 152
Classes Documented in Style Guide: ~60-70 (estimated)
Coverage: ~45%

## CSS Classes by Category

### ✅ Documented in Style Guide

#### Form Fields
- `.form-field-filled` - ✅ Documented
- `.form-field-empty` - ✅ Documented
- `.form-field-short` - ✅ Documented
- `.form-field-medium` - ✅ Documented
- `.form-field-long` - ✅ Documented

#### Document Notes
- `.document-notes` - ✅ Documented
- `.document-note` - ✅ Documented
- `.note-type-label` - ✅ Documented
- `.note-content` - ✅ Documented
- `.note-item` - ✅ Documented

#### Enhanced Lists
- `.alpha-list` - ✅ Documented
- `.alpha-list-no-bullets` - ✅ Documented
- `.numeric-list` - ✅ Documented
- `.numeric-list-no-bullets` - ✅ Documented
- `.roman-list` - ✅ Documented
- `.roman-list-no-bullets` - ✅ Documented
- `.letter-item` - ✅ Documented
- `.letter-marker` - ✅ Documented
- `.list-marker-alpha` - ✅ Documented
- `.list-marker-numeric` - ✅ Documented
- `.list-marker-roman` - ✅ Documented
- `.whereas-clause` - ✅ Documented
- `.whereas-marker` - ✅ Documented

#### Cards
- `.doc-card` - ✅ Documented
- `.doc-title` - ✅ Documented
- `.doc-year` - ✅ Documented
- `.doc-number` - ✅ Documented
- `.doc-meta` - ✅ Documented
- `.simple-cards` - ✅ Documented
- `.simple-card` - ✅ Documented
- `.ordinances-card` - ✅ Documented
- `.resolutions-card` - ✅ Documented

#### Tables
- `.formatted-table` - ✅ Documented
- `.fee-schedule-table` - ✅ Documented
- `.table-wrapper` - ✅ Documented
- `.footnotes` - ✅ Documented
- `.footnote-definition` - ✅ Documented

### ❌ Missing from Style Guide

#### Navigation Components (Priority 2)
- `.sidebar` - ❌ Not documented
- `.sidebar-scrollbox` - ❌ Not documented
- `.sidebar-resize-handle` - ❌ Not documented
- `.sidebar-resize-indicator` - ❌ Not documented
- `.sidebar-resizing` - ❌ Not documented
- `.sidebar-transitioning` - ❌ Not documented
- `.sidebar-toggle` - ❌ Not documented
- `.nav-wrapper` - ❌ Not documented
- `.nav-header` - ❌ Not documented
- `.nav-stats` - ❌ Not documented
- `.nav-controls` - ❌ Not documented
- `.nav-search` - ❌ Not documented
- `.nav-search-input` - ❌ Not documented
- `.nav-search-clear` - ❌ Not documented
- `.nav-view` - ❌ Not documented
- `.nav-view-toggle` - ❌ Not documented
- `.nav-btn` - ❌ Not documented
- `.nav-chapters` - ❌ Not documented
- `.nav-section-selector` - ❌ Not documented
- `.nav-section-dropdown` - ❌ Not documented
- `.section-dropdown-btn` - ❌ Not documented
- `.section-option` - ❌ Not documented

#### Relationships Panel (Priority 2)
- `.right-panel` - ❌ Not documented
- `.right-panel-header` - ❌ Not documented
- `.right-panel-content` - ❌ Not documented
- `.panel-placeholder` - ❌ Not documented
- `.panel-toggle` - ❌ Not documented
- `.relationship-section` - ❌ Not documented
- `.relationship-items` - ❌ Not documented
- `.relationship-item` - ❌ Not documented
- `.relationship-count` - ❌ Not documented
- `.references` - ❌ Not documented
- `.amendments` - ❌ Not documented
- `.interpretations` - ❌ Not documented
- `.related` - ❌ Not documented
- `.rel-doc-type` - ❌ Not documented
- `.rel-doc-number` - ❌ Not documented
- `.rel-doc-title` - ❌ Not documented

#### Signature Blocks (Priority 2)
- `.signature-block` - ❌ Not documented
- `.signature-line` - ❌ Not documented
- `.signature-title` - ❌ Not documented
- `.signature-date` - ❌ Not documented
- `.signature-mark` - ❌ Not documented (has tooltip issue #25)
- `.attestation-block` - ❌ Not documented

#### Interactive Controls (Priority 3)
- `.toggle` - ❌ Not documented
- `.toggle-switch` - ❌ Not documented
- `.toggle-slider` - ❌ Not documented
- `.dropdown-arrow` - ❌ Not documented
- `.sort-toggle` - ❌ Not documented
- `.sort-toggle-btn` - ❌ Not documented
- `.hide-boring` - ❌ Not documented

#### Definition Lists
- `.definition-list` - ❌ Not documented
- `.definition-item` - ❌ Not documented
- `.definition-marker` - ❌ Not documented
- `.definition-separator` - ❌ Not documented
- `.definition-term` - ❌ Not documented
- `.definition-text` - ❌ Not documented

#### Custom List Processing
- `.custom-numbered-list` - ❌ Not documented
- `.custom-list-marker` - ❌ Not documented
- `.custom-controlled` - ❌ Not documented
- `.special-list-number` - ❌ Not documented
- `.special-start-list` - ❌ Not documented
- `.roman-marker` - ❌ Not documented
- `.roman-parenthetical-list` - ❌ Not documented
- `.roman-sublist` - ❌ Not documented
- `.roman-sublist-item` - ❌ Not documented

#### mdBook Components
- `.chapter` - ❌ Not documented
- `.chapter-item` - ❌ Not documented
- `.part-title` - ❌ Not documented
- `.menu-title` - ❌ Not documented
- `.page` - ❌ Not documented
- `.page-wrapper` - ❌ Not documented
- `.content` - ❌ Not documented
- `.header` - ❌ Not documented
- `.affix` - ❌ Not documented
- `.boring` - ❌ Not documented

#### Utility Classes
- `.active` - ❌ Not documented
- `.collapsed` - ❌ Not documented
- `.selected` - ❌ Not documented
- `.hidden` - ❌ Not documented
- `.current-document` - ❌ Not documented
- `.spacer` - ❌ Not documented
- `.left` - ❌ Not documented
- `.right` - ❌ Not documented
- `.next` - ❌ Not documented
- `.previous` - ❌ Not documented

#### Document-Specific
- `.document-figure` - ❌ Not documented
- `.section-quote` - ❌ Not documented
- `.section-ref` - ❌ Not documented
- `.label-page-ref` - ❌ Not documented
- `.label-separator` - ❌ Not documented
- `.topic-group` - ❌ Not documented
- `.grouped-item` - ❌ Not documented
- `.nested-section` - ❌ Not documented

#### Meeting Materials
- `.transcripts-card` - ❌ Not documented
- `.interpretations-card` - ❌ Not documented

## Key Findings

### 1. Coverage Gaps
- **Navigation System**: Entire navigation sidebar and controls undocumented (~24 classes)
- **Relationships Panel**: Complete right panel system undocumented (~16 classes)
- **Signature Blocks**: Critical document component missing (~6 classes)
- **Definition Lists**: Entire definition list system undocumented (~6 classes)
- **Custom List Processing**: Postprocessor-generated classes undocumented (~10 classes)

### 2. Priority Actions

#### High Priority
1. Document signature blocks (resolves Issue #25 context)
2. Document navigation system components
3. Document relationships panel

#### Medium Priority
1. Document definition lists
2. Document custom list processing classes
3. Document interactive controls

#### Low Priority
1. Document mdBook default classes
2. Document utility classes
3. Document edge cases

### 3. Markdown Pattern Verification Needed

Need to verify these markdown patterns trigger correct CSS:
- `{{signature}}` markers → `.signature-mark`
- `{{filled:text}}` patterns → `.form-field-*`
- `(a)`, `(b)`, `(c)` lists → `.alpha-list`
- `(i)`, `(ii)`, `(iii)` lists → `.roman-list`
- Definition lists → `.definition-*`
- WHEREAS clauses → `.whereas-*`

### 4. Processing Pipeline Verification

Need to verify these processors generate expected classes:
- `unified-list-processor.py` → custom list classes
- `enhanced-custom-processor.py` → enhanced element classes
- `form-fields-processor.py` → form field classes
- `sync-resolutions.py` → signature markers

## Recommendations

1. **Immediate Actions**:
   - Fix signature tooltip issue (#25)
   - Document all Priority 2 components from Issue #24
   - Complete navigation polish from Issue #19

2. **Style Guide Improvements**:
   - Add navigation/TOC to style guide
   - Include markdown → HTML examples
   - Add copy code buttons
   - Create searchable interface

3. **Testing Strategy**:
   - Create visual regression tests
   - Add CSS validation to build pipeline
   - Test all markdown patterns systematically

4. **Documentation**:
   - Update STYLE-GUIDE.md with missing patterns
   - Create CSS troubleshooting guide
   - Document postprocessor transformations

## Next Steps

1. Start with signature block documentation and fix tooltip issue
2. Document navigation components systematically
3. Create comprehensive test suite for markdown patterns
4. Update Style Guide with all missing components
5. Implement search and navigation in Style Guide