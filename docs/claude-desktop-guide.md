# Claude Desktop Workflow - Document Processing & Airtable

## Overview

This guide covers the Claude Desktop workflow for processing City of Rivergrove documents, including OCR, transcription, and Airtable updates.

- **Repository**: [GitHub](https://github.com/wifelette/city_of_rivergrove)
- **Related Guides**:
  - [Claude Code Guide](claude-code-guide.md) - Repository management
  - [mdBook Guide](mdbook-guide.md) - Site generation and technical details
  - [Airtable Integration](airtable-integration.md) - Technical integration details

## Document Types and Workflows

The digitization process now handles two distinct document types with separate workflows:

### Governing Documents Workflow

- **Document Types**: Ordinances, Resolutions, Interpretations
- **Tables Used**: Documents, Governing, Governing_Metadata
- **Process**: OCR/transcription → Create 3 Airtable records → Upload to GitHub → Update URLs

### Meeting Records Workflow

- **Document Types**: Meeting Agendas, Meeting Minutes
- **Tables Used**: Meetings, Meeting Records, Documents, Meetings_Metadata
- **Process**: Create Meeting record → Create 4 Airtable records → Upload to GitHub → Update URLs

---

## Governing Documents Processing

### 1. OCR and Transcription

- Leah uses Adobe Acrobat for OCR (export as **plain text**, not .docx) and shares with Claude OR has Claude do it directly
- If done via Adobe, Leah uploads source PDF and OCR text output to Claude for final comparison
- Claude creates clean markdown version fixing OCR errors
- Claude reviews for legal terms, dates, and signatures, but doesn't make any changes without explicit approval by Leah, not even fixing typos. We're strictly digitizing as is.
- **Claude searches existing Airtable entries first** before creating new ones
- Claude creates or updates three entries in the Airtable MCP base:
  - 1. **Documents** record for file storage
  - 2. **Governing** record for the ordinance/resolution/interpretation
  - 3. **Governing_Metadata** record for website publication (with Publication Status: Draft)
- Leah saves artifact with established naming conventions
- Leah uploads to GitHub and provides URLs to Claude for Airtable updates
- Once GitHub URLs are added:
  - Mark as Digitized in Governing table
  - Change Publication Status from "Draft" to "Published" in Governing_Metadata table

### 2. PDF Page Order Verification

**Critical Step:** Always verify PDF pages are in logical order before transcribing.

**Issue:** Some PDFs have scrambled page order (e.g., signature page in middle, sections out of sequence).

**Process:**

1. Scan through all pages first
2. Identify the proper document flow (title → sections 1,2,3... → signatures)
3. If pages are out of order, mentally reorganize before transcribing
4. Create artifact with correct logical structure, not PDF page order

### 3. Governing Documents Airtable Updates

When processing a governing document:

- **Always search existing entries first** using multiple search terms
- **Search with multiple ID format variations**: When searching for existing entries, try multiple formats of the same ID:
  - `Ordinance #28`, `Ordinance 28`, `#28`, `28`
  - `Resolution #72`, `Resolution 72`, `#72`, `72`
  - Also try key topic words from the title/subject
- **Discover field names before creating/updating**: Use list functions with small limits (3-5 records) to see actual field names and avoid validation errors from incorrect field naming.
  - `daily-tasks:council_documents_list (limit: 3)`
  - `daily-tasks:council_governing_list (limit: 3)`
  - etc.

**Create/update Documents entry:**

- `documentType`: "Governing Doc"
- `tags`: "Ordinance/Resolution/Interpretation" (pass as string, not array!)
- documentDate
- documentTitle
- fileURL (PDF files on GitHub)
- mdURL (Markdown files on GitHub)
- rawURL (auto-populates from mdURL - don't touch)
- description

**Update Governing entry:**

- Link to Documents record
- Summary (dry, objective, searchable)
- Topics (use existing valid options)
- Mark as Digitized when GitHub upload complete

**Create Governing_Metadata entry:**

- Link to Governing record via `governing_docs` field
- Publication Status: "Draft" (initially, then "Published" after GitHub upload)
- Any other relevant metadata fields

---

## Meeting Records Processing

### 1. Meeting Records Digitization Workflow

When digitizing meeting agendas or minutes:

1. **Check for existing Meeting record** - Search by date
2. **Create Meeting record** (if doesn't exist):
   - Set date
   - Set appropriate inventory boolean: `Agenda?: true` for agendas, `Minutes?: true` for minutes
   - Note: Both can be checked if digitizing both document types for the same meeting
3. **Create Meeting Records record**:
   - Link to Meeting record
   - Set Document Type: "Agenda", "Minutes" or "Transcript"
   - Add notes about content/context
4. **Create Documents record**:
   - Use correct `documentType`: "Agendas" for agendas, "Minutes" for minutes, etc.
5. **Create Meetings_Metadata record**:
   - For website publication
   - Status: "Draft" initially
6. **Link all records together**
7. **Create markdown artifact**
8. **Upload to GitHub and update URLs**

### 2. Meeting Records Airtable Updates

**Meetings record:**

- Date (required - see Meeting Time Entry below for proper format)
- Set `Meeting Type` to `Regular` as default, unless I say otherwise; ask if it ought be changed if the contents make you think it wasn't a regular meeting
- Set inventory booleans: `Agenda?: true` for agendas, `Minutes?: true` for minutes, etc.
- Links to Meeting Records record(s)

**Meeting Time Entry:**
- **Default time**: All Rivergrove meetings are scheduled for 7:00 PM unless explicitly stated otherwise
- **Format**: Use `YYYY-MM-DDTHH:MM:00` in Pacific Time (24-hour format)
- **Standard entry**: For a typical meeting on June 12, 2017: `2017-06-12T19:00:00`
- **Important distinction**: 
  - Use 7:00 PM (19:00) as the scheduled meeting time, even if minutes show a different call-to-order time
  - Example: Minutes may say "called to order at 7:03 p.m." but still use `2017-06-12T19:00:00`
  - Only use a different time if the meeting was explicitly scheduled for a different time (e.g., "special meeting at 5:00 PM")
- **Why this matters**: If time is omitted, Airtable may default to noon/midnight depending on timezone settings, causing sorting issues

**Meeting Records record:**

- Link to Meetings record (auto-populates Meeting Date)
- Document Type: "Agenda", "Minutes", etc.
- Notes about content/significance
- Source URL (if from website)
- Set `Digitized` boolean to `Digitized?: true` assuming you've indeed processed the markdown file

**Documents record:**

- `documentType`: "Agendas" for agendas, "Minutes" for minutes, etc.
- `tags`: "Meeting Documentation"
- documentDate (meeting date)
- documentTitle following naming convention
- Link to Meeting Records record

**Meetings_Metadata record:**

- Link to Meeting Records record via `meeting_docs` field
- Status: "Draft" initially, "Published" after GitHub upload
- Short title for navigation
- Tags for meeting content (only if substantive topics evident—things like a regular Planning Commission update don't need to be noted since they happen most meetings)

---

## Content Standards

- **No editorializing**: Keep summaries factual and objective
- **Preserve all metadata**: Stamps, signatures, dates, handwritten notes
- **Focus on rote work over content analysis** - Leah doesn't need detailed summaries unless requested
- **Markdown formatting**: Use headers, lists, and clear structure
- **Cross-references**: Keep document references as plain text (e.g., "Ordinance #52", "Resolution #22")
  - NEVER add manual markdown links for cross-references
  - The build system automatically converts these to clickable links
  - See `docs/markdown-conventions.md` for patterns that are detected

### Signature Section Formatting

See **[styles/signature-formatting.md](styles/signature-formatting.md)** for complete signature block formatting standards.

**Key Points:**

- Use `[Signature], Name, Title` format (all on one line)
- Add double spaces at end of lines for proper breaks
- Use `{{filled:}}` for handwritten dates
- Preserve exact date formats from source

### Page Break Handling

- **Ignore page breaks**: Transcribe documents continuously without page markers
- **No page numbers needed**: Don't add "Page 1", "---", or similar markers
- **Single flowing document**: Present the entire ordinance as one continuous markdown file
- **Exception**: Only note page breaks if they are for some reason meaningful (like when legal documents say "Continue on next page" or "this section intentionally left blank")

### Handwritten Content and Form Fields

See **[styles/form-fields.md](styles/form-fields.md)** for complete guide on handling blank and filled fields.

**Key Points**:

- Use `{{filled:}}` for blank fields in source documents
- Use `{{filled:text}}` for handwritten/filled content
- Always use `{{filled:}}` for handwritten dates in signature blocks
- Underlined text: Convert to bold (we don't use underlines except for form fields)

### Images and Diagrams

See **[styles/inline-images.md](styles/inline-images.md)** for handling images, diagrams, and visual content.

**Key Points**:

- Use `{{image:filename.png|caption=Description|alt=Alt text}}` syntax
- Images should be stored in `images/[document-type]/` at the repository root (not in `src/` which is gitignored)
- Screenshots and diagrams should be saved as PNG files
- If an image or complex table is found and would be useful to include, point it out to Leah so she can extract it (or do it for her) and save it where it needs to go

## Document Title Standards

All documentTitle fields in Airtable follow standardized formats:

**Governing Documents:**

- **Interpretations**: "PC Interpretation - [Topic]"
  - Example: "PC Interpretation - Section 5.080 Setbacks"
- **Ordinances**: "Ordinance #XX - [Topic]" (convert roman numerals to standard numbers)
  - Example: "Ordinance #16 - Establishing a Park Advisory Council"
  - Use full Ordinance number if there is a second part, like "Ordinance 20-1997"
- **Resolutions**: "Resolution #XX - [Topic]"
  - Example: "Resolution #22 - Planning Commission CCI"

**Meeting Documents:**

- **Agendas**: "[Month DD, YYYY] Council Meeting Agenda"
  - Example: "May 14, 2018 Council Meeting Agenda"
- **Minutes**: "[Month DD, YYYY] Council Meeting Minutes"
  - Example: "May 14, 2018 Council Meeting Minutes"

When processing documents, always check existing titles and update them to match these standards if needed.

## Quality Control & Best Practices

### Post-Digitization Verification

**For Governing Documents:**

- [ ] Documents entry has both fileURL and mdURL
- [ ] rawURL auto-populated correctly
- [ ] Governing entry marked as Digitized
- [ ] Governing_Metadata status changed to Published
- [ ] Bidirectional linking verified
- [ ] Amendment relationships preserved
- [ ] Document title follows naming convention
- [ ] Passed date matches signatures/adoption date

**For Meeting Documents:**

- [ ] Meeting record has appropriate inventory boolean checked
- [ ] Meeting Records record properly linked
- [ ] Documents entry has correct documentType ("Agendas" or "Minutes")
- [ ] Meetings_Metadata record linked and published
- [ ] All bidirectional linking verified
- [ ] GitHub URLs updated in appropriate records

### MCP Tool Notes

- **Always search existing entries** before creating new ones
- Use multiple search terms (ID, year, topic keywords)
- **Array fields (tags, linked records)**: Always pass as strings, not arrays - MCP auto-wraps them
  - See `/Users/leahsilber/Github/daily-claude/mcp-server/MCP_USAGE_GUIDE.md` for full details
- **Inform Leah immediately of any field validation failures** for her decision on resolution
- Link documents to governing/meeting records appropriately
- Handle field validation errors gracefully (especially for Topics and tags)
- Include topics for searchability using valid options only

### MCP Function Reference

**Governing Documents:**

- `daily-tasks:council_governing_search/list/create/update`
- `daily-tasks:council_governing_metadata_search/list/create/update`
- `daily-tasks:council_documents_search/list/create/update`

**Meeting Documents:**

- `daily-tasks:council_meetings_list/create` (limited update capabilities)
- `daily-tasks:council_meeting_records_search/list/create/update`
- `daily-tasks:council_meetings_metadata_search/list/create/update`
- `daily-tasks:council_documents_search/list/create/update`

### Key Reminders

- Search existing Airtable entries thoroughly before creating new ones
- **Alert Leah immediately to any field validation failures**
- Use established naming conventions consistently
- Focus on accurate transcription over content analysis
- Preserve all original formatting, dates, and signatures
- Claude should ask for GitHub URLs with correct filenames ready for immediate save
- **For Meeting Documents**: Set appropriate inventory boolean in Meeting records
- **For Agendas**: Use documentType "Agendas", not "Minutes"
- **Tagging**: Only tag meeting documents if substantive topics were discussed, not for routine items
- **Digitization Guide updates**: When Leah asks for text to add to the Digitization Guide, always provide it as inline copyable markdown in code blocks rather than artifacts - this allows single-button copying without downloads.
- **Batch URL Updates**: When updating multiple documents with GitHub URLs, use the systematic approach: list all records first to see field structure, then update fileURL and mdURL fields (rawURL will auto-populate)
