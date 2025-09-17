# Claude Desktop Workflow - Document Processing & Airtable

## Overview

This guide covers the Claude Desktop (CD) workflow for processing City of Rivergrove documents, including OCR, transcription, and Airtable updates.

- **Repository**: [GitHub](https://github.com/wifelette/city_of_rivergrove)

## Document Types and Workflows

The digitization process handles two distinct document types with completely separate workflows:

1. **Governing Documents** (Ordinances, Resolutions, Interpretations, Other)
2. **Meeting Documents** (Agendas, Minutes, Transcripts)

Each has its own complete workflow section below. Follow the appropriate section based on your document type.

---

## Governing Documents Processing

### Step 1: Review and Transcribe the PDF

**First, check page order:**

- Scan through all PDF pages before starting transcription
- Identify if pages are in logical order (title → sections → signatures)
- If scrambled, mentally reorganize - transcribe in correct logical order, not PDF page order
- Common issue: signature pages in middle, sections out of sequence

**Then transcribe:**

- Leah provides either:
  - Adobe Acrobat OCR output (plain text export) + original PDF for comparison
  - OR just the PDF for Claude to OCR directly
- Create clean markdown version fixing OCR errors
- Review for legal terms, dates, signatures
- **Don't change anything without explicit approval** - not even typos (strict digitization as-is)
- Provide suggested filename when confirming digitization (for Leah's save dialog)

### Step 2: Search Existing Airtable Records

**Before creating any new records, always search thoroughly:**

- **Search with multiple ID format variations**: When searching for existing entries, try multiple formats of the same ID:
  - `Ordinance #28`, `Ordinance 28`, `#28`, `28`
  - `Resolution #72`, `Resolution 72`, `#72`, `72`
  - **For year-suffixed documents**: `Ordinance 52-2001`, `52-2001`, `Ordinance 52-01`
    - Some documents use formats like `#XX-YYYY` where the year is part of the official number
    - Try searching with and without the year suffix
    - Also search just the base number (e.g., `52`) to catch variations
  - Also try key topic words from the title/subject
- **List existing records first** to see actual field names:
  - `daily-tasks:council_documents_list (limit: 3)`
  - `daily-tasks:council_governing_list (limit: 3)`
  - This helps avoid field validation errors

### Step 3: Create/Update Airtable Records

**Create three linked records in this order:**

**1. `Documents` entry (for file storage):**

- `documentType`: "Governing Doc"
- `tags`: "Ordinance/Resolution/Interpretation" (pass as string, not array!)
- `documentDate`
- `documentTitle` (you set this - different from `docName` which auto-generates)
- `description`

**2. `Governing` entry (the main record):**

- Link to `Documents` record
- `Summary` (dry, objective, searchable)
- `Topics` (use existing valid options)
- Mark as `Digitized` when GitHub upload complete and those two URLs have been added

**3. `Governing_Metadata` entry (for website publication):**

- Link to `Governing` record via `governing_docs` field
- `status`: "Draft" (initially, then "Published" after GitHub upload)
- `fileURL` (leave blank initially - will be filled after GitHub upload)
- `mdURL` (leave blank initially - will be filled after GitHub upload)
- `rawURL` (auto-populates from `mdURL` - don't set this field)
- Leave `special_state` blank for now (this is typically set on OTHER documents - see Step 5)
- Any other relevant metadata fields

### Step 4: GitHub Upload and Final Updates

**After Leah uploads to GitHub via Claude Code:**

1. Leah will provide two URLs:

   - PDF GitHub URL
   - Markdown GitHub URL

2. Update the `Governing_Metadata` record with both URLs:

   - `fileURL` (PDF URL)
   - `mdURL` (Markdown URL)
   - `rawURL` will auto-populate from `mdURL`

3. Update status fields:
   - Mark `Governing` entry as **Digitized**
   - Change `Governing_Metadata` `status` from "Draft" to **"Published"**

### Step 5: Check for Impacts on Other Documents

**If this document mentions it affects other documents:**

If the document contains language like:

- "This ordinance repeals Ordinance #48"
- "This amends Ordinance #52"
- "This supersedes Resolution #22"

Then:

1. Search for the affected document in Airtable
2. **Ask Leah**: "Should I update the `special_state` field in the `Governing_Metadata` record for [Document #XX] to [Repealed/Amended/Superseded]?"
3. Only update if Leah confirms

**Common phrases to watch for:**

Active voice (this document does something):

- "hereby repeals"
- "amends and restates"
- "supersedes and replaces"
- "modifies"
- "rescinds"

Passive voice (something is done to another document):

- "Ordinance #XX is hereby amended"
- "Ordinance #XX is hereby repealed"
- "Resolution #XX is superseded"
- "Ordinance #XX is rescinded"
- "is modified as follows"

### Document Title Standards - Governing

**Different title fields and their purposes:**

**`documentTitle` in `Documents` table** (you set this manually):

- **Interpretations**: "PC Interpretation - [Topic]"
  - Example: "PC Interpretation - Section 5.080 Setbacks"
- **Ordinances**: "Ordinance #XX - [Topic]" (convert roman numerals to standard numbers)
  - Example: "Ordinance #16 - Establishing a Park Advisory Council"
  - Use full Ordinance number if there is a second part, like "Ordinance 20-1997"
- **Resolutions**: "Resolution #XX - [Topic]"
  - Example: "Resolution #22 - Planning Commission CCI"

**Note**: The `docName` field in `Documents` will auto-generate - don't set it

**Other title fields**:

- `Governing_Metadata` table has a `short_title` for display in the navigation bar - create a succinct version (e.g., "Park Council" instead of "Establishing a Park Advisory Council")

### Quality Control Checklist - Governing

Before marking complete, verify:

- [ ] `Governing_Metadata` has both `fileURL` and `mdURL` (after GitHub upload)
- [ ] `rawURL` auto-populated correctly in `Governing_Metadata`
- [ ] `Governing` entry marked as `Digitized`
- [ ] `Governing_Metadata` status changed to `Published`
- [ ] Bidirectional linking verified
- [ ] Amendment relationships preserved
- [ ] Document title follows naming convention
- [ ] Passed date matches signatures/adoption date

### MCP Functions - Governing

- `daily-tasks:council_governing_search/list/create/update`
- `daily-tasks:council_governing_metadata_search/list/create/update`
- `daily-tasks:council_documents_search/list/create/update`

---

## Meeting Documents Processing

### Step 1: Transcribe the Meeting Document

- Review the agenda, transcript or minutes PDF
- Create clean markdown version
- Follow same transcription rules as Governing docs (preserve as-is, no corrections)
- Provide suggested filename (according to conventions) when confirming digitization

### Step 2: Search/Create Meeting Record

**Search for existing `Meetings` record by date first**

If none exists, create one with:

- `Date` (see Meeting Time Entry format below)
- `Meeting Type`: "Regular" (default) or "Special"/"Work Session" if specified
- Set inventory boolean:
  - `Agenda?: true` for agendas
  - `Minutes?: true` for minutes
  - `Transcript?: true` for transcripts
  - Note: Any or all can be true simultaneously for any docs; this is a log of what's already been processed for this meeting

### Step 3: Create Three Linked Airtable Records

**1. `Documents` record:**

- `documentType`: "Agendas" for agendas, "Minutes" for minutes, "Transcripts" for transcripts
- `tags`: "Meeting Documentation" (as string, not array)
- `documentDate` (meeting date)
- `documentTitle` (you set this - see naming convention below)
- `description` (if relevant)

**2. Update `Meetings` record:**

- Link to `Documents` record
- Mark as `Digitized` once complete
- Verify the appropriate inventory boolean is checked

**3. `Meetings_Metadata` record:**

- Link to `Meetings` record (via `Meetings` field)
- Link to `Documents` record (via `Documents` field)
- `Status`: "Draft" initially
- `fileURL` (leave blank initially - will be filled after GitHub upload)
- `mdURL` (leave blank initially - will be filled after GitHub upload)
- `rawURL` (auto-populates from `mdURL` - don't set this field)
- `short_title` for navigation (e.g., "May 14 Council Meeting" - shorter than full `documentTitle`)
- `Tags` for meeting content (only if substantive topics - not routine items)

**Meeting Time Entry Format:**

- **Default time**: All Rivergrove meetings are scheduled for 7:00 PM unless explicitly stated otherwise
- **Format**: Use `YYYY-MM-DDTHH:MM:00` in Pacific Time (24-hour format)
- **Standard entry**: For a typical meeting on June 12, 2017: `2017-06-12T19:00:00`
- **Important distinction**:
  - Use 7:00 PM (19:00) as the scheduled meeting time, even if minutes show a different call-to-order time
  - Example: Minutes may say "called to order at 7:03 p.m." but still use `2017-06-12T19:00:00`
  - Only use a different time if the meeting was explicitly scheduled for a different time (e.g., "special meeting at 5:00 PM")
- **Why this matters**: If time is omitted, Airtable may default to noon/midnight depending on timezone settings, causing sorting issues

### Step 4: GitHub Upload and Final Updates

**After Leah uploads to GitHub via Claude Code:**

1. Leah will provide two URLs (PDF and Markdown)
2. Update the `Meetings_Metadata` record with both URLs:
   - `fileURL` (PDF URL)
   - `mdURL` (Markdown URL)
   - `rawURL` will auto-populate
3. Update status fields:
   - Change `Meetings_Metadata` `status` from "Draft" to **"Published"**

### Document Title Standards - Meetings

**Different title fields and their purposes:**

**`documentTitle` in `Documents` table** (you set this manually):

- **Agendas**: "[Month DD, YYYY] Council Meeting Agenda"
  - Example: "May 14, 2018 Council Meeting Agenda"
- **Minutes**: "[Month DD, YYYY] Council Meeting Minutes"
  - Example: "May 14, 2018 Council Meeting Minutes"
- **Transcripts**: "[Month DD, YYYY] Council Meeting Transcript"
  - Example: "May 14, 2018 Council Meeting Transcript"

**Note**: The `docName` field in `Documents` will auto-generate - don't set it

**Other title fields** (if present):

- `Meetings_Metadata` table has `short_title` for navigation - use abbreviated version like "May 14 CC Agenda" (for City Council) or "May 20 PC Minutes" (for Planning Commission)

### Quality Control Checklist - Meetings

Before marking complete, verify:

- [ ] `Meetings` record has appropriate inventory boolean checked
- [ ] `Documents` record properly linked to `Meetings`
- [ ] `Documents` entry has correct `documentType` ("Agendas" or "Minutes")
- [ ] `Meetings_Metadata` record linked and published
- [ ] All bidirectional linking verified
- [ ] GitHub URLs (`fileURL` and `mdURL`) updated in `Meetings_Metadata`

### MCP Functions - Meetings

- `daily-tasks:council_meetings_list/create` (limited update capabilities)
- `daily-tasks:council_meeting_records_search/list/create/update`
- `daily-tasks:council_meetings_metadata_search/list/create/update`
- `daily-tasks:council_documents_search/list/create/update`

### Key Reminders - Meetings

- **For Meeting Documents**: Set appropriate inventory boolean in Meeting records
- **Tagging**: Only tag meeting documents if substantive topics were discussed, not for routine items

---

## Content Standards

- **No editorializing**: Keep summaries factual and objective
- **Preserve all metadata**: Stamps, signatures, dates, handwritten notes
- **Focus on rote work over content analysis** - Leah doesn't need summaries unless requested
- **Preserve original content exactly**: Don't fix typos or grammar unless explicitly asked

## Markdown Notation Standards

This section provides comprehensive markdown formatting instructions for digitizing City of Rivergrove documents. Follow these conventions exactly to ensure documents process correctly through the build system.

### Quick Reference

| Element             | Markdown Syntax                              | Example Usage                                           |
| ------------------- | -------------------------------------------- | ------------------------------------------------------- |
| Parenthetical lists | `(a)` at line start (no bullet)              | `(a) First item text here`                              |
| Blank fields        | `{{filled:}}`                                | `Date: {{filled:}}`                                     |
| Filled fields       | `{{filled:text}}`                            | `Date: {{filled:March 15, 2024}}`                       |
| Signatures          | `{{signature}}, Name, Title`                 | `{{signature}}, John Smith, Mayor`                      |
| Cross-references    | Plain text (no manual links)                 | `Ordinance #52` NOT `[Ord #52](...)`                    |
| Table footnotes     | `¹ **Bold.** Text` after table               | `¹ **Note.** See definition...`                         |
| Document notes      | `## Document Notes`<br>`### Type {{page:X}}` | `## Document Notes`<br>`### Stamp {{page:1}}`<br>`COPY` |

### Headers Hierarchy

- **Main title (H1)**: `# ORDINANCE NO. XX-YYYY` or `# An Interpretation of the Planning Commission`
- **Subtitle/description (H2)**: `## AN ORDINANCE...` or `## (May 7, 2001)`
- **Section headers (H3)**: `### Section 1. Title` or `### INTERPRETATION`
- **Subsection headers (H4)**: `#### Subsection A` or `#### (a) Definitions`

### Lists - Critical Formatting

**Parenthetical Lists (Most Common in Legal Documents)**

These lists use (a), (b), (c) or (1), (2), (3) format and require special formatting:

```markdown
(a) First item text here
(b) Second item text here
(c) Third item text here
```

**Important**:

- Start each item at the beginning of the line (no indentation)
- NO bullet markers or dashes before parenthetical items
- The build system will automatically style these with blue markers and no bullets

**Nested Lists**

```markdown
(a) Parent item
(1) Nested numeric item
(2) Second nested numeric item
(i) Double nested roman numeral
(ii) Another double nested roman
(b) Second parent item
```

Use 4-space indentation for each level of nesting.

**Standard Numbered Lists**

```markdown
1. First numbered item
2. Second numbered item
3. Third numbered item
```

**Lists with Continuation Text**

```markdown
(a) First item with a simple sentence.

This is a continuation paragraph under item (a) with more detailed explanation.
Use 3-space indentation to prevent markdown from treating it as a code block.

(b) Second item continues here.
```

**Lists with Introductory Text**

Preserve introductory text before lists:

```markdown
The term does not, however, include either:
(1) any project for improvement of a structure
(2) any alteration of a structure listed on the National Register
```

**Common introductory phrases to preserve:**

- "The following items are included:"
- "This does not include:"
- "Requirements consist of:"
- "The term means:"
- "as follows:"

**Lists in Blockquotes (for quoted sections):**

```markdown
> **Section 1. Definitions**
>
> (a) "Building" means any structure
> (b) "Structure" means anything constructed
> (c) "Use" means the purpose for which land is occupied
```

### Cross-References

**NEVER add manual markdown links**. Keep all references as plain text:

- ✅ Correct: `Ordinance #52`, `Resolution #22`, `Ordinance 70-2001`
- ❌ Wrong: `[Ordinance #52](../ordinances/...)`

The build system automatically converts these patterns to links.

**Patterns that will be auto-linked:**

- Ordinances: `Ordinance #52`, `Ordinance 52`, `Ord. #52`, `Ord. 52`, `Ordinance No. 52`
- With years: `Ordinance #54-89`, `Ordinance 70-2001`
- With letters: `Ordinance #54-89C`
- Resolutions: `Resolution #22`, `Resolution 22`, `Res. #22`, `Res #22`
- Interpretations: References will be linked when they match existing documents

### Signature Blocks

**Standard Format:**

```markdown
{{signature}}, John Smith, Mayor
**Date**: {{filled:10-12-98}}

{{signature}}, Jane Doe, City Recorder
**Date**: {{filled:10/12/98}}
```

(Note: The two spaces at line ends are shown above)

**Key Rules:**

- Names and titles are NOT bolded (just plain text)
- Add TWO SPACES at end of each line (creates proper line break in markdown)
- Use `{{filled:date}}` for handwritten dates
- Preserve exact date format from source (8-12-02 vs 8/12/02 vs August 12, 2002)
- Pre-printed dates: just transcribe normally without `{{filled:}}`

**ATTEST Format:**

```markdown
{{signature}}
John Nelson, Mayor

**ATTEST:**

{{signature}}
Rosalie Morrison, City Recorder
```

**Adoption Statements:**

```markdown
**ADOPTED** by the Rivergrove City Council this {{filled:12}} day of {{filled:June, 1978}}
```

**Reading Dates:**

```markdown
**FIRST READING** {{filled:May 5, 1978}}
**SECOND READING** {{filled:June 12, 1978}}
```

### Form Fields

**Blank fields in source:**

```markdown
Planning File No.: {{filled:}}
Date: {{filled:}}
Applicant: {{filled:}}
```

These render as underlined blank spaces with a tooltip "Blank in source document".

**Handwritten/filled content:**

```markdown
This ordinance was adopted on {{filled:March 15, 2024}}
The fee shall be {{filled:$250.00}}
Signed by {{filled:John Smith}}, Mayor
```

These render with blue highlighting to indicate hand-filled content.

**Common patterns:**

- Blank signature date: `**Date**: {{filled:}}`
- Filled date: `**Date**: {{filled:8-12-02}}`
- Inline blank: `by the City and {{filled:}} (Applicant)`
- Inline filled: `on the {{filled:12th}} day of {{filled:June}}`

**Important:** Always use `{{filled:}}` syntax - never just underscores (`___`) or brackets

### Table Footnotes

**For footnotes below tables:**

```markdown
| Column | Value |
| ------ | ----- |
| Item   | Cost¹ |

¹ **Brief title.** Full explanation text.
² **Second footnote.** Additional explanation.
```

**How to type superscript numbers:**

- Copy/paste these: ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹ ⁰
- Or on Mac: Use Character Viewer (Edit → Emoji & Symbols)
- Or use Unicode: U+00B9 for ¹, U+00B2 for ², U+00B3 for ³

**Format:** Always use pattern `¹ **Bold title.** Regular explanation text.`

Write footnotes immediately after the table. The build system will automatically style them with a gray background and border.

### Document Notes

**For stamps, handwritten text, or digitization notes:**

```markdown
## Document Notes

### Handwritten text {{page:1}}

I certify this to be a true copy. Rosalie Morrison, City Recorder

### Stamp {{page:3}}

COPY

### Digitization note

The source document was in ALL CAPITAL LETTERS. It has been converted to standard capitalization for readability.
```

**Common note types to use as H3 headers:**

- `### Stamp {{page:X}}` - for official stamps
- `### Handwritten text {{page:X}}` - for handwritten additions
- `### Handwritten notation {{page:X}}` - for marginal notes
- `### Digitization note` - for notes about the digitization process
- `### Source document note` - for peculiarities in the original

Always use H3 headers for different note types. The `{{page:X}}` notation is optional but helpful.

### Special Text Formatting

- **Underlined text**: Convert to bold (markdown doesn't support underlines)
- **Strikethrough**: Preserve using `~~text~~` when it appears in legal documents
- **ALL CAPS**: Ask Leah before converting - she'll decide case-by-case. If converted, add a Digitization note
- **Handwritten additions**: Use `{{filled:text}}` for handwritten content
- **Blank lines/spaces**: Use `{{filled:}}` for blank form fields
- **Checkboxes**: Use `☐` for empty boxes, `☑` for checked boxes
- **Line breaks in signatures**: Add two spaces at the end of lines

### Page Breaks

- Generally ignore page breaks - transcribe continuously
- Don't add page markers like "Page 1", "---", or page numbers
- Only note if legally meaningful (e.g., "Continue on next page")

### Tables in Documents

```markdown
| **Column Header** | **Column Header** |
| ----------------- | ----------------- |
| Content           | Content           |
```

- Bold column headers
- Use pipes for alignment
- For complex tables with merged cells, preserve structure as much as possible
- Use `{{br}}` for line breaks within cells if needed

### Images and Diagrams

If you encounter images, diagrams, or complex visual content:

- Note their location and description
- Use placeholder: `{{image:filename.png|caption=Description|alt=Alt text}}`
- Alert Leah that an image needs to be extracted, or that you've extracted it for her if capable

### Complete Example

Here's how a typical ordinance section should be formatted:

```markdown
# ORDINANCE NO. 52

## AN ORDINANCE ADOPTING FLOOD DAMAGE PREVENTION REGULATIONS

### Section 1. Purpose

The purpose of this ordinance is to promote public health, safety, and general welfare.

### Section 2. Definitions

(a) **Flood** or **flooding** means a general and temporary condition of partial or complete inundation

(b) **Structure** means a walled and roofed building that is principally above ground

### Section 3. Requirements

The following requirements shall apply:
(1) All new construction shall be anchored
(2) All new construction shall be constructed with materials resistant to flood damage

{{signature}}, Mark Johnson, Mayor
**Date**: {{filled:3-12-98}}

{{signature}}, Rosalie Morrison, City Recorder
**Date**: {{filled:3/12/98}}

## Document Notes

### Stamp {{page:1}}

COPY

### Handwritten text {{page:2}}

Planning File No.: {{filled:CD-98-12}}
```

_Note: The example above shows `## Document Notes` used within the document_

### Key Reminders for Digitization

1. **Never add HTML or manual markdown links** - the build system handles all linking
2. **Preserve exact formatting** from source documents (dates, capitalization, etc.)
3. **Use parenthetical list format** exactly as shown - no bullets or dashes
4. **Apply {{filled:}} syntax** consistently for all blank and handwritten fields
5. **Follow the header hierarchy** strictly for proper document structure
6. **Include two spaces at line ends** for signatures and other line breaks
7. **Document all stamps and handwritten notes** in the Document Notes section

---

## Common MCP Tool Notes

- **Always search existing entries** before creating new ones
- Use multiple search terms (ID, year, topic keywords)
- **Inform Leah immediately of any field validation failures** for her decision on resolution
- Link documents to governing/meeting records appropriately
- Handle field validation errors gracefully (especially for Topics and tags)
- Include topics for searchability using valid options only

### Critical: Array Field Handling

**For array-type fields (tags, linked records, multi-select), always pass as strings - MCP auto-wraps them:**

✅ **Correct**:
- Single value: `tags: "Ordinance"`
- Multiple values: `tags: "Budget,Planning,Public Safety"`
- With slashes: `tags: "Ordinance/Resolution/Interpretation"`
- Linked record: `governing_docs: "recXYZ123"`

❌ **Wrong**:
- Pre-wrapped array: `tags: ["Ordinance"]` (will be double-wrapped!)
- Stringified array: `tags: '["Budget", "Planning"]'` (treated as literal string!)

The MCP server automatically detects array-type fields and wraps string values appropriately

### General Workflow Reminders

- Search existing Airtable entries thoroughly before creating new ones
- Use established naming conventions consistently
- Focus on accurate transcription over content analysis
- Preserve all original formatting, dates, and signatures
- Provide correct filename when confirming digitization (for Leah's save dialog)
- **Digitization Guide updates**: When Leah asks for text to add to the Digitization Guide, always provide it as inline copyable markdown in code blocks rather than artifacts
- **Batch URL Updates**: When updating multiple documents with GitHub URLs, use the systematic approach: list all records first to see field structure, then update `fileURL` and `mdURL` fields in the metadata tables (`rawURL` will auto-populate)
