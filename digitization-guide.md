# Rivergrove Ordinance Digitization Project - Continuity Guide

## Project Overview

Creating a searchable, centralized repository of all City of Rivergrove ordinances, resolutions, and interpretations. This addresses the current problem where no central listing exists, allowing people to "selectively ignore things or make things up." We have copies of old, hard-to-read photocopied versions, and are working to extract the text as markdown files for saving in Github.

- **Repository**: [GitHub](https://github.com/wifelette/city_of_rivergrove)

## Infrastructure

- **Airtable MCP base** with:
  - Ordinances and Resolutions inventory table (40+ records with varying completeness)
  - Documents table (linked to ordinances)
- **Document storage**: GitHub URLs in Airtable (fileURL for PDFs, mdURL for Markdown)
- **Final output**: Markdown files in GitHub repo

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

#### 1.1 PDF Page Order Verification

**Critical Step:** Always verify PDF pages are in logical order before transcribing.

**Issue:** Some PDFs have scrambled page order (e.g., signature page in middle, sections out of sequence).

**Process:**

1. Scan through all pages first
2. Identify the proper document flow (title → sections 1,2,3... → signatures)
3. If pages are out of order, mentally reorganize before transcribing
4. Create artifact with correct logical structure, not PDF page order

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

### 3. Content Standards

- **No editorializing**: Keep summaries factual and objective
- **Preserve all metadata**: Stamps, signatures, dates, handwritten notes
- **Focus on rote work over content analysis** - Leah doesn't need detailed summaries unless requested
- **Markdown formatting**: Use headers, lists, and clear structure

#### 3.1 Signature Section Formatting

Standardized format for ordinance signatures:

```markdown
[Signature], [Name], [Title]
**Date**: [Date as written]

[Signature], [Name], [Title]
**Date**: [Date as written]
```

**Important notes:**

- Transcribe dates exactly as written (e.g., "8-12-02" vs "8/12/02")
- Different signers may use different date formats - preserve these differences
- Use "[Signature]" placeholder for actual signatures

#### 3.2 Page Break Handling

- **Ignore page breaks**: Transcribe documents continuously without page markers
- **No page numbers needed**: Don't add "Page 1", "---", or similar markers
- **Single flowing document**: Present the entire ordinance as one continuous markdown file
- **Exception**: Only note page breaks if they are for some reason meaningful (like when legal documents say "Continue on next page" or "this section intentionally left blank")

#### 3.3 Handwritten Content and Emphasis

- **Handwritten fill-ins**: Bold any content that was clearly filled in by hand on a form or blank (e.g., "Adopted on **March 15, 1998**")
- **Underlined text**: Convert underlines to bold since we aren't using underlines
- **Purpose**: Makes it immediately clear what was pre-printed vs. manually added
- **Example**: "This ordinance shall take effect **30 days** after adoption" (where "30 days" was handwritten)

### 4. Document Title Standards

All documentTitle fields in Airtable follow standardized formats:

- **Interpretations**: "PC Interpretation - [Topic]"
  - Example: "PC Interpretation - Section 5.080 Setbacks"
- **Ordinances**: "Ordinance #XX - [Topic]" (convert roman numerals to standard numbers)
  - Example: "Ordinance #16 - Establishing a Park Advisory Council"
  - Use full Ordinance number if there is a second part, like "Ordinance 20-1997"
- **Resolutions**: "Resolution #XX - [Topic]"
  - Example: "Resolution #22 - Planning Commission CCI"

When processing documents, always check existing titles and update them to match these standards if needed.

### 5. Quality Control & Best Practices

#### 5.1 Post-Digitization Verification

After completing GitHub upload and URL updates:

- [ ] Documents entry has both fileURL and mdURL
- [ ] rawURL auto-populated correctly
- [ ] Ordinances entry marked as Digitized
- [ ] Bidirectional linking verified
- [ ] Amendment relationships preserved
- [ ] Document title follows naming convention
- [ ] Passed date matches signatures/adoption date

#### 5.2 MCP Tool Notes

- **Always search existing entries** before creating new ones
- Use multiple search terms (ID, year, topic keywords)
- **Array fields (tags, linked records)**: Always pass as strings, not arrays - MCP auto-wraps them
  - See `/Users/leahsilber/Github/daily-claude/mcp-server/MCP_USAGE_GUIDE.md` for full details
- **Inform Leah immediately of any field validation failures** for her decision on resolution
- Link documents to ordinance/resolution records
- Handle field validation errors gracefully (especially for Topics and tags)
- Include topics for searchability using valid options only

#### 5.3 Key Reminders

- Search existing Airtable entries thoroughly before creating new ones
- **Alert Leah immediately to any field validation failures**
- Use established naming conventions consistently
- Focus on accurate transcription over content analysis
- Preserve all original formatting, dates, and signatures
- Claude should ask for GitHub URLs with correct filenames ready for immediate save
- **Digitization Guide updates**: When Leah asks for text to add to the Digitization Guide, always provide it as inline copyable markdown in code blocks rather than artifacts - this allows single-button copying without downloads.
- **Batch URL Updates**: When updating multiple documents with GitHub URLs, use the systematic approach: list all records first to see field structure, then update fileURL and mdURL fields (rawURL will auto-populate)

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
- Otherwise, provide both GitHub web URLs (fileURL for PDF, mdURL for Markdown) for manual entry

---

## mdBook Documentation Site

### Overview

The repository now includes an mdBook static site generator that creates a searchable, browsable website from all the digitized documents. This provides an easy-to-use interface for accessing ordinances, resolutions, interpretations, and transcripts.

### Configuration

**book.toml** - Main configuration file containing:

- Basic metadata (title, authors, description)
- Build settings (output directory: `book/`)
- HTML output configuration with search enabled
- GitHub repository integration
- Custom CSS styling support

### Directory Structure

```text
city_of_rivergrove/
├── src/                  # Source content for mdBook
│   ├── SUMMARY.md       # Table of contents
│   ├── introduction.md  # Welcome page
│   ├── ordinances/      # Ordinance markdown files
│   ├── resolutions/     # Resolution markdown files
│   ├── interpretations/ # Interpretation markdown files
│   └── transcripts/     # Transcript markdown files
├── book/                # Built static website (generated)
├── book.toml           # mdBook configuration
├── build.sh            # Build script
├── custom.css          # Custom styling
└── add-cross-references.py  # Preprocessor script
```

### Build Process

1. **Simple Build**: Run `mdbook build` to generate the static site
2. **Enhanced Build**: Run `./build.sh` which:
   - Adds cross-reference links between documents
   - Builds the mdBook site
   - Outputs to the `book/` directory

### Local Development

To serve the site locally for testing:

```bash
mdbook serve
```

This starts a local server (usually at `http://localhost:3000`) with live-reload for development.

### Adding New Documents

When new documents are digitized:

1. The markdown file is automatically copied to the appropriate `src/` subdirectory
2. Run `python3 fix-signatures.py` to update SUMMARY.md with new entries
3. Run `./build.sh` to rebuild the site with cross-references
4. The new document will appear in the navigation and be searchable

### Features

- **Full-text search**: All documents are searchable through the built-in search functionality
- **Cross-references**: Automatic linking between documents that reference each other
- **Responsive design**: Works on desktop and mobile devices
- **Dark mode support**: Toggle between light and dark themes
- **Print-friendly**: Can generate printer-friendly versions of documents
- **GitHub integration**: Direct links to view source files on GitHub

### Maintenance

- The `src/` directory mirrors the main repository structure but only includes markdown files
- PDF files remain in the root directories but are not included in mdBook
- The `book/` directory is generated and can be safely deleted/regenerated
- Cross-references are added at build time and don't modify source files
