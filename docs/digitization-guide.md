# Rivergrove Ordinance Digitization Project - Continuity Guide

## Project Overview

Creating a searchable, centralized repository of all City of Rivergrove ordinances, resolutions, and interpretations. This addresses the current problem where no central listing exists, allowing people to "selectively ignore things or make things up." We have copies of old, hard-to-read photocopied versions, and are working to extract the text as markdown files for saving in Github.

- **Repository**: [GitHub](https://github.com/wifelette/city_of_rivergrove)

## Infrastructure

- **Airtable MCP base** with:
  - Ordinances and Resolutions inventory table (40+ records with varying completeness)
  - Documents table (linked to ordinances)
  - See **[airtable-integration.md](airtable-integration.md)** for technical integration details
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
- **Cross-references**: Keep document references as plain text (e.g., "Ordinance #52", "Resolution #22")
  - NEVER add manual markdown links for cross-references
  - The build system automatically converts these to clickable links
  - See `docs/markdown-conventions.md` for patterns that are detected

#### 3.1 Signature Section Formatting

See **[styles/signature-formatting.md](styles/signature-formatting.md)** for complete signature block formatting standards.

**Key Points:**
- Use `[Signature], Name, Title` format (all on one line)
- Add double spaces at end of lines for proper breaks
- Use `{{filled:}}` for handwritten dates
- Preserve exact date formats from source
- Run `scripts/preprocessing/fix-signatures.py` to standardize automatically

#### 3.2 Page Break Handling

- **Ignore page breaks**: Transcribe documents continuously without page markers
- **No page numbers needed**: Don't add "Page 1", "---", or similar markers
- **Single flowing document**: Present the entire ordinance as one continuous markdown file
- **Exception**: Only note page breaks if they are for some reason meaningful (like when legal documents say "Continue on next page" or "this section intentionally left blank")

#### 3.3 Handwritten Content and Form Fields

See **[styles/form-fields.md](styles/form-fields.md)** for complete guide on handling blank and filled fields.

**Key Points**:
- Use `{{filled:}}` for blank fields in source documents
- Use `{{filled:text}}` for handwritten/filled content
- Always use `{{filled:}}` for handwritten dates in signature blocks
- Underlined text: Convert to bold (we don't use underlines except for form fields)

#### 3.4 Images and Diagrams

See **[styles/inline-images.md](styles/inline-images.md)** for handling images, diagrams, and visual content.

**Key Points**:
- Use `{{image:filename.png|caption=Description|alt=Alt text}}` syntax
- Images are stored in `book/images/[document-type]/`
- Screenshots and diagrams should be saved as PNG files

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

See **[styles/naming-conventions.md](styles/naming-conventions.md)** for complete naming standards and file organization rules.

**Key Points**:
- All documents follow strict naming patterns
- PDFs must have identical names to their .md counterparts
- Files are organized by document type in their respective folders

### 2. When Digitizing Documents

1. **Check and fix naming EVERYWHERE**: 
   - **CRITICAL**: Rename files in BOTH locations to follow the naming convention:
     - In the GitHub repository (the .md file you're working with)
     - In the Dropbox source folder (the original PDF)
   - **Naming conventions**:
     - **Resolutions**: `YYYY-Res-#XX-Topic` (e.g., `2018-Res-#259-Planning-Development-Fees`)
     - **Ordinances**: `YYYY-Ord-#XX-Topic` (e.g., `1974-Ord-#16-Parks`)
     - **Interpretations**: `YYYY-MM-DD-RE-[section]-[brief topic]`
2. **Run standardization scripts**:
   - Run `python3 scripts/preprocessing/standardize-headers.py` to ensure consistent header formatting
   - Run `python3 scripts/preprocessing/fix-signatures.py` to standardize signature blocks
3. **Add PDF**: After renaming in Dropbox, copy the PDF to GitHub repository with the same naming
4. **Commit and Push**: When new .md and .pdf files are added to the repo, commit with descriptive message and push to GitHub (no Claude attribution needed)
5. **Provide GitHub Links**: After pushing, always provide the GitHub web URLs for Airtable:
   - Markdown: `https://github.com/wifelette/city_of_rivergrove/blob/main/[path]/file.md`
   - PDF: `https://github.com/wifelette/city_of_rivergrove/blob/main/[path]/file.pdf`
6. **Update mdBook**: 
   - **Option A - Single file (faster)**: Run `./scripts/build/update-single.sh [path/to/file.md]`
   - **Option B - Full sync**: Run `./scripts/build/update-mdbook.sh` to sync ALL documents and rebuild
   - Note: The build scripts automatically update `src/SUMMARY.md`
7. **Update Issue #3**:
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

The repository includes an mdBook static site generator that creates a searchable, browsable website from all digitized documents. The site includes enhanced navigation with list formatting fixes and improved document display.

### File Structure & Sync Workflow

**IMPORTANT**: There are two separate directories for ordinances:

- **`source-documents/Ordinances/`** (capital O) - Main directory for editing files (includes `#` in filenames)
- **`src/ordinances/`** (lowercase o) - mdBook source directory (filenames without `#`)

**Current Workflow** (due to sync issues discovered):

1. **Edit files** in the main `source-documents/Ordinances/` directory
2. **Manual sync**: Run `./scripts/build/update-mdbook.sh` to sync changes to `src/` and rebuild
3. **View changes** at `http://localhost:3000`

**Automated sync** is available but currently **not recommended** due to content override issues:
- `./watch-and-sync.py` - File watcher for auto-sync (use with caution)
- Issue: Unknown process sometimes generates auto-headers that override file content
- **Symptom**: File content temporarily disappears and gets replaced with auto-generated headers
- **Workaround**: Use manual sync with `./scripts/build/update-mdbook.sh` and restore content if needed

### Directory Structure

```text
city_of_rivergrove/
├── source-documents/Ordinances/           # Main editing directory (with # in filenames)
├── src/                  # Source content for mdBook
│   ├── SUMMARY.md       # Table of contents
│   ├── introduction.md  # Welcome page
│   ├── ordinances/      # Synced ordinance files (no # in filenames)
│   ├── resolutions/     # Resolution markdown files
│   ├── interpretations/ # Interpretation markdown files
│   └── transcripts/     # Transcript markdown files
├── book/                # Built static website (generated)
├── sync-ordinances.py   # Manual sync script
├── watch-and-sync.py    # Auto file watcher (use with caution)
├── scripts/
│   └── build/
│       └── update-mdbook.sh  # Combined sync + build script
├── book.toml           # mdBook configuration
├── custom.css          # Custom styling
└── add-cross-references.py  # Preprocessor script
```

### Local Development

1. **Start mdBook server**:
   ```bash
   mdbook serve
   ```
   
2. **Edit files** in `source-documents/` directories (Ordinances/, Resolutions/, etc.)

3. **Sync changes**:
   - **For single file**: `./scripts/build/update-single.sh [path/to/file.md]`
   - **For all files**: `./scripts/build/update-mdbook.sh`

4. **View at** `http://localhost:3000`

### List Formatting Standards

Legal documents require exact preservation of enumeration styles for reference integrity. Our system uses post-processing to handle special list formats while keeping source markdown pure.

**Source Format Preservation:**
- Keep original legal formatting in source files: `(1)`, `(a)`, `(i)`
- Do NOT convert to standard markdown lists in source files
- The custom-list-processor.py handles conversion during build

**Supported List Formats:**
- **Numbered lists**: `(1)`, `(2)`, `(3)` → Rendered with preserved markers
- **Letter lists**: `(a)`, `(b)`, `(c)` → Rendered with preserved markers  
- **Roman numerals**: `(i)`, `(ii)`, `(iii)` → Rendered with preserved markers
- **Standard markdown**: `1.`, `2.`, `3.` → Standard rendering

**Processing Workflow:**
1. Source files maintain exact legal formatting
2. mdBook builds HTML from markdown
3. `custom-list-processor.py` post-processes HTML to create proper lists
4. CSS styling preserves original markers while improving visual structure

**Examples in source markdown:**
```markdown
(1) First numbered item with legal formatting
(2) Second numbered item 
    (a) Letter subitem preserved exactly
    (b) Another letter subitem
        (i) Roman numeral nested item
        (ii) Another roman numeral
(3) Third numbered item
```

**Common issues resolved:**
- Lists not rendering as lists (appearing as paragraphs)
- Wrong enumeration conversion (letters to numbers, etc.)
- Sync scripts overwriting manual fixes
- Need to preserve exact legal enumeration for reference

### Navigation System Status

**Tracking**: [GitHub Issue #10](https://github.com/wifelette/city_of_rivergrove/issues/10) - Navigation Enhancement Implementation

**Status**: Navigation system operational with the following components:

- ✅ Style E format implemented (#XX - Title (Year))
- ✅ List formatting fixes applied to all ordinances
- ✅ Enhanced navigation controls with dropdown context switcher
- ✅ Other Documents section functional (City Charter)
- ✅ Clean home page presentation with hidden sidebars
- ✅ Minimum threshold grouping (10+ documents) prevents single-item groups
- ✅ Document selection states and active indicators working
- ✅ mdBook UI elements properly hidden (duplicate titles, hamburger menu)
- ⚠️ File sync workflow established but needs stability improvements
- 🔄 Right panel for document relationships planned

### Features

- **Full-text search**: All documents searchable
- **Cross-references**: Automatic linking between documents
- **Proper list rendering**: All nested lists display correctly
- **Responsive design**: Works on desktop and mobile
- **GitHub integration**: Direct links to source files

### Maintenance

- Edit in `source-documents/Ordinances/` directory (main source of truth)
- Use `./scripts/build/update-mdbook.sh` for safe syncing
- The `book/` directory is generated and can be safely regenerated
- Monitor [Issue #10](https://github.com/wifelette/city_of_rivergrove/issues/10) for navigation updates

---

## Session Startup Prompts

See **[STARTUP-PROMPTS.md](STARTUP-PROMPTS.md)** for quick reference prompts to start new Claude sessions for both Claude Code and Claude Desktop workflows.
