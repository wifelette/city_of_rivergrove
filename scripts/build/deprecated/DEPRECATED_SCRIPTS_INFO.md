# DEPRECATED BUILD SCRIPTS

## ⚠️ DO NOT USE THESE SCRIPTS

These scripts have been replaced by a simplified build system with just 3 scripts in the repository root:

### New Scripts (Use These Instead)

- **`./build-all.sh`** - Replaces all the update-mdbook variants
- **`./build-one.sh`** - Replaces update-single.sh
- **`./dev-server.sh`** - Replaces serve.sh and mdbook serve

### Why These Were Deprecated

1. **Too many variants** - 6+ scripts with unclear differences
2. **Confusing names** - update-mdbook vs update-mdbook-enhanced vs update-mdbook-airtable
3. **Wrong workflow** - serve.sh watched /src instead of source-documents
4. **Error-prone** - Easy to use wrong script or forget steps
5. **Complex** - update-single.sh was 100+ lines for a simple task

### Migration Date

These scripts were deprecated on August 30, 2025 as part of the build system simplification.

### Removal Plan

These deprecated scripts will be kept for 30 days (until September 30, 2025) then deleted.

See `/BUILD-QUICKSTART.md` for the new simplified workflow.