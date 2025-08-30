# Stub Documents Pattern

## Overview

Stub documents are created for ordinances, resolutions or other official documents that were referenced or assigned numbers but **never actually passed**. These documents are important to track to prevent confusion when references to them appear in other documents.

## When to Create a Stub

Create a stub document when:

- A document number was assigned but the document was never passed
- Other documents reference this non-existent document
- There's institutional knowledge that the document was planned but never enacted
- Council records show discussion but no passage

## File Naming Convention

Add `-STUB` suffix to the filename:

- Regular: `2000-Ord-#68-2000-Metro-Compliance.md`
- Stub: `2000-Ord-#69-2000-Title-3-Compliance-STUB.md`

## Markdown Template

```markdown
# [DOCUMENT TYPE] #[NUMBER] - [TITLE IF KNOWN]

## ⚠️ **STUB - THIS [DOCUMENT TYPE] WAS NEVER PASSED**

### Referenced But Not Enacted

[Explain where this document is referenced and quote the reference if available]

### What This [Document Type] Was Intended to Address

[Based on references or records, explain the intended purpose]

### Status: Never Enacted

- **No draft copy exists** in city records
- **No evidence of passage** in council minutes or [document type] records
- **No subsequent references** found in other city documents
- **[Subject matter]** may or may not have been addressed through other means

### Research Notes

- **Date used**: [Explain why this date was chosen - last reference, assignment date, etc.]
- **Source of information**: [Meeting minutes, other ordinances, etc.]

This stub file is created to document the institutional knowledge that [Document Type] #[Number] was referenced but never actually passed, preventing confusion for future researchers who may encounter the reference in [source].
```

## Date Convention for Stubs

Since stub documents were never passed, they lack official adoption dates. Use this convention:

- **Primary date**: Use the **last date the document was officially referenced** (in minutes, other ordinances, etc.)
- **If only month/year known**: Default to the **1st of the month** (e.g., "09-2020" becomes "09-01-2020")
- **If no references found**: Use the date the number was assigned or first mentioned
- **Document this date source** in the Research Notes section

### Examples:
- Resolution #265-2019: Last referenced 10-2020 → Date: 10-01-2020
- Ordinance #69-2000: Referenced in Ord #68-2000 (10-16-2000) → Date: 10-16-2000

## Airtable Handling

For stub documents in Airtable:

### Public Metadata Table

- **Status**: "Published"
- **special_state**: "Never Passed"
- **passed_date**: Last reference date (following convention above)
- **mdURL**: Link to the stub .md file
- **fileURL**: Leave empty if no PDF exists

### Ordinances/Resolutions Table

- **Digitized**: Mark as true (the stub is the digitization)
- **Summary**: "Never passed. Referenced but not enacted."
- **Notes**: Explain why stub exists

### Documents Table

**Not needed for stubs** - Since there's no PDF file, skip creating a Documents entry. The Public Metadata and Ordinances/Resolutions entries are sufficient.

## Examples

- **Ordinance #69-2000**: Referenced in Ord #68-2000 but never passed (Title 3 compliance)
- **Resolution #265-2019**: Number assigned but never enacted

## When NOT to Create Stubs

Do not create stub documents for:
- Documents that were passed but later repealed (create the actual document)
- Working drafts that never got numbers (no official reference exists)
- Documents you simply can't find (may exist but be missing from records)
- Informal references without assigned numbers
- Documents where you're unsure if they passed (research further first)

## Navigation and Display

- Stubs appear in normal document lists with "(Never Passed)" indicators
- They sort chronologically by their reference date using the date convention
- The ⚠️ **STUB** header ensures immediate recognition
- Cross-references to stubs work normally but lead to explanation pages
- Special state "Never Passed" can be used to filter or highlight stubs

## Visual Indicators

The stub warning header (⚠️ **STUB**) ensures readers immediately understand this document never became law.
