# Airtable Sync Commands

## Setup Commands

Based on the sync script analysis, here are the MCP commands to run:

### Step 1: Check Ordinances/Resolutions (Test with 1 record)
```
council_ordinances_list maxRecords:1
```

### Step 2: Check Existing Public Metadata
```
council_public_metadata_list maxRecords:200
```

### Step 3: Create Public Metadata Record (if needed)

For Resolution No. 259-2018 (example):
```
council_public_metadata_create fields:{"Document":"recOrd259","Publication Status":"Draft","Digitization Notes":"","Public Tags":""}
```

## What the Script Does

1. **Scans Repository**: Found 22 mappable documents
2. **Matches to Airtable**: Links documents like "Resolution No. 259-2018" to files like `Resolutions/2018-Res-#259-Planning-Development-Fees.md`
3. **Creates Metadata Records**: For each matched document without metadata, creates a Public Metadata record

## Test Modes

- `--dry-run`: Shows what would be created without making changes
- `--test-single`: Process only 1 record for testing
- `--test-limit N`: Process N records for testing
- `--setup`: Run in setup mode to create Public Metadata records

## Next Steps

1. Run `node airtable-sync.js --setup --test-single --dry-run` to see what would happen
2. When ready, run without `--dry-run` to actually create the records
3. The script will output the exact MCP commands needed