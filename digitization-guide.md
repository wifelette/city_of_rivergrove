# Rivergrove Ordinance Digitization Project - Continuity Guide

## Project Overview

Creating a searchable, centralized repository of all City of Rivergrove ordinances, resolutions, and interpretations. This addresses the current problem where no central listing exists, allowing people to "selectively ignore things or make things up." We have copies of old, hard-to-read photocopied versions, and are working to extract the text as markdown files for saving in Github.

- **Repository**: [GitHub](https://github.com/wifelette/city_of_rivergrove)

## Infrastructure

- **Airtable MCP base** with:
  - Ordinances and Resolutions inventory table (40+ records with varying completeness)
  - Documents table (linked to ordinances)
- **Document storage**: Dropbox links in Airtable
- **Final output**: Markdown files in GitHub repo

## Progress as of August 23, 2025

- **Planning Commission Interpretations**: ✅ **COMPLETE** - All 13 interpretations from 1997-2008 digitized
- **Other completed documents**: City Charter, Resolution 22, Resolution 72, Ordinance #16 (1974)
- **Current focus**: Ordinances from various time periods
- **Tracking**: [GitHub issue #3](https://github.com/wifelette/city_of_rivergrove/issues/3) with comprehensive checklists

## Established Workflow

### 1. Document Processing

- Leah uses Adobe Acrobat for OCR (export as **plain text**, not .docx) and shares with Claude OR has Claude do it directly
- If done via Adobe, Leah uploads source PDF and OCR text output to Claude for final comparison
- Claude creates clean markdown version fixing OCR errors
- Claude reviews for legal terms, dates, and signatures, but doesn't make any changes without explicit approval by Leah, not even fixing typos. We're strictly digitizing as is.
- **Claude searches existing Airtable entries first** before creating new ones
- Claude creates or updates two entries in the Airtable MCP base:
  - 1 Document record for the file
  - 2 Ordinances and Resolutions record for the file
- Leah saves artifact with established naming conventions
- Leah uploads to GitHub and provides URLs to Claude for Airtable updates
- Mark as Digitized once GitHub URL is added

### 2. Naming Conventions

- **Resolutions**: `YYYY-Res-#XX-Topic` (e.g., `1984-Res-#72-Municipal-Services`)
- **Interpretations**: `YYYY-MM-DD-RE-[section]-[brief topic]`
- **Ordinances**: `YYYY-Ord-#XX-Topic` (e.g., `1974-Ord-#16-Parks`)

### 3. Airtable Updates

When processing a document:

- **Always search existing entries first** using multiple search terms
- **Field validation failures**: If any specific field fails validation, inform Leah immediately so she can decide whether to resolve or ignore
- Create/update Documents entry with:
  - `documentType`: "Governing Doc"
  - `tags`: ["Ordinance/Resolution/Interpretation"] (may have validation issues)
  - documentDate
  - documentTitle
  - Dropbox URL (from Leah)
  - Public URL (from Leah once uploaded to Github)
  - Brief description
- Update `Ordinances and Resolutions` entry with:
  - Link to document
  - Summary (dry, objective, searchable)
  - Topics (use existing valid options)
  - Mark as Digitized when GitHub upload complete

### 4. Content Standards

- **No editorializing**: Keep summaries factual and objective
- **Preserve all metadata**: Stamps, signatures, dates, handwritten notes
- **Focus on rote work over content analysis** - Leah doesn't need detailed summaries unless requested
- **Markdown formatting**: Use headers, lists, and clear structure

## Completed Collections

### ✅ Planning Commission Interpretations

**ALL 13 interpretations from 1997-2008 are complete and digitized.**

## Current Phase: Ordinances and Resolutions

- Working chronologically and by availability
- Using new naming convention for ordinances
- Standard workflow applies

## MCP Tool Notes

- **Always search existing entries** before creating new ones
- Use multiple search terms (ID, year, topic keywords)
- **Inform Leah immediately of any field validation failures** for her decision on resolution
- Link documents to ordinance/resolution records
- Handle field validation errors gracefully (especially for Topics and tags)
- Include topics for searchability using valid options only

## Key Workflow Reminders

- Search existing Airtable entries thoroughly before creating new ones
- **Alert Leah immediately to any field validation failures**
- Use established naming conventions consistently
- Focus on accurate transcription over content analysis
- Preserve all original formatting, dates, and signatures
- Claude should ask for GitHub URLs with correct filenames ready for immediate save
