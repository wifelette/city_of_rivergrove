# Meeting Documents Navigation

## Overview

Meeting documents (Agendas, Minutes, and Transcripts) have a specialized navigation interface that differs from other document types in the City of Rivergrove digital archive.

## Key Differences from Other Document Types

### 1. No View Options
Unlike Ordinances, Resolutions, and Interpretations which offer multiple view options (Numerical, Chronological, Topical), meeting documents have no view selection controls. The view controls are completely hidden when viewing meeting documents.

### 2. Date-Based Grouping
Meeting documents are always organized by meeting date. Each meeting date becomes a group header (e.g., "February 12, 2024") with all documents from that meeting listed beneath it.

### 3. Document Type Ordering
Within each meeting date group, documents are displayed in a consistent order:
1. Agenda (if available)
2. Minutes (if available)  
3. Transcript (if available)

### 4. No Individual Dates
Since documents are already grouped by meeting date, individual document items only show their type (Agenda, Minutes, Transcript) without repeating the date.

### 5. Sort Controls
The main sort arrows (↑↓) remain available and control the ordering of the date groups:
- Ascending (↑): Oldest meetings first
- Descending (↓): Newest meetings first

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
   - Groups documents by date
   - Formats dates in readable format (e.g., "February 12, 2024")
   - Sorts documents within each group by type

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

## Future Considerations

- Consider adding meeting type filters (Regular, Special, Emergency)
- Could add year grouping for better organization as archive grows
- Might add search highlighting specific to meeting content
- Could integrate meeting video links when available

## Related Documentation

- [Navigation Architecture](./navigation-architecture.md)
- [Build Architecture](./build-architecture.md)
- [Airtable Integration](./airtable-integration.md)