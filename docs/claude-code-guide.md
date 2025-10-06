# Claude Code Workflow - Repository Management

## Overview

This guide covers the Claude Code workflow for managing the City of Rivergrove repository, including file organization, Git operations, and mdBook updates.

- **Repository**: [GitHub](https://github.com/wifelette/city_of_rivergrove)
- **Related Guides**:
  - [Claude Desktop Guide](claude-desktop-guide.md) - Document processing & Airtable
  - [mdBook Guide](mdbook-guide.md) - Site generation and technical details
  - [Build Architecture](build-architecture.md) - Complete build system documentation

## File Organization & Naming Conventions

See **[styles/naming-conventions.md](styles/naming-conventions.md)** for complete naming standards and file organization rules.

**Key Points**:

- All documents follow strict naming patterns
- PDFs must have identical names to their .md counterparts
- Files are organized by document type in their respective folders

**Meeting Documents Organization**:
```
source-documents/Meetings/
├── 2024/
│   ├── 2024-12-09/
│   │   ├── 2024-12-09-Agenda.md
│   │   ├── 2024-12-09-Minutes.md
│   │   └── 2024-12-09-Transcript.md
│   └── 2024-02-12/
│       └── 2024-02-12-Transcript.md
└── 2018/
    └── 2018-04-11/
        └── 2018-04-11-Agenda.md
```
Each meeting has its own folder containing all related documents

## When Digitizing Documents

### 1. Check and Fix Naming EVERYWHERE

**CRITICAL**: Rename files in BOTH locations to follow the naming convention:
- In the GitHub repository (the .md file you're working with)
- In the Dropbox source folder (the original PDF)

**Naming conventions**:
- **Resolutions**: `YYYY-Res-#XX-Topic` (e.g., `2018-Res-#259-Planning-Development-Fees`)
- **Ordinances**: `YYYY-Ord-#XX-Topic` (e.g., `1974-Ord-#16-Parks`)
- **Interpretations**: `YYYY-MM-DD-RE-[section]-[brief topic]`

### 2. Run Standardization Scripts

- Run `python3 scripts/preprocessing/standardize-single.py [path/to/file.md]` to standardize headers and signatures
- This combines header formatting and signature block standardization in one script

### 3. Add PDF

After renaming in Dropbox, copy the PDF to GitHub repository with the same naming.

### 4. Commit and Push

- `git add` both the .md and .pdf files
- Commit with descriptive message (no Claude attribution)
- `git push` to GitHub

### 5. Provide GitHub URLs

After pushing, always provide the GitHub web URLs for Airtable:
- **Markdown**: `https://github.com/wifelette/city_of_rivergrove/blob/main/[path]/file.md`
- **PDF**: `https://github.com/wifelette/city_of_rivergrove/blob/main/[path]/file.pdf`

### 6. Update mdBook

**⚠️ IMPORTANT**: Never edit files in `/src` directly! Always edit source documents, then run sync scripts. The `/src` directory is auto-generated and any direct edits will be lost.

**Option A - Single file (faster):**
- Run `./build-one.sh [path/to/file.md]`
- Example: `./build-one.sh source-documents/Resolutions/2024-Res-#300-Fee-Schedule-Modification.md`

**Option B - Full rebuild (if multiple files changed):**
- Run `./build-all.sh` to sync ALL files to src/ folders and rebuild
- Use `./build-all.sh --quick` to skip Airtable sync for faster local testing

**For development with hot-reload:**
- Run `./dev-server.sh` to start a development server that watches source files
- Automatically rebuilds when you save changes to source documents

**Note**: The build scripts automatically update `src/SUMMARY.md`

### 7. Update Issue #3

- **Always update the issue body**:
  - Check off completed items in the checklist
  - Move to "Completed Documents" section with format: `- [x] Document Name ([commit](link))`
  - If not already listed, add directly to completed section
- **Optionally add a comment** only when there are meaningful changes/decisions to document
- No need to write "Complete" - the checked box is sufficient

## Issue Management

- Keep issue #3 as the single source of truth for digitization progress
- When consolidating repetitive tasks, use "Add to Airtable via Claude Desktop process"
- Bold document names in checklists for visibility: `**Ordinance #XX**`

## Airtable Integration

- Claude Code can potentially update Airtable directly if provided with:
  - Record ID from the Governing table
  - The GitHub URL to add to the Public URL field
- Otherwise, provide both GitHub web URLs (fileURL for PDF, mdURL for Markdown) for manual entry

## Cross-References

**IMPORTANT**: Never add manual markdown links for document references in source files!

- Keep references as plain text (e.g., "Ordinance #52", "Resolution #22")
- The build system automatically converts these to clickable links
- Manual links will be removed if found
- See `docs/markdown-conventions.md` for patterns that are detected

## Visual Regression Testing

When making CSS changes, use visual regression testing to catch unintended layout changes:

```bash
# Run visual tests before making CSS changes
npm run test:visual

# Make your CSS changes in theme/css/
# Edit source files, compile CSS, rebuild

# Run visual tests again to see what changed
npm run test:visual

# Review differences interactively
npm run test:visual:ui

# If changes are intentional, update baselines
npm run test:visual:update
```

**Key Points**:
- Visual tests catch CSS regressions in sections you didn't directly edit
- Full-page screenshots ensure changes don't break distant sections
- See [Visual Testing Guide](visual-testing-guide.md) for complete workflow

## Key Reminders

- No Claude attribution in commit messages
- Work is part of digitizing City of Rivergrove's ordinances, resolutions, and interpretations
- This applies to ALL document types (Ordinances, Resolutions, Interpretations)
- Never add manual cross-reference links - let the build system handle them