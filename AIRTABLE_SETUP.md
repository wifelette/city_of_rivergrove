# Airtable Integration Setup

This repository includes scripts that sync document metadata with Airtable. These scripts help maintain consistency between the documents in this repository and their metadata in Airtable.

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Airtable API key:
   ```
   AIRTABLE_API_KEY=your_actual_api_key_here
   AIRTABLE_BASE_ID=appnsWognX10X9TDL
   ```

### 3. Getting Your Airtable API Key

1. Go to [Airtable Account Settings](https://airtable.com/create/tokens)
2. Create a new personal access token
3. Give it a descriptive name like "City of Rivergrove Document Sync"
4. Grant it the following scopes:
   - `data.records:read` - To read document records
   - `data.records:write` - To update metadata
   - `schema.bases:read` - To read base structure
5. Add the specific base (City Council base) to the token's access list
6. Copy the generated token and add it to your `.env` file

## Available Scripts

### `node airtable-sync-api.js`
Main sync script that updates public metadata in Airtable based on documents in the repository.

### `node match-all-documents.js`
Matches documents in the repository with their corresponding records in Airtable.

### `node create-all-metadata.js`
Creates new metadata records for matched documents.

### `node airtable-direct.js`
Direct API access for testing and debugging Airtable connections.

### `node test-matching.js`
Tests the document matching logic without making any changes.

## Security Notes

- **NEVER commit your `.env` file** - It contains sensitive API keys
- The `.gitignore` file is configured to exclude `.env` files
- If you accidentally commit an API key, regenerate it immediately in Airtable
- Use environment variables for all sensitive configuration

## Troubleshooting

### "AIRTABLE_API_KEY environment variable is required" error
- Make sure you've created a `.env` file with your API key
- Verify the `.env` file is in the root directory of this repository
- Check that your API key is valid and has the correct permissions

### Connection errors
- Verify your API key has access to the base ID specified
- Check that your internet connection is working
- Ensure the Airtable API is not experiencing downtime

## Base Information

- **Base ID**: `appnsWognX10X9TDL` (City Council base)
- **Tables Used**:
  - `Ordinances and Resolutions` - Main document records
  - `Public Metadata` (tblySudmnPUjrJQwE) - Public-facing metadata