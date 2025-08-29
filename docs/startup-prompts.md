# Rivergrove Project - Claude Startup Prompts

Quick reference for starting new Claude sessions on the Rivergrove digitization project.

## Claude Code Startup

```
Hello! We're working on the City of Rivergrove digitization project. Please start by reviewing:
1. CLAUDE.md - workflow and conventions
2. docs/digitization-guide.md - complete project guide
3. docs/build-architecture.md - build system and script dependencies
4. docs/styles/ - formatting standards (naming, signatures, form fields, images)

Check git status to see if there are any uncommitted changes, and if so, commit and push them. Then check GitHub Issue #3 to see which documents are pending processing.

Today I'll be working on: [specify which ordinances/resolutions/interpretations]

Key Reminders:
- NEVER add manual markdown links for cross-references (e.g., [Ordinance #52](../))
- Keep document references as plain text - the build system handles linking
- Use ./scripts/build/update-single.sh for single file rebuilds
- Use ./scripts/build/update-mdbook.sh for full rebuilds
- If mdBook serve is running, manually run custom-list-processor.py to restore form fields
```

## Claude Desktop Startup

```
Hi! We're continuing the Rivergrove ordinance digitization project. Here's what you need to know to jump right in:

Key Resources:
1. Review the Digitization Guide in Project Knowledge - contains complete workflow
2. Airtable MCP tools are connected (daily-tasks:council_*)
3. GitHub repo: https://github.com/wifelette/city_of_rivergrove

Your Mission:

1. When I upload PDFs, follow the established workflow:
   • Search existing entries FIRST (try multiple ID formats: #XX, Ordinance #XX, etc.)
   • Verify PDF page order before transcribing
   • Transcribe as-is (no edits without permission)
   • Keep document references as plain text (e.g., "Ordinance #52") - NO manual links
   • Create/update Airtable records with proper summaries
   • Use established naming conventions
   • Create an entry in the new Public Metadata table that links to the new Ordinance/Resolution/etc, with the Publication Status of Draft

Critical Reminders:
• Always search existing entries first using multiple ID format variations
• Verify PDF page order - some documents have scrambled pages
• List a few records first to see actual field names before updating
• If you get "Record IDs must start with 'rec'" validation error, inform Leah
• Use correct URL structure: fileURL (PDF), mdURL (Markdown), rawURL (auto-populates)

Established Workflow:
1. Search for existing Ordinances and Documents entries
2. Create markdown transcription artifact
3. Create/update Documents entry
4. Update Ordinances entry (mark as digitized, add summary, passed date)
5. Link entries bidirectionally
6. Await GitHub URLs from Leah
7. Update Documents entry with fileURL and mdURL
```
