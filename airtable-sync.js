#!/usr/bin/env node
/**
 * Airtable to Repository Sync Script
 * Syncs public metadata from Airtable to the document repository
 */

const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  // File patterns for matching
  patterns: {
    ordinance: /^(\d{4})-Ord-#?(\d+)-(.+)\.md$/,
    resolution: /^(\d{4})-Res-#?(\d+)-(.+)\.md$/,
    interpretation: /^(\d{4}-\d{2}-\d{2})-RE-(.+)\.md$/
  },
  
  // Directories to scan
  sourceDirs: ['Ordinances', 'Resolutions', 'Interpretations', 'Other'],
  
  // Output directory for metadata
  metadataDir: 'metadata'
};

/**
 * Find repository files that match Airtable document IDs
 */
function findMatchingRepoFiles() {
  const files = new Map(); // docId -> filepath
  
  for (const dir of CONFIG.sourceDirs) {
    if (!fs.existsSync(dir)) continue;
    
    const dirFiles = fs.readdirSync(dir).filter(f => f.endsWith('.md'));
    
    for (const file of dirFiles) {
      const filepath = path.join(dir, file);
      
      // Try to extract document ID for matching
      let docId = null;
      
      if (CONFIG.patterns.ordinance.test(file)) {
        const match = file.match(CONFIG.patterns.ordinance);
        docId = `Ordinance No. ${match[2]}-${match[1]}`;
      } else if (CONFIG.patterns.resolution.test(file)) {
        const match = file.match(CONFIG.patterns.resolution);
        docId = `Resolution No. ${match[2]}-${match[1]}`;
      }
      // Add more patterns as needed
      
      if (docId) {
        files.set(docId, filepath);
        console.log(`📄 Mapped: "${docId}" -> ${filepath}`);
      } else {
        console.log(`❓ Could not map: ${file}`);
      }
    }
  }
  
  return files;
}

/**
 * Generate metadata file for a document
 */
function generateMetadataFile(record, repoFile) {
  const metadata = {
    document_id: record.documentId,
    repo_file: repoFile,
    publication_status: record.publicationStatus,
    digitization_notes: record.digitizationNotes,
    public_tags: record.publicTags || [],
    last_updated: record.lastUpdated,
    synced_at: new Date().toISOString()
  };
  
  return metadata;
}

/**
 * Create a Public Metadata record for a document that doesn't have one
 */
async function createPublicMetadataRecord(documentId, dryRun = false) {
  console.log(`📝 Creating Public Metadata record for: ${documentId}`);
  
  if (dryRun) {
    console.log('  Would create record with:');
    console.log('  - Document: Link to Ordinances and Resolutions record');
    console.log('  - Publication Status: Draft');
    console.log('  - Digitization Notes: (empty)');
    console.log('  - Public Tags: (empty)');
    return { id: 'mock-id', created: true };
  }
  
  // TODO: Replace with actual MCP API call:
  // const result = await mcpClient.call('council_public_metadata_create', {
  //   fields: {
  //     'Document': [documentId], // Link to the Ordinances record
  //     'Publication Status': 'Draft',
  //     'Digitization Notes': '',
  //     'Public Tags': []
  //   }
  // });
  
  console.log('⚠️  Dry run mode - no actual record created');
  return { id: 'mock-id', created: false };
}

/**
 * Get all Ordinances and Resolutions that exist in the repo
 */
async function getOrdinancesAndResolutions(testMode = null, testLimit = null) {
  console.log('📋 Fetching Ordinances and Resolutions from Airtable...');
  
  // TODO: Replace with actual MCP API call:
  // const result = await mcpClient.call('council_ordinances_list', {
  //   maxRecords: testLimit || 100
  // });
  
  // For now, return mock data based on what we found in repo
  const mockData = [
    { id: 'recOrd259', fields: { 'ID': 'Resolution No. 259-2018' } },
    { id: 'recOrd72', fields: { 'ID': 'Resolution No. 72-1984' } },
    { id: 'recOrd22', fields: { 'ID': 'Resolution No. 22-1976' } }
  ];
  
  if (testMode === 'single') {
    return mockData.slice(0, 1);
  } else if (testLimit) {
    return mockData.slice(0, testLimit);
  }
  
  return mockData;
}

/**
 * Fetch existing Public Metadata records
 */
async function getExistingPublicMetadata() {
  console.log('🔍 Checking existing Public Metadata records...');
  
  // TODO: Replace with actual MCP API call:
  // const result = await mcpClient.call('council_public_metadata_list', {});
  
  // For now, return empty array (no existing records)
  return [];
}

/**
 * Setup mode: Create Public Metadata records for documents that don't have them
 */
