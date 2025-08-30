# Claude Desktop Workflow - Document Processing & Airtable

## Overview

This guide covers the Claude Desktop workflow for processing City of Rivergrove documents, including OCR, transcription, and Airtable updates.

- **Repository**: [GitHub](https://github.com/wifelette/city_of_rivergrove)
- **Related Guides**: 
  - [Claude Code Guide](claude-code-guide.md) - Repository management
  - [mdBook Guide](mdbook-guide.md) - Site generation and technical details
  - [Airtable Integration](airtable-integration.md) - Technical integration details

## Document Processing

### 1. OCR and Transcription

- Leah uses Adobe Acrobat for OCR (export as **plain text**, not .docx) and shares with Claude OR has Claude do it directly
- If done via Adobe, Leah uploads source PDF and OCR text output to Claude for final comparison
- Claude creates clean markdown version fixing OCR errors
- Claude reviews for legal terms, dates, and signatures, but doesn't make any changes without explicit approval by Leah, not even fixing typos. We're strictly digitizing as is.
- **Claude searches existing Airtable entries first** before creating new ones
- Claude creates or updates three entries in the Airtable MCP base:
  - 1. **Document** record for the file
  - 2. **Ordinances and Resolutions** record for the file
  - 3. **Public Metadata** record linked to the Ordinance/Resolution (with Publication Status: Draft)
- Leah saves artifact with established naming conventions
- Leah uploads to GitHub and provides URLs to Claude for Airtable updates
- Once GitHub URLs are added:
  - Mark as Digitized in Ordinances and Resolutions table
  - Change Publication Status from "Draft" to "Published" in Public Metadata table

### 2. PDF Page Order Verification

**Critical Step:** Always verify PDF pages are in logical order before transcribing.

**Issue:** Some PDFs have scrambled page order (e.g., signature page in middle, sections out of sequence).

**Process:**

1. Scan through all pages first
2. Identify the proper document flow (title → sections 1,2,3... → signatures)
3. If pages are out of order, mentally reorganize before transcribing
4. Create artifact with correct logical structure, not PDF page order

## Airtable Updates

When processing a document:

- **Always search existing entries first** using multiple search terms
- **Search with multiple ID format variations**: When searching for existing entries, try multiple formats of the same ID:
  - `Ordinance #28`, `Ordinance 28`, `#28`, `28`
  - `Resolution #72`, `Resolution 72`, `#72`, `72`
  - Also try key topic words from the title/subject
- **Discover field names before creating/updating**: Use list functions with small limits (3-5 records) to see actual field names and avoid validation errors from incorrect field naming.
  - `daily-tasks:council_documents_list (limit: 3)`
  - `daily-tasks:council_ordinances_list (limit: 3)`
  - etc.
- **Field validation failures**: If any specific field fails validation, inform Leah immediately so she can decide whether to resolve or ignore
- **IMPORTANT - Array Fields**: For tags and linked record fields, pass values as simple strings, NOT arrays:
  - ✅ CORRECT: `tags: "Ordinance/Resolution/Interpretation"`
  - ❌ WRONG: `tags: ["Ordinance/Resolution/Interpretation"]` (will be double-wrapped!)
  - The MCP server auto-wraps string values in arrays for these fields
- Create/update Documents entry with:
  - `documentType`: "Governing Doc"
  - `tags`: "Ordinance/Resolution/Interpretation" (pass as string, not array!)
  - documentDate
  - documentTitle
  - fileURL (PDF files on GitHub)
  - mdURL (Markdown files on GitHub)
  - rawURL (auto-populates from mdURL - don't touch)
  - ytURL (YouTube video URLs, when applicable)
  - description
- Update `Ordinances and Resolutions` entry with:
  - Link to document
  - Summary (dry, objective, searchable)
  - Topics (use existing valid options)
  - Mark as Digitized when GitHub upload complete
- Create `Public Metadata` entry with:
  - Link to Ordinance/Resolution record
  - Publication Status: "Draft" (initially, then "Published" after GitHub upload)
  - Any other relevant metadata fields

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

See **[../styles/signature-formatting.md](../styles/signature-formatting.md)** for complete signature block formatting standards.

**Key Points:**

- Use `[Signature], Name, Title` format (all on one line)
- Add double spaces at end of lines for proper breaks
- Use `{{filled:}}` for handwritten dates
- Preserve exact date formats from source
- Run `scripts/preprocessing/fix-signatures.py` to standardize automatically

### Page Break Handling

- **Ignore page breaks**: Transcribe documents continuously without page markers
- **No page numbers needed**: Don't add "Page 1", "---", or similar markers
- **Single flowing document**: Present the entire ordinance as one continuous markdown file
- **Exception**: Only note page breaks if they are for some reason meaningful (like when legal documents say "Continue on next page" or "this section intentionally left blank")

### Handwritten Content and Form Fields

See **[../styles/form-fields.md](../styles/form-fields.md)** for complete guide on handling blank and filled fields.

**Key Points**:

- Use `{{filled:}}` for blank fields in source documents
- Use `{{filled:text}}` for handwritten/filled content
- Always use `{{filled:}}` for handwritten dates in signature blocks
- Underlined text: Convert to bold (we don't use underlines except for form fields)

### Images and Diagrams

See **[../styles/inline-images.md](../styles/inline-images.md)** for handling images, diagrams, and visual content.

**Key Points**:

- Use `{{image:filename.png|caption=Description|alt=Alt text}}` syntax
- Images are stored in `book/images/[document-type]/`
- Screenshots and diagrams should be saved as PNG files

## Document Title Standards

All documentTitle fields in Airtable follow standardized formats:

- **Interpretations**: "PC Interpretation - [Topic]"
  - Example: "PC Interpretation - Section 5.080 Setbacks"
- **Ordinances**: "Ordinance #XX - [Topic]" (convert roman numerals to standard numbers)
  - Example: "Ordinance #16 - Establishing a Park Advisory Council"
  - Use full Ordinance number if there is a second part, like "Ordinance 20-1997"
- **Resolutions**: "Resolution #XX - [Topic]"
  - Example: "Resolution #22 - Planning Commission CCI"

When processing documents, always check existing titles and update them to match these standards if needed.

## Quality Control & Best Practices

### Post-Digitization Verification

After completing GitHub upload and URL updates:

- [ ] Documents entry has both fileURL and mdURL
- [ ] rawURL auto-populated correctly
- [ ] Ordinances entry marked as Digitized
- [ ] Public Metadata status changed to Published
- [ ] Bidirectional linking verified
- [ ] Amendment relationships preserved
- [ ] Document title follows naming convention
- [ ] Passed date matches signatures/adoption date

### MCP Tool Notes

- **Always search existing entries** before creating new ones
- Use multiple search terms (ID, year, topic keywords)
- **Array fields (tags, linked records)**: Always pass as strings, not arrays - MCP auto-wraps them
  - See `/Users/leahsilber/Github/daily-claude/mcp-server/MCP_USAGE_GUIDE.md` for full details
- **Inform Leah immediately of any field validation failures** for her decision on resolution
- Link documents to ordinance/resolution records
- Handle field validation errors gracefully (especially for Topics and tags)
- Include topics for searchability using valid options only

### Key Reminders

- Search existing Airtable entries thoroughly before creating new ones
- **Alert Leah immediately to any field validation failures**
- Use established naming conventions consistently
- Focus on accurate transcription over content analysis
- Preserve all original formatting, dates, and signatures
- Claude should ask for GitHub URLs with correct filenames ready for immediate save
- **Digitization Guide updates**: When Leah asks for text to add to the Digitization Guide, always provide it as inline copyable markdown in code blocks rather than artifacts - this allows single-button copying without downloads.
- **Batch URL Updates**: When updating multiple documents with GitHub URLs, use the systematic approach: list all records first to see field structure, then update fileURL and mdURL fields (rawURL will auto-populate)