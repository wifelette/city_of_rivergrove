# Claude Code Instructions for City of Rivergrove Repository

## Important Context Files to Read

Please read these files for context on this project and how to work with Leah:

1. **Project-specific guide**: Read the `docs/digitization-guide.md` file in this repository for details about the Rivergrove ordinance digitization project, including:

   - Project overview and goals
   - Naming conventions for documents
   - Claude Code workflow for repository management

2. **Build system architecture**: Read `docs/build-architecture.md` for understanding the processing pipeline:

   - Script dependencies and order
   - How cross-references work
   - Common issues and solutions

3. **General working preferences**: Read `/Users/leahsilber/Github/daily_tasks/CLAUDE.md` for Leah's general preferences when working with Claude Code, including:
   - Communication style preferences
   - How to handle errors and issues
   - General productivity tips

## COMPLETE PROCESSING WORKFLOW

**When Leah says "process [document name]", follow ALL these steps:**

### Step 1: Find Document in Public Metadata

- Use MCP tool to search: `daily-tasks:council_public_metadata_list` with search parameter
- Try multiple search formats: document number (e.g., "52"), full reference (e.g., "Ordinance 52"), or topic keywords
- The record will show document type, year, number, topic, and processing status
- Use this information to locate the .md file in the appropriate folder (source-documents/Resolutions/, source-documents/Ordinances/, source-documents/Interpretations/)
- No need to read the full document just to get basic metadata

### Step 2: Run Standardization Script

- Run `python3 scripts/preprocessing/standardize-single.py [path/to/file.md]` to standardize headers and signatures
- Example: `python3 scripts/preprocessing/standardize-single.py source-documents/Resolutions/2024-Res-#300-Fee-Schedule-Modification.md`
- This only processes the single file you're working on (much faster than processing all files)

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

- Run `./scripts/build/update-single.sh [path/to/file.md]` to sync just this file and rebuild
- Example: `./scripts/build/update-single.sh source-documents/Resolutions/2024-Res-#300-Fee-Schedule-Modification.md`

**Option B - Full sync (if multiple files changed):**

- Run `./scripts/build/update-mdbook.sh` to sync ALL files to src/ folders and rebuild

**IMPORTANT - mdBook serve limitations:**

- If `mdbook serve` is running, it auto-rebuilds when files change BUT does NOT run our postprocessors
- This means form fields (see `docs/styles/form-fields-syntax.md`) and other custom formatting will disappear
- To see the REAL appearance with all formatting:
  1. After any changes while `mdbook serve` is running
  2. Manually run: `python3 scripts/postprocessing/custom-list-processor.py`
  3. This restores form field styling and other custom formatting
- Alternatively, use the build scripts above which include postprocessing

### Step 8: Update Issue #3

- Update the checklist in the body of issue #3 noting the document has been processed; if it's already on the list, check it off, link to the commit, and move it to the appropriate section of the completed section below. If it wasn't on the list, add it to the completed items section, also with a commit link.

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
