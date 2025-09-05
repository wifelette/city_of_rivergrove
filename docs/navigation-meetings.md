# Meeting Documents Navigation

## Overview

Meeting documents (Agendas, Minutes, and Transcripts) have a specialized navigation interface that differs from other document types in the City of Rivergrove digital archive.

## Key Differences from Other Document Types

### 1. No View Options
Unlike Ordinances, Resolutions, and Interpretations which offer multiple view options (Numerical, Chronological, Topical), meeting documents have no view selection controls. The view controls are completely hidden when viewing meeting documents.

### 2. Nested Year/Month/Date Grouping
Meeting documents are organized in a three-level hierarchy:
- **Years** are expandable/collapsible sections with light backgrounds
- **Months** within each year are also expandable (e.g., "June 2017")
- **Individual documents** are shown with type badges (AGENDA, MINUTES, TRANSCRIPT)

### 3. Document Type Badges
Each document displays with a styled badge indicating its type:
- **AGENDA** - Light blue badge
- **MINUTES** - Light green badge  
- **TRANSCRIPT** - Light purple badge

Documents are displayed in chronological order within each month.

### 4. Expandable Navigation
The navigation uses an accordion pattern:
- Click year headers to expand/collapse all months in that year
- Click month headers to expand/collapse documents in that month
- The system remembers your expanded/collapsed state using localStorage
- The current document's year and month auto-expand on page load

### 5. Visual Design
- Year headers have light gray backgrounds with borders
- Year content is contained in bordered boxes for visual cohesion
- Month headers are more subtle with lighter backgrounds
- Selected documents are highlighted with a blue background
- Smooth transitions for expand/collapse animations

## Implementation Details

### JavaScript Changes (navigation-standalone.js)

1. **Document Type Detection**
   - When `currentDocType === 'transcripts'`, special rendering is triggered
   - This includes all meeting-related document types: transcript, meeting, agenda, minutes

2. **View Controls Hiding**
   ```javascript
   if (type === 'transcripts') {
       // Hide view controls entirely for meetings
       if (viewControls) viewControls.style.display = 'none';
   }
   ```

3. **Custom Rendering Method**
   - `renderMeetingDocuments(container, docs)` handles the special display logic
   - Groups documents by year, then by month
   - Formats dates in readable format (e.g., "June 2017")
   - Implements expandable/collapsible sections with chevron icons
   - Persists expanded state in localStorage

### Data Structure

Meeting documents in the relationships.json have the following structure:
```json
{
  "type": "agenda|minutes|transcript",
  "date": "YYYY-MM-DD",
  "file": "filename.md"
}
```

### Metadata Integration

Meeting metadata from Airtable is stored in `meetings-metadata.json` and includes:
- Display names
- Short titles
- Meeting dates
- Document URLs

The system handles timezone issues by extracting dates from filenames when available, avoiding UTC shift problems.

## User Experience

From the user's perspective:
1. Select "Meeting Records" from the dropdown
2. View controls disappear
3. Documents are displayed grouped by meeting date
4. Each date shows all available documents for that meeting
5. Click any document to view it
6. Use sort arrows to reverse chronological order if desired

## Folder Structure

Meeting documents are organized in folders by year and month:
```
source-documents/Meetings/
├── 2017/
│   ├── 2017-06/
│   │   ├── 2017-06-12-Agenda.md
│   │   └── 2017-06-12-Minutes.md
│   └── 2017-11/
│       └── 2017-11-13-Minutes.md
├── 2018/
│   ├── 2018-04/
│   │   └── 2018-04-11-Agenda.md
│   └── 2018-05/
│       └── 2018-05-14-Agenda.md
```

Folders are named `YYYY-MM` format while files retain the full `YYYY-MM-DD` date.

## Future Considerations

- Consider adding meeting type filters (Regular, Special, Emergency)
- Might add search highlighting specific to meeting content
- Could integrate meeting video links when available
- Could add meeting attendance information

## Related Documentation

- [Navigation Architecture](./navigation-architecture.md)
- [Build Architecture](./build-architecture.md)
- [Airtable Integration](./airtable-integration.md)