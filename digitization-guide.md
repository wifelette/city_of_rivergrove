# Rivergrove Ordinance Digitization Project - Continuity Guide

## Project Overview

Creating a searchable, centralized repository of all City of Rivergrove ordinances, resolutions, and interpretations. This addresses the current problem where no central listing exists, allowing people to "selectively ignore things or make things up." We have copies of old, hard-to-read photocopied versions, and are working to extract the text as markdown files for saving in Github.

- **Repository**: [GitHub](https://github.com/wifelette/city_of_rivergrove)

## Infrastructure

- **Airtable MCP base** with:
  - Ordinances and Resolutions inventory table (40+ records with varying completeness)
  - Documents table (linked to ordinances)
- **Document storage**: Dropbox links in Airtable
- **Final output**: Markdown files in GitHub repo

## Progress as of August 23, 2025

- **Planning Commission Interpretations**: ✅ **COMPLETE** - All 13 interpretations from 1997-2008 digitized
- **Other completed documents**: City Charter, Resolution 22, Resolution 72, Ordinance #16 (1974)
- **Current focus**: Ordinances from various time periods
- **Tracking**: [GitHub issue #3](https://github.com/wifelette/city_of_rivergrove/issues/3) with comprehensive checklists

---

## Claude Desktop Workflow (Document Processing & Airtable)

### 1. Document Processing

- Leah uses Adobe Acrobat for OCR (export as **plain text**, not .docx) and shares with Claude OR has Claude do it directly
- If done via Adobe, Leah uploads source PDF and OCR text output to Claude for final comparison
- Claude creates clean markdown version fixing OCR errors
- Claude reviews for legal terms, dates, and signatures, but doesn't make any changes without explicit approval by Leah, not even fixing typos. We're strictly digitizing as is.
- **Claude searches existing Airtable entries first** before creating new ones
- Claude creates or updates two entries in the Airtable MCP base:
  - 1 Document record for the file
  - 2 Ordinances and Resolutions record for the file
- Leah saves artifact with established naming conventions
- Leah uploads to GitHub and provides URLs to Claude for Airtable updates
- Mark as Digitized once GitHub URL is added

### 2. Airtable Updates

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
- Create/update Documents entry with:
  - `documentType`: "Governing Doc"
  - `tags`: ["Ordinance/Resolution/Interpretation"] (may have validation issues)
  - documentDate
  - documentTitle
  - Dropbox URL (from Leah)
  - Public URL (from Leah once uploaded to Github)
  - Brief description
- Update `Ordinances and Resolutions` entry with:
  - Link to document
  - Summary (dry, objective, searchable)
  - Topics (use existing valid options)
  - Mark as Digitized when GitHub upload complete

### 3. Content Standards

- **No editorializing**: Keep summaries factual and objective
- **Preserve all metadata**: Stamps, signatures, dates, handwritten notes
- **Focus on rote work over content analysis** - Leah doesn't need detailed summaries unless requested
- **Markdown formatting**: Use headers, lists, and clear structure

### 4. MCP Tool Notes

- **Always search existing entries** before creating new ones
- Use multiple search terms (ID, year, topic keywords)
- **Inform Leah immediately of any field validation failures** for her decision on resolution
- Link documents to ordinance/resolution records
- Handle field validation errors gracefully (especially for Topics and tags)
- Include topics for searchability using valid options only

### 5. Key Reminders

- Search existing Airtable entries thoroughly before creating new ones
- **Alert Leah immediately to any field validation failures**
- Use established naming conventions consistently
- Focus on accurate transcription over content analysis
- Preserve all original formatting, dates, and signatures
- Claude should ask for GitHub URLs with correct filenames ready for immediate save
- **Digitization Guide updates**: When Leah asks for text to add to the Digitization Guide, always provide it as inline copyable markdown in code blocks rather than artifacts - this allows single-button copying without downloads.

---

## Claude Code Workflow (Repository Management)

### 1. File Organization & Naming Conventions

#### Naming Conventions

- **Resolutions**: `YYYY-Res-#XX-Topic` (e.g., `1984-Res-#72-Municipal-Services`)
- **Interpretations**: `YYYY-MM-DD-RE-[section]-[brief topic]`
- **Ordinances**: `YYYY-Ord-#XX-Topic` (e.g., `1974-Ord-#16-Parks`)

#### File Organization

- **Interpretations**: Go in `/Interpretations/` folder (both .md and .pdf files)
- **Ordinances**: Go in `/Ordinances/` folder (both .md and .pdf files)
- **Resolutions**: Go in `/Resolutions/` folder (both .md and .pdf files)
- **Other Documents**: Root level or appropriate subfolder (both .md and .pdf files)

**PDF Storage**: Source PDFs are stored alongside their markdown counterparts using identical naming:
- Example: `1978-Ord-#28-Parks.md` and `1978-Ord-#28-Parks.pdf` in the same folder
- PDFs are only added to GitHub after the markdown file has been created
- Original PDFs remain in Dropbox (renamed to match convention) with copies in GitHub

### 2. When Digitizing Documents

1. **Add PDF**: Copy the source PDF from Dropbox to the same folder as the .md file, using identical naming
2. **Commit and Push**: When new .md and .pdf files are added to the repo, commit with descriptive message and push to GitHub (no Claude attribution needed)
3. **Provide GitHub Links**: After pushing, always provide the GitHub web URLs for Airtable:
   - Markdown: `https://github.com/wifelette/city_of_rivergrove/blob/main/[path]/file.md`
   - PDF: `https://github.com/wifelette/city_of_rivergrove/blob/main/[path]/file.pdf`
4. **Update Issue #3**:
   - Remove item from the "Documents Needing Processing" list
   - Add to "Completed Documents" section at bottom with format: `- [x] Document Name`
   - Include commit link if significant: `([commit-hash](link))`
   - No need to write "Complete" - the checked box is sufficient

### 3. Issue Management

- Keep issue #3 as the single source of truth for digitization progress
- When consolidating repetitive tasks, use "Add to Airtable via Claude Desktop process"
- Bold document names in checklists for visibility: `**Ordinance #XX**`

### 4. Airtable Integration

- Claude Code can potentially update Airtable directly if provided with:
  - Record ID from the Ordinances and Resolutions table
  - The GitHub URL to add to the Public URL field
- Otherwise, provide GitHub web URLs for manual entry

---

## Completed Collections

### ✅ Planning Commission Interpretations

**ALL 13 interpretations from 1997-2008 are complete and digitized.**

## Current Phase: Ordinances and Resolutions

- Working chronologically and by availability
- Using new naming convention for ordinances
- Standard workflow applies