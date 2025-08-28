# Navigation Redesign - Implementation Plan

## Current Status (August 27, 2025)

We've designed a new navigation system after extensive mockups and testing. After implementing Phase 1 and 2, we discovered fundamental architectural conflicts with mdBook that require a different approach (see Issue #15).

## Final Design Decision

### Left Sidebar - Clean and Document-Specific
- Each document type (Ordinances, Resolutions, Interpretations) has its own section
- Style E format: `#70 - WQRA` with year as small tag `[2001]`
- Document-appropriate controls:
  - **Ordinances**: View (List/By Decade/By Topic/By Number) + Order (Oldest/Newest)
  - **Resolutions**: Simpler controls (fewer documents)
  - **Interpretations**: View (By Date/By Code Section)
- NO mixing or nesting of document types in the main navigation

### Right Panel - Relationship Hub
Shows all connections for the currently viewed document:
- 📝 **Interpretations** (yellow accent) - interpretations of this ordinance
- 📋 **Related Ordinances** (blue accent) - references or amendments
- 📄 **Related Resolutions** (green accent) - implementing resolutions
- 🔄 **Amendment History** (purple accent) - evolution over time
- **Quick Actions** - View PDF, Download, Copy Link

### Main Content Area
- Clean display of document content
- Minimal formatting (note: current yellow notice box is too bold, needs refinement)

## Implementation Tasks

### Phase 1: Foundation ✅ COMPLETED
1. **Update generate-summary.py**
   - Change from: `2001 - Ordinance #70-2001-WQRA - 70-2001`
   - To Style E: `#70 - WQRA` with `[2001]` tag
   - Keep file paths unchanged

2. **Build relationship tracking**
   - Create `document-relationships.json`
   - Track: interpretations, references, amendments
   - Auto-generate from document content analysis

### Phase 2: mdBook Integration ⚠️ ISSUES FOUND
3. **Custom JavaScript for controls** ✅ Implemented
   - View switcher (List/Decade/Topic) 
   - Order toggle (Oldest/Newest)
   - Search within section

4. **Right panel template** ✅ Implemented
   - Inject via JavaScript

**Problems Discovered:**
- Fighting mdBook's sidebar control causes flickering
- Race conditions with mdBook's JavaScript
- Content loss due to DOM manipulation conflicts
- See Issue #15 for complete analysis

### Phase 3: Complete Sidebar Replacement (NEW APPROACH)
Instead of fighting mdBook's sidebar, we'll replace it entirely:
1. Hide mdBook's sidebar via CSS
2. Build our own sidebar from relationships.json
3. Handle navigation with History API
4. Clean state management without DOM fights

### Phase 4: Polish (Future)
5. **Fix note formatting** (too bold/large currently)
6. **Add view persistence** (remember user's preferred view)
7. **Implement deep linking** (link directly to specific views)

## File Structure
```
/src/
  SUMMARY.md (generated with Style E format)
  custom.css (styling for nav and panels)
  navigation.js (view controls and switching)
  relationships.json (document connections)
  /ordinances/
  /resolutions/
  /interpretations/
```

## Key Design Principles
1. **Separation**: Each document type has its own optimized UI
2. **Relationships**: All connections visible in right panel, not cluttering main nav
3. **Simplicity**: Left sidebar stays clean and scannable
4. **Context**: Right panel provides rich context without overwhelming

## Mockup Files (for reference)
- `navigation-preview.html` - Initial style options
- `navigation-interactive.html` - Working controls prototype
- `navigation-clean-controls.html` - Refined View/Order separation
- `navigation-full-architecture.html` - Multi-document type exploration
- `navigation-integrated.html` - Final integrated design

## Next Milestone Checkpoint
When Phase 1 is complete, we'll have:
- ✅ New SUMMARY.md format
- ✅ Relationship data structure
- ✅ Clear path for JavaScript implementation

---
Last updated: August 26, 2025, 2:45 PM