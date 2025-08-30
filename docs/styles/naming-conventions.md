# Document Naming Conventions

## Overview

All City of Rivergrove documents follow strict naming conventions to ensure consistency and searchability across the repository. These conventions apply to both the source files and their locations in the repository.

## File Naming Patterns

### Ordinances
**Pattern**: `YYYY-Ord-#XX-Topic`

- **YYYY**: 4-digit year of passage
- **Ord**: Document type identifier
- **#XX**: Ordinance number (may include suffix like -89C)
- **Topic**: Brief descriptive topic (dash-separated)

**Examples**:
- `1974-Ord-#16-Parks.md`
- `1989-Ord-#54-89C-Land-Development.md`
- `2001-Ord-#70-2001-WQRA.md`

### Resolutions
**Pattern**: `YYYY-Res-#XX-Topic`

- **YYYY**: 4-digit year of passage
- **Res**: Document type identifier
- **#XX**: Resolution number
- **Topic**: Brief descriptive topic (dash-separated)

**Examples**:
- `1984-Res-#72-Municipal-Services.md`
- `2024-Res-#300-Fee-Schedule-Modification.md`

### Interpretations
**Pattern**: `YYYY-MM-DD-RE-[section]-[topic]`

- **YYYY-MM-DD**: Full date of interpretation
- **RE**: Document type identifier
- **[section]**: Code section being interpreted (optional)
- **[topic]**: Brief descriptive topic (dash-separated)

**Examples**:
- `1998-06-01-RE-5.080-setback-orientation.md`
- `2001-05-07-RE-balanced-cut-and-fill.md`

### Meeting Documents
**Pattern**: `YYYY-MM-DD-[Type]`

- **YYYY-MM-DD**: Full date of meeting
- **[Type]**: Document type (Agenda, Minutes, Transcript)

**Examples**:
- `2018-04-11-Agenda.md`
- `2018-05-14-Agenda.md`
- `2024-02-12-Minutes.md`
- `2024-12-09-Transcript.md`

**Special Meeting Types** (optional suffixes):
- `2024-03-15-Minutes-Special` (Special Meeting)
- `2024-06-20-Agenda-Emergency` (Emergency Meeting)
- `2024-09-10-Transcript-Workshop` (Workshop)

**Multiple Meetings Same Day**:
- `2024-04-11-Minutes-1` (First meeting)
- `2024-04-11-Minutes-2` (Second meeting)

## File Organization

### Source Locations
Documents are stored in their respective directories:
- **Ordinances**: `/source-documents/Ordinances/` (with # in filename)
- **Resolutions**: `/source-documents/Resolutions/` (with # in filename)
- **Interpretations**: `/source-documents/Interpretations/`
- **Meeting Documents**: `/source-documents/Meetings/[YYYY]/[YYYY-MM-DD]/` (organized by year and date)
- **Other Documents**: `/source-documents/Other/` or root level

**Meeting Documents Organization**:
Each meeting has its own folder containing all related documents:
```
source-documents/Meetings/
├── 2024/
│   ├── 2024-12-09/
│   │   ├── 2024-12-09-Agenda.md
│   │   ├── 2024-12-09-Minutes.md
│   │   └── 2024-12-09-Transcript.md
│   └── 2024-02-12/
│       └── 2024-02-12-Transcript.md
└── 2018/
    └── 2018-04-11/
        └── 2018-04-11-Agenda.md
```

### mdBook Source (src/)
When synced to mdBook, files are copied to `/src/` subdirectories with the # character removed where applicable:
- `/source-documents/Ordinances/1974-Ord-#16-Parks.md` → `/src/ordinances/1974-Ord-16-Parks.md`
- `/source-documents/Resolutions/1984-Res-#72-Municipal-Services.md` → `/src/resolutions/1984-Res-72-Municipal-Services.md`
- `/source-documents/Meetings/2018/2018-04-11/2018-04-11-Agenda.md` → `/src/agendas/2018-04-11-Agenda.md`
- `/source-documents/Meetings/2024/2024-02-12/2024-02-12-Minutes.md` → `/src/minutes/2024-02-12-Minutes.md`
- `/source-documents/Meetings/2024/2024-12-09/2024-12-09-Transcript.md` → `/src/transcripts/2024-12-09-Transcript.md`

## PDF Storage

Source PDFs must have **identical naming** to their markdown counterparts:
- Markdown: `1978-Ord-#28-Parks.md`
- PDF: `1978-Ord-#28-Parks.pdf`

Both files are stored in the same directory.

## Important Notes

1. **Case Sensitivity**: Use proper capitalization in topics (e.g., "Land-Development" not "land-development")
2. **Special Characters**: Only use dashes (-) as separators, no spaces or underscores
3. **Consistency**: Both .md and .pdf files must have identical base names
4. **Year Suffixes**: Some ordinances include the year as a suffix (e.g., #70-2001) - preserve these
5. **Letter Suffixes**: Some ordinances have letter suffixes (e.g., #54-89C) - preserve these

## Validation

Before finalizing any document:
1. Verify the naming follows the correct pattern
2. Ensure both .md and .pdf files have matching names
3. Check that files are in the correct directory
4. Confirm the # character is present in source files (source-documents/Ordinances/Resolutions)

## Airtable Correspondence

The naming convention corresponds to Airtable fields:
- Document title in Airtable: "Ordinance #28 - Parks Advisory Council"
- GitHub filename: `1978-Ord-#28-Parks.md`
- The link is made through the GitHub Path field in Airtable