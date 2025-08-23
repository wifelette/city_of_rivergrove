# Rivergrove Ordinance Digitization Project - Continuity Guide

## Project Overview

Creating a searchable, centralized repository of all City of Rivergrove ordinances, resolutions, and interpretations. This addresses the current problem where no central listing exists, allowing people to "selectively ignore things or make things up." We have copies of old, hard-to-read photocopied versions, and are working to extract the text as markdown files for saving in Github.

- **Repository**: GitHub at https://github.com/wifelette/city_of_rivergrove

## Infrastructure

- **Airtable MCP base** with:
  - Ordinances and Resolutions inventory table (34+ records with varying completeness)
  - Documents table (linked to ordinances)
- **Document storage**: Dropbox links in Airtable
- **Final output**: Markdown files in GitHub repo

## Progress as of August 22, 2025

- **Completed documents**:
  - City Charter
  - Resolution 22
  - Resolution 72
  - Interpretation 1997-07-07-RE-2.040h-permitting-adus
  - Interpretation 1997-09-08-RE-9.030-permit-fees-and-completeness
  - Interpretation 1997-11-03-RE-9.030-permit-fees-and-completeness
  - Interpretation 1998-03-02-RE-5.080-setbacks
  - Interpretation 2004-03-15-RE-5.080-setbacks
- **Created**: GitHub issue with comprehensive checklists organized by document
- **Discovered**: Multi-interpretation document needing careful parsing

## Established Workflow

### 1. Document Processing

- Leah uses Adobe Acrobat for OCR (export as **plain text**, not .docx) and shares with Claude OR has Claude do it directly
- If it was done via Adobe, Leah then uploads source PDF and OCR text output to Claude for final comparison
- Claude creates clean markdown version (fixing OCR errors) as artifact
- Claude reviews for legal terms, dates, and signatures—basically anything that should be captured in the .md file—but doesn't't make any changes without explicit approval by Leah, not even fixing typos. We're strictly digitizing as is.
- Claude creates or finds (if they already exist, in which case they'll need updating) two entries in the Airtable MCP Data base, filling in as much data as it can:
  - 1 is a Document record for the file
  - 2 is an Ordinances and Resolutions record for the file
- Leah downloads the artifact from Claude as an .md file and saves with naming convention:
- For Resolutions:
  - resolution-##
- For Interpretations:
  - YYYY-MM-DD-RE-[section]-[brief topic]
- For Ordinances
  - TBD
- Leah uploads the .md file to Github
- Leah logs the Github URL by adding it to Airtable or providing it to Claude to add
- Once the Github URL is in, Leah or Claude can mark the Document entry as Digitized

### 2. Airtable Updates

When processing a document:

- Create/update Documents entry with:
  - `documentType`: "Governing Doc"
  - `tags`: ["Ordinance/Resolution/Interpretation"]
  - documentDate
  - documentTitle (intuit what this ought be)
  - Dropbox URL (get each time from Leah)
  - Public URL (get each time from Leah once uploaded to Github)
  - Brief description
- Update `Ordinances and Resolutions` base entry with:
  - Link to document
  - Summary (dry, objective, searchable)
  - Topics
  - Mark as Digitized when Leah confirms upload to Github is complete

### 3. Content Standards

- **No editorializing**: Keep summaries factual and objective
- **Preserve all metadata**: Stamps, signatures, dates, handwritten notes
- **Administrative stamps**: Place at end as notations (e.g., LCDC received stamps)
- **Markdown formatting**: Use headers, lists, and clear structure for future programmatic conversion

### 4. GitHub Integration

- Each document gets two tasks: "Digitize" and "Add to GitHub"
- This separation allows for batch processing and version control tracking

## Strategic Considerations

- Many documents are old photocopies with handwritten portions
- OCR struggles with typewriter fonts and handwriting
- Prioritize documents relevant to current issues over chronological processing
- Consider batch OCR for efficiency, then selective Claude review

## MCP Tool Notes

- Use document search/list functions to check existing entries before creating duplicates
- Always link documents to their ordinance/resolution records
- Include topics for searchability

## Multi-Interpretation Document Challenge

Leah discovered a single PDF containing multiple Planning Commission interpretations that she separated and matched to inventory. The document's first page contained this inventory list, which is the first list of what we need to focus on:

### RIVERGROVE LAND USE ORDINANCES - Interpretations Inventory

1. **Interpretation 1997-7-7** (ACCESSORY STRUCTURE RE: PERMIT)
2. **Interpretation 1997-9-8** (FEES, SYSTEM DEVELOPMENT CHARGES)
3. **Interpretation 1997-11-3** (SYSTEM DEVELOPMENT CHARGES)
4. **Interpretation 1998-3-2** (MEASURE SETBACK TO STRUCTURE)
5. **Interpretation 1998-6-1** (SETBACKS—ORIENTATION)
6. **Interpretation 1998-7-6** (SETBACKS—AMENDS PREVIOUS—ADDS FACTOR)
7. **Interpretation 2001-5-7** (BALANCED CUT AND FILL)
8. **Interpretation 2002-8-5** (LOTS PARTIALLY IN FLOODPLAIN)
9. **Interpretation 2002-9-5** (APPEARS SIMILAR TO PREVIOUS)
10. **Interpretation 2004-10-11** (SETBACKS WHERE THERE IS A WQRA TRACT)
11. **Interpretation 2005-4-4** (AREA ACCESSORY DEV PERMIT FOR SEWER)
12. **Interpretation 2008-2-4** (DEFINITION OF MULTI-FAMILY)

**Note**: Also found an unlisted interpretation of Ordinance 68-2000 dated October 16, 2000 about multi-family developments.

We've been working through this list together. Thus far we have completed:

- [x] 1997-07-07-RE-2.040h-permitting-adus
- [x] 1997-09-08-RE-9.030-permit-fees-and-completeness
- [x] 1997-11-03-RE-9.030-permit-fees-and-completeness
- [x] 2004-03-15-RE-5.080-setbacks
