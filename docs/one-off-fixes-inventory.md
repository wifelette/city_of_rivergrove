# One-Off Fixes Inventory

**Purpose:** Track document-specific processors and special-case handling that don't fit general patterns.

**Philosophy:** Some documents are unique enough that bending the entire system around them creates more problems than it solves. When a pattern appears in only 1-2 documents and would require complex universal logic, a targeted fix is often the better choice.

---

## Active One-Off Processors

### 1. Ordinance #54-89 Land Development (`fix-ord54-specific.py`)

**Created:** January 2025
**Reason:** Structural outlier in every metric

**Unique Characteristics:**
- **Size:** 1,074 lines (3x larger than next largest document)
- **ALL CAPS headers:** `(a) DEFINITIONS:` pattern appears ONLY in this document
- **Rare numbering format:** Uses `1)` style that appears in only 5 places across entire codebase
- **Complex nesting:** Deep hierarchical structure with mixed list types
- **Test failures:** 10+ unique failures vs 0-2 for typical documents

**Specific Issues Fixed:**
1. ALL CAPS section headers not being converted to proper lists
2. Concatenated numeric items under alpha headers (12 instances)
3. Orphaned continuation paragraphs (4 instances)
4. Special nesting patterns in Sections 5.100, 5.120

**Alternative Considered:** Universal processor enhancements
**Why Rejected:** Would add complexity to handle 1 document, risk breaking 20+ others

**Testing:** Run `python3 scripts/tests/test-list-formatting.py` and verify Ord #54-89 specific tests pass

**Maintenance Notes:**
- If Ord #54 is ever amended again, verify this processor still works
- If another document adopts similar structure (unlikely), consider extracting common patterns

---

## Guidelines for Adding One-Offs

**When to create a document-specific processor:**
- Pattern appears in 1-2 documents only
- Universal fix would require complex conditional logic
- Document is structurally unique (like Ord #54's size/complexity)
- Risk to other documents outweighs benefit

**When NOT to create one-off:**
- Pattern appears in 3+ documents (make universal)
- Simple fix can be applied broadly without risk
- Pattern might become more common over time

**Process:**
1. Document decision in this file
2. Create processor: `scripts/postprocessing/fix-[identifier]-specific.py`
3. Add to build pipeline with clear comments
4. Add specific tests in test suite
5. Reference in relevant issue/PR

---

### 2. Ordinance #65-99 Sewer Services (`fix_ord_65_list_break` in enhanced-custom-processor.py)

**Created:** October 2025
**Reason:** Markdown list continuation quirk with nested alpha lists

**Unique Characteristics:**
- Section 2 has three subsections: A, B, C (treated as paragraph headers)
- Section B.3 contains nested lowercase alpha items (a, b)
- Markdown interprets **C.** as list continuation after nested `a.` and `b.`
- Only appears in this specific structural pattern

**Specific Issue Fixed:**
Bold paragraph **C. The parties agree:** was rendering as list item "c" continuing from nested "a, b" list

**Solution:**
- Post-process HTML to extract `<p><strong>C. The parties agree:</strong></p>` from any parent list
- Insert it immediately after the list as standalone paragraph

**Alternative Considered:** Add HTML `<div></div>` as list breaker in markdown
**Why Rejected:** Project policy prohibits HTML in markdown source files

**Testing:** View Ord 65-99 Section 2 and verify C appears as paragraph header, not list continuation

**Maintenance Notes:**
- If similar A/B/C subsection pattern appears with nested a/b lists, may need to generalize
- Currently document-specific to avoid false positives

---

## Deprecated One-Offs

*None yet*

---

## Future Considerations

**Watch for patterns that might become common:**
- If 3+ documents adopt Ord #54-style structure, extract to universal processor
- If amendments to Ord #54 create similar documents, reconsider approach

**Regular Review:**
- Review this list quarterly
- Look for patterns that have become more common
- Refactor one-offs into universal fixes when appropriate
