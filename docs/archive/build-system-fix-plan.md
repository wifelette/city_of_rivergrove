# Build System Fix Implementation Plan

## Phase 1: Create New Simplified Scripts (Do First)
*These don't break anything - they're new files we can test before switching over*

### 1.1 Create Master Build Script (`./build-all.sh`)
- Combines all the variant build scripts into ONE
- Auto-detects what needs to be done
- Kills mdbook serve if running (with warning)
- Enforces correct order
- Clear progress messages
- **Handles ALL cases**: with/without Airtable, with/without enhanced formatting

### 1.2 Create Smart Dev Script (`./dev-server.sh`)
- Replaces both `mdbook serve` and `serve.sh`
- Watches files and auto-runs postprocessors
- Shows clear message: "✨ Custom formatting applied"
- Warns if someone runs `mdbook serve` directly

### 1.3 Create Simple Single-File Script (`./build-one.sh`)
- Takes a file path, figures out the rest
- Only processes what's needed (not full rebuild)
- Clear output about what it's doing

## Phase 2: Add Safety Rails (Non-Breaking)
*These prevent future mistakes*

### 2.1 Protect /src Directory
- Add `.gitignore` entry for `/src/` (except SUMMARY.md and introduction.md)
- Create `check-src-edits.sh` that detects manual edits
- Add warning file: `/src/DO_NOT_EDIT_FILES_HERE.md`

### 2.2 Create Pre-Flight Check Script
- Detects common problems before they happen
- Checks if mdbook serve is running
- Verifies source files exist
- Confirms dependencies are installed

## Phase 3: Clean Up Confusion (After Testing New Scripts)

### 3.1 Consolidate Preprocessing
- Check if `standardize-single.py` already combines headers + signatures
- If yes: Delete redundant scripts
- If no: Make it do both, then delete redundant scripts

### 3.2 Create Clear Documentation
- New file: `BUILD-QUICKSTART.md` with just 3 commands
- Put ALL warnings at the TOP in red boxes
- Include "If things go wrong" section

## Phase 4: Migration (Once New System Works)

### 4.1 Update All Documentation
- Replace all script references in CLAUDE.md
- Update claude-code-guide.md
- Update mdbook-guide.md
- Add deprecation notices to old scripts

### 4.2 Archive Old Scripts
- Move to `scripts/build/deprecated/`
- Add README explaining why deprecated
- Keep for 30 days then delete

## Implementation Order

Let's do this systematically:

1. **TODAY**: Create the three new scripts (build-all.sh, dev-server.sh, build-one.sh)
2. **TEST**: Run them on a few documents to ensure they work
3. **SAFEGUARDS**: Add the /src protections
4. **DOCUMENT**: Create the simple quickstart guide
5. **MIGRATE**: Update all references to use new scripts
6. **CLEANUP**: Archive old scripts

## Ready to Start?

Should I begin with Phase 1 - creating the new consolidated scripts? We can test them alongside the existing ones without breaking anything.