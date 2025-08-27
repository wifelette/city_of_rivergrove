#!/usr/bin/env node
/**
 * Airtable to Repository Sync Script - Direct API Version
 * Syncs public metadata from Airtable to the document repository
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// Airtable configuration
const AIRTABLE_API_KEY = 'patmTIQyJmTtUfekh.75221e3bd677984018782065e3b2a5d696fbd2a07f7233b7c71435b7d789a250';
const AIRTABLE_BASE_ID = 'appnsWognX10X9TDL';
const ORDINANCES_TABLE = 'Ordinances and Resolutions';
const METADATA_TABLE = 'tblySudmnPUjrJQwE';

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
 * Make a request to Airtable API
 */
function airtableRequest(method, path, data = null) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.airtable.com',
      port: 443,
      path: `/v0/${AIRTABLE_BASE_ID}${path}`,
      method: method,
      headers: {
        'Authorization': `Bearer ${AIRTABLE_API_KEY}`,
        'Content-Type': 'application/json'
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => body += chunk);
      res.on('end', () => {
        try {
          const response = JSON.parse(body);
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(response);
          } else {
            reject(new Error(`Airtable API error: ${response.error?.message || body}`));
          }
        } catch (e) {
          reject(new Error(`Failed to parse response: ${body}`));
        }
      });
    });

    req.on('error', reject);
    
    if (data) {
      req.write(JSON.stringify(data));
    }
    
    req.end();
  });
}

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
        // Try different formats that might match Airtable
        const possibilities = [
          `Ordinance #${match[2]}-${match[1]}`,
          `Ordinance #${match[2]}`,
          `Ordinance ${match[2]}-${match[1]}`
        ];
        docId = possibilities[0]; // Use the most likely format
      } else if (CONFIG.patterns.resolution.test(file)) {
        const match = file.match(CONFIG.patterns.resolution);
        // Try different formats that might match Airtable
        const possibilities = [
          `Resolution #${match[2]}-${match[1]}`,
          `Resolution #${match[2]}`,
          `Resolution ${match[2]}-${match[1]}`
        ];
        docId = possibilities[0]; // Use the most likely format
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
 * Get all Ordinances and Resolutions from Airtable
 */
async function getOrdinancesAndResolutions(maxRecords = 100) {
  console.log('📋 Fetching Ordinances and Resolutions from Airtable...');
  
  const response = await airtableRequest('GET', 
    `/${encodeURIComponent(ORDINANCES_TABLE)}?maxRecords=${maxRecords}`
  );
  
  console.log(`Found ${response.records.length} ordinance/resolution records`);
  return response.records;
}

/**
 * Get existing Public Metadata records
 */
async function getExistingPublicMetadata() {
  console.log('🔍 Checking existing Public Metadata records...');
  
  const response = await airtableRequest('GET', `/${METADATA_TABLE}?maxRecords=200`);
  
  console.log(`Found ${response.records.length} existing Public Metadata records`);
  
  // Create a set of document IDs that already have metadata
  const existingDocs = new Set();
  response.records.forEach(record => {
    if (record.fields['Document'] && record.fields['Document'][0]) {
      existingDocs.add(record.fields['Document'][0]);
    }
  });
  
  return existingDocs;
}

/**
 * Create a Public Metadata record
 */
async function createPublicMetadata(documentRecordId, documentName, dryRun = false) {
  console.log(`📝 Creating Public Metadata record for: ${documentName}`);
  
  if (dryRun) {
    console.log(`  Would create record with:`);
    console.log(`  - Document: Link to record ${documentRecordId}`);
    console.log(`  - Publication Status: Draft`);
    console.log(`  - Digitization Notes: (empty)`);
    console.log(`  - Public Tags: (empty)`);
    return { created: true };
  }
  
  const data = {
    fields: {
      'Document': [documentRecordId],
      'Publication Status': 'Draft',
      'Digitization Notes': '',
      'Public Tags': []
    }
  };
  
  try {
    const response = await airtableRequest('POST', `/${METADATA_TABLE}`, data);
    console.log(`✅ Created record: ${response.id}`);
    return { created: true, id: response.id };
  } catch (error) {
    console.error(`❌ Failed to create record: ${error.message}`);
    return { created: false, error: error.message };
  }
}

/**
 * Setup mode: Create Public Metadata records for documents that don't have them
 */
async function setupPublicMetadata(options = {}) {
  const { dryRun = false, testMode = null, testLimit = null } = options;
  
  console.log('🚀 Setting up Public Metadata records...');
  console.log(`Mode: ${dryRun ? 'DRY RUN' : 'LIVE'} ${testMode ? `(${testMode})` : ''} ${testLimit ? `(limit: ${testLimit})` : ''}`);
  
  try {
    // Step 1: Get all ordinances and resolutions
    const maxRecords = testLimit || (testMode === 'single' ? 1 : 100);
    const ordinanceRecords = await getOrdinancesAndResolutions(maxRecords);
    
    // Step 2: Get existing public metadata
    const existingDocIds = await getExistingPublicMetadata();
    
    // Step 3: Find repository files
    console.log('\n📂 Scanning repository files...');
    const repoFiles = findMatchingRepoFiles();
    
    // Step 4: Find documents that need metadata records
    const toCreate = [];
    for (const record of ordinanceRecords) {
      const docId = record.fields.ID;
      const recordId = record.id;
      
      // Check if this document already has metadata
      if (!existingDocIds.has(recordId)) {
        // Check if we have a matching repo file
        if (repoFiles.has(docId)) {
          toCreate.push({ 
            docId, 
            recordId, 
            repoFile: repoFiles.get(docId) 
          });
          console.log(`✅ Will create metadata for: ${docId} (${repoFiles.get(docId)})`);
        } else {
          console.log(`❓ Skipping ${docId} - no repo file found`);
        }
      } else {
        console.log(`➡️  Skipping ${docId} - metadata already exists`);
      }
    }
    
    // Step 5: Create the records
    if (toCreate.length > 0) {
      console.log(`\n📝 Creating ${toCreate.length} Public Metadata records...`);
      
      let created = 0;
      let failed = 0;
      
      for (const { docId, recordId, repoFile } of toCreate) {
        const result = await createPublicMetadata(recordId, docId, dryRun);
        if (result.created) {
          created++;
        } else {
          failed++;
        }
      }
      
      console.log(`\n✅ Created: ${created}`);
      if (failed > 0) {
        console.log(`❌ Failed: ${failed}`);
      }
    } else {
      console.log('\n✨ No new records to create!');
    }
    
    // Summary
    console.log('\n📊 Setup Summary:');
    console.log(`  📋 Ordinance records checked: ${ordinanceRecords.length}`);
    console.log(`  📄 Repo files found: ${repoFiles.size}`);
    console.log(`  ✅ Already have metadata: ${existingDocIds.size}`);
    console.log(`  📝 Records to create: ${toCreate.length}`);
    
  } catch (error) {
    console.error('❌ Error:', error.message);
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
  
  setupPublicMetadata(options).catch(console.error);
}

module.exports = { setupPublicMetadata, findMatchingRepoFiles };