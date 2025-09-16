# Rivergrove Project - Claude Startup Prompts

Quick reference for starting new Claude sessions on the Rivergrove digitization project.

## Claude Code Startup

```
Hello! We're working on the City of Rivergrove digitization project. Please start by reviewing:
1. CLAUDE.md - complete workflow and conventions
2. docs/claude-code-guide.md - repository management workflow
3. docs/mdbook-guide.md - mdBook site and build information
4. docs/build-architecture.md - build system and script dependencies
5. docs/styles/ - formatting standards (naming, signatures, form fields, images)
6. docs/scripts/SCRIPTS-GUIDE.md - complete script documentation
7. docs/metadata-architecture.md - metadata system overview

Check git status to see if there are any uncommitted changes, and if so, commit and push them.

Today I'll be working on:
```

### Docs Cleanup Prompt

```
Today I'd like to start with a holistic review of our docs. That means making sure there aren't any docs living outside of /docs that need to be moved, and then reviewing the contents of our /docs for:
1. things that aren't properly nested in subdirectories,
2. things that conflict with each other or are outdated,
3. things that have unnecessarily duplicate content and lastly,
4. any other suggestions you might have.
```

## Claude Desktop Startup

```
Hi! We're continuing the Rivergrove ordinance digitization project. Here's what you need to know to jump right in:

Key Resources:
1. Review the Claude Desktop Guide in Project Knowledge - contains document processing workflow
2. Airtable MCP tools are connected (daily-tasks:council_*)
3. GitHub repo: https://github.com/wifelette/city_of_rivergrove (and you have access to some of the contents of the repo via Project Documents)

Your Mission:

1. When I upload PDFs, follow the established workflow:
   • Search existing entries FIRST (try multiple ID formats: #XX, Ordinance #XX, etc.)
   • Verify PDF page order before transcribing
   • Transcribe as-is (no edits without permission)
   • Keep document references as plain text (e.g., "Ordinance #52") - NO manual links
   • Create/update Airtable records with proper summaries
   • Use established naming conventions
   • Create THREE entries in Airtable:
     - Documents entry (with fileURL and mdURL after GitHub upload)
     - Ordinances/Resolutions entry (mark Digitized after GitHub upload)
     - Public Metadata entry (Status: Draft → Published after GitHub upload)

Critical Reminders:
• Always search existing entries first using multiple ID format variations
• Verify PDF page order - some documents have scrambled pages
• List a few records first to see actual field names before updating
• If you get "Record IDs must start with 'rec'" validation error, inform Leah
• Use correct URL structure: fileURL (PDF), mdURL (Markdown), rawURL (auto-populates)
• When processing the PDFs or other documents into .md format for the digitization, follow the markdown conventions outined in docs/markdown-conventions.md

Established Workflow:
1. Search for existing Ordinances/Resolutions and Documents entries
2. Create markdown transcription artifact
3. Create/update Documents entry (documentType: "Governing Doc")
4. Update Ordinances/Resolutions entry (add summary, passed date)
5. Create Public Metadata entry (Status: "Draft", linked to Ordinance/Resolution)
6. Await GitHub URLs from Leah
7. Update Documents with fileURL and mdURL
8. Mark Ordinances/Resolutions as Digitized
9. Change Public Metadata Status to "Published"
```
