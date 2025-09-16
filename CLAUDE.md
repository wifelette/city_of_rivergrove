# Claude Code Instructions for City of Rivergrove Repository

## Important Context Files to Read

Please read these files for context on this project and how to work with Leah:

1. **Main project guides**:

   - `docs/digitization-guide.md` - Project overview and links to all guides
   - `docs/claude-code-guide.md` - Repository management workflow (most relevant for Claude Code)
   - `docs/mdbook-guide.md` - mdBook site generation and technical details
   - `docs/build-architecture.md` - Complete build system documentation, script dependencies, and processing order

2. **Style and formatting guides**:

   - `docs/styles/naming-conventions.md` - File naming standards
   - `docs/styles/form-fields.md` - Form field syntax and validation
   - `docs/styles/signature-formatting.md` - Signature block standards
   - `docs/markdown-conventions.md` - Cross-references and formatting patterns

3. **Technical documentation**:

   - `docs/scripts/SCRIPTS-GUIDE.md` - All script documentation
   - `docs/airtable-integration.md` - Airtable sync and metadata
   - `docs/metadata-architecture.md` - Metadata system overview

4. **General working preferences**:
   - `/Users/leahsilber/Github/daily_tasks/CLAUDE.md` - Leah's general preferences when working with Claude Code

If you are instructed to review this file or any others, but skip any files or sections, or cannot access any of them, let Leah know right away so she has an accurate understanding of your context for each interaction.

## COMPLETE PROCESSING WORKFLOW

**When Leah says "process [document name]", follow ALL these steps:**

### Step 1: Find Document in Airtable

- Use MCP tool to search existing records first
- Try multiple search formats: document number (e.g., "52"), full reference (e.g., "Ordinance 52"), or topic keywords
- The record will show document type, year, number, topic, and processing status
- Use this information to locate the .md file in the appropriate folder:
  - `source-documents/Ordinances/`
  - `source-documents/Resolutions/`
  - `source-documents/Interpretations/`
  - `source-documents/Meetings/[YYYY]/[YYYY-MM-DD]/`

### Step 2: Run Standardization Script (if needed)

- Run `python3 scripts/preprocessing/standardize-single.py [path/to/file.md]` to standardize headers and signatures
- Example: `python3 scripts/preprocessing/standardize-single.py source-documents/Resolutions/2024-Res-#300-Fee-Schedule-Modification.md`
- This standardizes headers and signature formatting for the single file

### Step 3: Check and Fix Naming EVERYWHERE

**CRITICAL - This step is often missed!**

- Verify the naming convention is correct (see `docs/styles/naming-conventions.md` for full details)
- If naming is incorrect, rename files in BOTH locations:
  - Use `git mv` to rename the .md file in the GitHub repository
  - Use `mv` to rename the original PDF in Dropbox at the same path
  - Both files (.md and .pdf) must have identical naming

### Step 4: Copy PDF to Repository

- Copy the PDF from Dropbox to the GitHub repository (same folder as .md)
- Ensure the PDF has the exact same name as the .md file

### Step 5: Commit and Push

- `git add` both the .md and .pdf files
- Commit with descriptive message (no Claude attribution)
- `git push` to GitHub

### Step 6: Provide GitHub URLs

**Always provide BOTH URLs for Airtable:**

- **Markdown URL**: `https://github.com/wifelette/city_of_rivergrove/blob/main/[path]/[filename].md`
- **PDF URL**: `https://github.com/wifelette/city_of_rivergrove/blob/main/[path]/[filename].pdf`

### Step 7: Update mdBook

**Option A - Single file (faster):**

- Run `./build-one.sh [path/to/file.md]` to sync and rebuild just this file
- Example: `./build-one.sh source-documents/Resolutions/2024-Res-#300-Fee-Schedule-Modification.md`

**Option B - Full rebuild (if multiple files changed):**

- Run `./build-all.sh` to sync ALL files and rebuild entire site

## CRITICAL: CSS and Development Server Usage

**ALWAYS use `./dev-server.sh` for development!**

### Why This is Critical

We have safeguards in place to prevent using `mdbook serve` directly:
- `./mdbook` wrapper automatically redirects to dev-server.sh
- Git hooks prevent commits if mdbook serve is running
- See `docs/safeguards-guide.md` for complete details

### CSS System Overview

**CSS is now compiled from modular files:**
- Source CSS modules are in `theme/css/` (organized by component)
- `scripts/build/compile-css.py` compiles them into `custom.css`
- The compiled CSS persists through mdBook rebuilds
- See `docs/css-refactor/css-compilation-guide.md` for details

### If styles disappear:

**Quick fix:**
```bash
./scripts/fix-styles.sh
```

This runs CSS compilation and postprocessors automatically.

### When editing CSS:

1. **Edit source files** in `theme/css/` (never edit custom.css directly)
2. **CSS compiles automatically** when using dev-server.sh
3. **Manual compilation** if needed: `python3 scripts/build/compile-css.py`

### Testing for issues:

```bash
# Check for direct /src edits
./scripts/validation/check-src-modifications.sh

# Verify CSS health
python3 scripts/validation/check-styles-health.py
```

### Step 8: Update Issue #3

- **Always update the issue body**:
  - Check off completed items in the checklist
  - Move completed items to the appropriate "Completed Documents" section
  - Include commit link when moving items
  - If document wasn't on the list, add it directly to completed section with commit link
- **Optionally add a comment** only if:
  - There were meaningful changes or decisions made worth documenting
  - You encountered and resolved specific issues that might be helpful for future reference
  - The changes involved something beyond standard processing

## Document Notes

**IMPORTANT**: Use proper markdown syntax for Document Notes sections!

- Create a section with `## Document Notes` at the end of documents
- Use H3 headers (`###`) for different note types (Stamp, Handwritten text, etc.)
- Include page references directly in H3 headers: `### Stamp {{page:3}}`
- The build system automatically styles these with badges and proper formatting
- See `docs/styles/document-notes.md` for complete syntax guide

Example:

```markdown
## Document Notes

### Stamp {{page:3}}

COPY

### Handwritten text {{page:2}}

I certify this to be a true copy.
Rosalie Morrison
City Recorder
```

## Form Field Validation

The build system automatically validates `{{filled:}}` form field syntax at multiple levels:

- **VSCode**: Real-time validation with custom markdownlint rule (red squiggles for errors)
- **Build Scripts**: Automatic validation prevents broken tags from reaching production
- **Dev Server**: Validates on every file save, blocks processing if errors found

If you encounter form field errors:

1. Check for unclosed tags: `\{\{filled:text` should be `\{\{filled:text\}\}`
2. Ensure colon after "filled": `\{\{filled:text\}\}` not `\{\{filledtext\}\}`
3. Run manual validation: `python3 scripts/validation/validate-form-fields.py [file]`
4. Use `--fix` flag to auto-fix simple issues: `python3 scripts/validation/validate-form-fields.py --fix`

See `docs/styles/form-fields.md` for complete syntax guide and validation details.

## Cross-References

**IMPORTANT**: Never add manual markdown links for document references in source files!

- Keep references as plain text (e.g., "Ordinance #52", "Resolution #22")
- The build system automatically converts these to clickable links
- Manual links will be removed if found
- See `docs/markdown-conventions.md` for patterns that are detected

## Key Reminders

- No Claude attribution in commit messages
- Work is part of digitizing City of Rivergrove's ordinances, resolutions, and interpretations
- This applies to ALL document types (Ordinances, Resolutions, Interpretations)
- Never add manual cross-reference links - let the build system handle them
