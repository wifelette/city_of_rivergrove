# Claude Code Instructions for City of Rivergrove Repository

## Important Context Files to Read

Please read these two files for context on this project and how to work with Leah:

1. **Project-specific guide**: Read the `digitization-guide.md` file in this repository for details about the Rivergrove ordinance digitization project, including:
   - Project overview and goals
   - Naming conventions for documents
   - Claude Code workflow for repository management
   - Issue #3 management procedures

2. **General working preferences**: Read `/Users/leahsilber/Github/daily_tasks/CLAUDE.md` for Leah's general preferences when working with Claude Code, including:
   - Communication style preferences
   - How to handle errors and issues
   - General productivity tips

## COMPLETE PROCESSING WORKFLOW

**When Leah says "process [document name]", follow ALL these steps:**

### Step 1: Locate and Read the Document
- Find the .md file in the appropriate folder (Resolutions/, Ordinances/, Interpretations/)
- Read the document to understand its content

### Step 2: Run Standardization Scripts
- Run `python3 standardize-headers.py` to ensure consistent header formatting
- Run `python3 fix-signatures.py` to standardize signature blocks

### Step 3: Check and Fix Naming EVERYWHERE
**CRITICAL - This step is often missed!**
- Verify the naming convention is correct:
  - **Resolutions**: `YYYY-Res-#XX-Topic` (e.g., `2024-Res-#300-Fee-Schedule-Modification`)
  - **Ordinances**: `YYYY-Ord-#XX-Topic` (e.g., `1974-Ord-#16-Parks`)
  - **Interpretations**: `YYYY-MM-DD-RE-[section]-[brief topic]`
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
- Run `./update-mdbook.sh` to sync files to src/ folders
- Run `mdbook build` to rebuild the site

### Step 8: Update Issue #3
- Add a comment to issue #3 noting the document has been processed
- Format: "✅ [Document Name] has been added to the repository"

## Key Reminders

- No Claude attribution in commit messages
- Work is part of digitizing City of Rivergrove's ordinances, resolutions, and interpretations
- This applies to ALL document types (Ordinances, Resolutions, Interpretations)