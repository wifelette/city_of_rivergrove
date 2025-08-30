# Rivergrove Ordinance Digitization Project - Overview

## Project Goal

Creating a searchable, centralized repository of all City of Rivergrove ordinances, resolutions, and interpretations. This addresses the current problem where no central listing exists, allowing people to "selectively ignore things or make things up." We have copies of old, hard-to-read photocopied versions, and are working to extract the text as markdown files for saving in Github.

- **Repository**: [GitHub](https://github.com/wifelette/city_of_rivergrove)
- **Live Site**: https://wifelette.github.io/city_of_rivergrove/

## Workflow Guides

The digitization project involves three main workflows, each documented separately:

### 1. [Claude Desktop Guide](claude-desktop-guide.md)
**For document processing and Airtable updates**
- OCR and transcription from PDFs
- Creating clean markdown versions
- Updating Airtable records (Documents, Ordinances, Public Metadata)
- Content standards and formatting rules
- Signature blocks and form fields

### 2. [Claude Code Guide](claude-code-guide.md)  
**For repository management**
- File organization and naming conventions
- Running standardization scripts
- Git operations (add, commit, push)
- Providing GitHub URLs for Airtable
- Updating Issue #3 for progress tracking

### 3. [mdBook Guide](mdbook-guide.md)
**For site generation and technical details**
- mdBook static site generator
- File sync workflow
- List formatting standards
- Navigation system features
- Local development setup

## Quick Reference

### Infrastructure
- **Airtable MCP base** with:
  - Ordinances and Resolutions inventory table (40+ records with varying completeness)
  - Documents table (linked to ordinances)
  - Public Metadata table (publication status tracking)
  - See **[airtable-integration.md](airtable-integration.md)** for technical integration details
- **Document storage**: GitHub URLs in Airtable (fileURL for PDFs, mdURL for Markdown)
- **Final output**: Markdown files in GitHub repo

### Style Guides
- [Naming Conventions](styles/naming-conventions.md) - File naming standards
- [Signature Formatting](styles/signature-formatting.md) - Signature block standards
- [Form Fields](styles/form-fields.md) - Form field syntax
- [Inline Images](styles/inline-images.md) - Image handling
- [Markdown Conventions](markdown-conventions.md) - Document formatting standards

### Technical Documentation
- [Build Architecture](build-architecture.md) - Complete build system documentation
- [Scripts Guide](../scripts/SCRIPTS-GUIDE.md) - All script documentation
- [Startup Prompts](startup-prompts.md) - Quick reference for starting new Claude sessions

## Session Startup

For quick reference prompts to start new Claude sessions, see **[startup-prompts.md](startup-prompts.md)** which contains specific prompts for both Claude Code and Claude Desktop workflows.