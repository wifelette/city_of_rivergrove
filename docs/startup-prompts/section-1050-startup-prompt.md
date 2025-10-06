# Startup Prompt for Resuming Section 1.050 Fix

When you resume, use this prompt:

---

I need to continue fixing the Section 1.050 list fragmentation issue in the City of Rivergrove repository.

## Current Status
- Working on Issue #32 (list formatting problems)
- The nested definitions for items (i) "Lot" and (w) "Street" are FIXED and working
- BUT: The entire Section 1.050 definitions list is fragmenting into multiple lists

## The Problem
In `book/ordinances/1989-Ord-54-89C-Land-Development.html`, Section 1.050 Definitions should be ONE continuous list with items (a) through (y). Instead, we have:
- List 1: Contains items (a)-(v) PLUS content from Article 2 mixed in
- List 2: Contains ONLY item (w) with its nested street definitions
- Items (x) and (y) are somewhere in the mess

## Quick Diagnosis
Run this to see the current state:
```bash
python3 /tmp/section_1050_diagnosis.py
```

## Key Files
- Processor: `scripts/postprocessing/unified-list-processor.py`
- Source: `src/ordinances/1989-Ord-54-89C-Land-Development.md`
- Output: `book/ordinances/1989-Ord-54-89C-Land-Development.html`

## What We Know
1. mdBook converts all definition items to `<p>` tags, not list items
2. Our processor's `convert_consecutive_paragraph_lists` function tries to fix this
3. The special Section 1.050 handler (line ~410) is collecting only 23-24 items instead of 25
4. Item (w) ends up in a separate list because it has nested items
5. Content from Article 2 (starting with "(a) Except as provided...") gets mixed into the definitions

## Next Steps
We need to either:
1. Fix the special handler to collect ALL 25 definitions and stop before Article 2
2. Add logic to merge the fragmented lists after creation
3. Preprocess the markdown to help mdBook generate better initial HTML

The diagnosis document at `/tmp/section_1050_diagnosis.md` has more details and test commands.

---