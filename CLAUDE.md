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

## Key Reminders for This Repository

- No Claude attribution in commit messages
- Always provide GitHub web URLs after pushing new documents (for Airtable) - format: `https://github.com/wifelette/city_of_rivergrove/blob/main/[path]`
- Update issue #3 when documents are completed
- **CRITICAL**: Follow naming conventions and rename files in BOTH locations:
  - Rename the original PDF in Dropbox
  - Use the same name for both .md and .pdf files in GitHub
  - This applies to ALL document types (Ordinances, Resolutions, Interpretations)
- Work is part of digitizing City of Rivergrove's ordinances, resolutions, and interpretations
- **After reading a new document .md file, run BOTH standardization scripts**:
  - `python3 standardize-headers.py` to ensure consistent header formatting
  - `python3 fix-signatures.py` to standardize signature blocks
- After providing GitHub URLs:
  - Run `./update-mdbook.sh` to sync files to src/ folders
  - Add the new document to `src/SUMMARY.md` in the appropriate section
  - Run `mdbook build` to rebuild the site