async function setupPublicMetadata(options = {}) {
  const { dryRun = false, testMode = null, testLimit = null } = options;
  
  console.log('🚀 Setting up Public Metadata records...');
  console.log(`Mode: ${dryRun ? 'DRY RUN' : 'LIVE'} ${testMode ? `(${testMode})` : ''} ${testLimit ? `(limit: ${testLimit})` : ''}`);
  
  // Step 1: Get all ordinances and resolutions
  const ordinanceRecords = await getOrdinancesAndResolutions(testMode, testLimit);
  console.log(`Found ${ordinanceRecords.length} ordinance/resolution records`);
  
  // Step 2: Get existing public metadata
  const existingMetadata = await getExistingPublicMetadata();
  const existingDocIds = new Set(existingMetadata.map(record => record.documentId));
  console.log(`Found ${existingMetadata.length} existing Public Metadata records`);
  
  // Step 3: Find repository files
  console.log('\n📂 Scanning repository files...');
  const repoFiles = findMatchingRepoFiles();
  
  // Step 4: Create metadata records for documents that exist in both Airtable and repo
  const toCreate = [];
  for (const ordRecord of ordinanceRecords) {
    const docId = ordRecord.fields.ID;
    
    if (!existingDocIds.has(docId) && repoFiles.has(docId)) {
      toCreate.push({ docId, airtableId: ordRecord.id, repoFile: repoFiles.get(docId) });
      console.log(`✅ Will create metadata for: ${docId} (${repoFiles.get(docId)})`);
    } else if (!repoFiles.has(docId)) {
      console.log(`❓ Skipping ${docId} - no repo file found`);
    } else if (existingDocIds.has(docId)) {
      console.log(`➡️  Skipping ${docId} - metadata already exists`);
    }
  }
  
  // Step 5: Create the records
  console.log(`\n📝 Creating ${toCreate.length} Public Metadata records...`);
  for (const { docId, airtableId, repoFile } of toCreate) {
    const result = await createPublicMetadataRecord(docId, dryRun);
    if (result.created) {
      console.log(`✓ Created metadata record for ${docId}`);
    }
  }
  
  console.log('\n📊 Setup Summary:');
  console.log(`  📋 Ordinance records: ${ordinanceRecords.length}`);
  console.log(`  📄 Repo files: ${repoFiles.size}`);
  console.log(`  ✅ Already have metadata: ${existingMetadata.length}`);
  console.log(`  📝 Created new records: ${toCreate.length}`);
}

/**
 * Main sync function
 */
async function syncMetadata(options = {}) {
  const { dryRun = false, testMode = null, testLimit = null } = options;
  
  console.log('🔄 Starting Airtable sync...');
  console.log(`Mode: ${dryRun ? 'DRY RUN' : 'LIVE'} ${testMode ? `(${testMode})` : ''} ${testLimit ? `(limit: ${testLimit})` : ''}`);
  
  // Step 1: Find repository files
  console.log('\n📂 Scanning repository files...');
  const repoFiles = findMatchingRepoFiles();
  console.log(`Found ${repoFiles.size} mappable files`);
  
  // Step 2: Get Airtable data
  console.log('\n📊 Fetching Airtable data...');
  const airtableRecords = await getAirtableData(testMode, testLimit);
  console.log(`Found ${airtableRecords.length} published records`);
  
  // Step 3: Match and generate metadata
  console.log('\n🔗 Matching records to files...');
  const matched = [];
  const unmatched = [];
  
  for (const record of airtableRecords) {
    const repoFile = repoFiles.get(record.documentId);
    
    if (repoFile) {
      matched.push({ record, repoFile });
      console.log(`✅ Matched: ${record.documentId} -> ${repoFile}`);
    } else {
      unmatched.push(record);
      console.log(`❌ No repo file for: ${record.documentId}`);
    }
  }
  
  // Step 4: Generate metadata files
  if (matched.length > 0) {
    console.log(`\n📝 Generating metadata for ${matched.length} documents...`);
    
    if (!dryRun) {
      // Create metadata directory
      if (!fs.existsSync(CONFIG.metadataDir)) {
        fs.mkdirSync(CONFIG.metadataDir, { recursive: true });
      }
    }
    
    for (const { record, repoFile } of matched) {
      const metadata = generateMetadataFile(record, repoFile);
      const metadataFile = path.join(CONFIG.metadataDir, `${record.id}.json`);
      
      if (dryRun) {
        console.log(`Would write: ${metadataFile}`);
        console.log(JSON.stringify(metadata, null, 2));
      } else {
        fs.writeFileSync(metadataFile, JSON.stringify(metadata, null, 2));
        console.log(`✓ Generated: ${metadataFile}`);
      }
    }
  }
  
  // Summary
  console.log('\n📊 Sync Summary:');
  console.log(`  ✅ Matched: ${matched.length}`);
  console.log(`  ❌ Unmatched: ${unmatched.length}`);
  console.log(`  📂 Repo files: ${repoFiles.size}`);
  console.log(`  📊 Airtable records: ${airtableRecords.length}`);
  
  if (unmatched.length > 0) {
    console.log('\n❗ Unmatched records:');
    unmatched.forEach(r => console.log(`  - ${r.documentId}`));
  }
}

// CLI handling
if (require.main === module) {
  const args = process.argv.slice(2);
  const options = {};
  
  if (args.includes('--dry-run')) options.dryRun = true;
  if (args.includes('--test-single')) options.testMode = 'single';
  if (args.includes('--test-limit')) {
    const limitIndex = args.indexOf('--test-limit');
    options.testLimit = parseInt(args[limitIndex + 1]) || 2;
  }
  
  if (args.includes('--setup')) {
    setupPublicMetadata(options).catch(console.error);
  } else {
    syncMetadata(options).catch(console.error);
  }
}

module.exports = { syncMetadata, findMatchingRepoFiles };