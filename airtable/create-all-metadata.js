#!/usr/bin/env node
/**
 * Create all Public Metadata records for matched documents
 */

const fs = require('fs');
const https = require('https');
require('dotenv').config();

// Airtable configuration
const AIRTABLE_API_KEY = process.env.AIRTABLE_API_KEY;
const AIRTABLE_BASE_ID = process.env.AIRTABLE_BASE_ID || 'appnsWognX10X9TDL';

// Validate required environment variables
if (!AIRTABLE_API_KEY) {
  console.error('Error: AIRTABLE_API_KEY environment variable is required');
  console.error('Please create a .env file with your Airtable API key');
  process.exit(1);
}
const METADATA_TABLE = 'tblySudmnPUjrJQwE';

/**
 * Make Airtable API request
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
 * Check existing Public Metadata records
 */
async function getExistingMetadata() {
  console.log('🔍 Checking existing Public Metadata records...');
  const response = await airtableRequest('GET', `/${METADATA_TABLE}?maxRecords=200`);
  
  // Create a set of document IDs that already have metadata
  const existingDocs = new Set();
  response.records.forEach(record => {
    if (record.fields['Document'] && record.fields['Document'][0]) {
      existingDocs.add(record.fields['Document'][0]);
    }
  });
  
  console.log(`Found ${response.records.length} existing metadata records`);
  return existingDocs;
}

/**
 * Create a Public Metadata record
 */
async function createMetadataRecord(airtableId, name) {
  const data = {
    fields: {
      'Document': [airtableId],
      'Publication Status': 'Draft',
      'Digitization Notes': '',
      'Public Tags': []
    }
  };
  
  try {
    const response = await airtableRequest('POST', `/${METADATA_TABLE}`, data);
    console.log(`✅ Created: ${name} (${response.id})`);
    return { success: true, id: response.id };
  } catch (error) {
    console.error(`❌ Failed: ${name} - ${error.message}`);
    return { success: false, error: error.message };
  }
}

/**
 * Main function to create all metadata records
 */
async function createAllMetadata() {
  console.log('📚 Creating Public Metadata Records\n');
  console.log('='.repeat(60));
  
  // Load matches
  if (!fs.existsSync('matches.json')) {
    console.error('❌ matches.json not found. Run match-all-documents.js first.');
    return;
  }
  
  const matches = JSON.parse(fs.readFileSync('matches.json', 'utf8'));
  console.log(`\n📊 Found ${matches.length} matched documents\n`);
  
  // Get existing metadata
  const existingDocs = await getExistingMetadata();
  
  // Filter to documents that need metadata
  const toCreate = matches.filter(m => !existingDocs.has(m.airtableId));
  
  if (toCreate.length === 0) {
    console.log('✨ All matched documents already have metadata records!');
    return;
  }
  
  console.log(`\n📝 Creating ${toCreate.length} new metadata records...\n`);
  
  // Create records with a small delay between each to avoid rate limits
  let created = 0;
  let failed = 0;
  
  for (let i = 0; i < toCreate.length; i++) {
    const match = toCreate[i];
    const result = await createMetadataRecord(match.airtableId, match.airtableName);
    
    if (result.success) {
      created++;
    } else {
      failed++;
    }
    
    // Small delay to avoid rate limits (Airtable allows 5 requests per second)
    if (i < toCreate.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 250)); // 4 per second to be safe
    }
  }
  
  // Summary
  console.log('\n' + '='.repeat(60));
  console.log('\n📊 Summary:');
  console.log(`  Total matched documents: ${matches.length}`);
  console.log(`  Already had metadata: ${matches.length - toCreate.length}`);
  console.log(`  Successfully created: ${created}`);
  if (failed > 0) {
    console.log(`  Failed: ${failed}`);
  }
  console.log('\n✅ Done!');
}

// Run
createAllMetadata().catch(console.error);