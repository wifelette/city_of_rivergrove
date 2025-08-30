# Stub Documents Pattern

## Overview

Stub documents are created for ordinances, resolutions or other official documents that fall into one of two categories. These documents are important to track to prevent confusion when references to them appear in other documents.

## Two Types of Stub Documents

### Type 1: Never Passed Documents
Documents that were referenced or assigned numbers but **never actually passed** or **never existed**.

### Type 2: Missing Original Documents  
Documents that were **passed and enacted** but the **original document is missing** from city records. These may have been superseded, repealed, or remain in effect, but the original text is not available.

## When to Create a Stub

Create a stub document when:

**Type 1 (Never Passed):**
- A document number was assigned but the document was never passed
- Other documents reference this non-existent document
- There's institutional knowledge that the document was planned but never enacted
- Council records show discussion but no passage

**Type 2 (Missing Original):**
- A document was officially passed and enacted
- The original document text is missing from city records
- Other documents reference this enacted document
- The document may have been superseded, repealed, or still be in effect

## File Naming Convention

Stub documents follow the same naming convention as regular documents:

- Example: `2000-Ord-#69-2000-Title-3-Compliance.md`
- No special suffix is needed - stubs are identified by the `Stub?` field in Airtable

## Markdown Templates

### Type 1: Never Passed Template

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

### Type 2: Missing Original Template

```markdown
# [DOCUMENT TYPE] #[NUMBER] - [TITLE IF KNOWN]

## ⚠️ **DOCUMENT MISSING - ORIGINAL LOST**

### Status: [Current Status - Superseded/Repealed/In Effect]

This [document type] was **passed on [DATE]** but was later **[superseded by/repealed by/remains in effect]** [additional details].

### Referenced In Other Documents

[Document type] #[Number] is referenced in **[Other Document]** (passed [date]), which states:

> "[Quote the reference]"

### What This [Document Type] Addressed

Based on the [superseding/referencing] [document type], this [document type] established [description]:

- [Key provisions based on references]
- [Other known content]

### Status: Document Missing

- **Original [document type] was passed** on [date]
- **No copy exists** in current city records
- **[Superseded completely/Repealed/Still in effect but missing]** [additional context]
- **Content [replaced/abolished/unknown]** [by what]

### Research Notes

- **Date used**: [Explain source of date]
- **Source of [supersession/repeal/reference]**: [Reference to other document]
- **Legal status**: [Current legal status]

This document file is created to acknowledge that [Document Type] #[Number] existed and was legally enacted, but the original document is missing from city records [and additional context about current status].
```

## Date Convention for Stubs

### Type 1 (Never Passed)
Since these documents were never passed, they lack official adoption dates. Use this convention:

- **Primary date**: Use the **last date the document was officially referenced** (in minutes, other ordinances, etc.)
- **If only month/year known**: Default to the **1st of the month** (e.g., "09-2020" becomes "09-01-2020")
- **If no references found**: Use the date the number was assigned or first mentioned
- **Document this date source** in the Research Notes section

### Type 2 (Missing Original)
These documents have official passage dates. Use the actual passage date:

- **Primary date**: Use the **official passage/adoption date** from records
- **Source**: Council minutes, superseding documents, or other official references
- **Document this date source** in the Research Notes section

### Examples:
- - **Type 1**: Resolution #265-2019: Last referenced 10-2020 → Date: 10-01-2020
- **Type 1**: Ordinance #69-2000: Referenced in Ord #68-2000 (10-16-2000) → Date: 10-16-2000  
- **Type 2**: Resolution #256-2018: Passed June 11, 2018 (from Resolution #259-2018) → Date: 06-11-2018

## Airtable Handling

For stub documents in Airtable:

### Public Metadata Table

**Type 1 (Never Passed):**
- **Status**: "Published"
- **special_state**: "Never Passed"
- **passed_date**: Last reference date (following convention above)
- **mdURL**: Link to the stub .md file
- **fileURL**: Leave empty if no PDF exists

**Type 2 (Missing Original):**
- **Status**: "Published"  
- **special_state**: Current legal status ("Superseded", "Repealed", or leave empty if still in effect)
- **passed_date**: Official passage date
- **mdURL**: Link to the stub .md file
- **fileURL**: Leave empty (original PDF is missing)

### Ordinances/Resolutions Table

**Type 1 (Never Passed):**
- **Digitized**: Mark as true (the stub is the digitization)
- **Summary**: "Never passed. Referenced but not enacted."
- **Notes**: Explain why stub exists

**Type 2 (Missing Original):**
- **Digitized**: Mark as true (the stub is the digitization)
- **Summary**: "Passed [date]. Original document missing from records. [Superseded by/Repealed by/Status]."
- **Notes**: Explain missing original and current legal status

### Documents Table

**Not needed for stubs** - Since there's no PDF file, skip creating a Documents entry. The Public Metadata and Ordinances/Resolutions entries are sufficient.

### Stub Identification

**Use the `Stub?` boolean field in Airtable's Public Metadata table** to identify stub documents. This field should be set to `true` for all stub documents (both Type 1 and Type 2).

## Examples

**Type 1 (Never Passed):**
- **Ordinance #69-2000**: Referenced in Ord #68-2000 but never passed (Title 3 compliance)
- **Resolution #265-2019**: Number assigned but never enacted

**Type 2 (Missing Original):**
- **Resolution #256-2018**: Passed June 11, 2018, superseded by Resolution #259-2018, original document missing from records

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

The stub warning headers ensure readers immediately understand the document's status:
- ⚠️ **STUB - THIS [DOCUMENT TYPE] WAS NEVER PASSED** - for Type 1 (never passed)
- ⚠️ **DOCUMENT MISSING - ORIGINAL LOST** - for Type 2 (passed but missing)
