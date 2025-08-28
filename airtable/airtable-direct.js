#!/usr/bin/env node
/**
 * Direct Airtable API access for testing
 */

const https = require('https');
require('dotenv').config();

// Airtable configuration
const AIRTABLE_API_KEY = process.env.AIRTABLE_API_KEY;
const AIRTABLE_BASE_ID = process.env.AIRTABLE_BASE_ID || 'appnsWognX10X9TDL'; // Council base

// Validate required environment variables
if (!AIRTABLE_API_KEY) {
  console.error('Error: AIRTABLE_API_KEY environment variable is required');
  console.error('Please create a .env file with your Airtable API key');
  process.exit(1);
}
const ORDINANCES_TABLE = 'Ordinances and Resolutions';
const METADATA_TABLE = 'tblySudmnPUjrJQwE'; // Public Metadata table

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
 * List ordinances and resolutions
 */
async function listOrdinances(maxRecords = 3) {
  console.log(`\n📋 Fetching Ordinances and Resolutions (max: ${maxRecords})...`);
  
  const response = await airtableRequest('GET', `/${encodeURIComponent(ORDINANCES_TABLE)}?maxRecords=${maxRecords}`);
  
  console.log(`Found ${response.records.length} records:`);
  response.records.forEach(record => {
    console.log(`  - ${record.fields.ID} (${record.id})`);
    if (record.fields.Summary) {
      console.log(`    Summary: ${record.fields.Summary.substring(0, 50)}...`);
    }
  });
  
  return response.records;
}

/**
 * List existing Public Metadata records
 */
async function listPublicMetadata(maxRecords = 5) {
  console.log(`\n🔍 Fetching Public Metadata records (max: ${maxRecords})...`);
  
  const response = await airtableRequest('GET', `/${METADATA_TABLE}?maxRecords=${maxRecords}`);
  
  console.log(`Found ${response.records.length} records:`);
  response.records.forEach(record => {
    console.log(`  - ${record.fields['Document Display Name'] || 'Unnamed'} (${record.id})`);
    if (record.fields['Publication Status']) {
      console.log(`    Status: ${record.fields['Publication Status']}`);
    }
  });
  
  return response.records;
}

/**
 * Search for a specific ordinance
 */
async function searchOrdinance(searchTerm) {
  console.log(`\n🔎 Searching for ordinance: "${searchTerm}"...`);
  
  const filterFormula = `SEARCH("${searchTerm}", {ID})`;
  const response = await airtableRequest('GET', 
    `/${encodeURIComponent(ORDINANCES_TABLE)}?filterByFormula=${encodeURIComponent(filterFormula)}&maxRecords=5`
  );
  
  console.log(`Found ${response.records.length} matching records:`);
  response.records.forEach(record => {
    console.log(`  - ${record.fields.ID} (${record.id})`);
  });
  
  return response.records;
}

/**
 * Create a Public Metadata record
 */
async function createPublicMetadata(documentRecordId, dryRun = true) {
  console.log(`\n📝 Creating Public Metadata record...`);
  
  if (dryRun) {
    console.log('DRY RUN - Would create record with:');
    console.log(`  - Document: [${documentRecordId}]`);
    console.log('  - Publication Status: Draft');
    console.log('  - Digitization Notes: (empty)');
    console.log('  - Public Tags: (empty)');
    return null;
  }
  
  const data = {
    fields: {
      'Document': [documentRecordId],
      'Publication Status': 'Draft',
      'Digitization Notes': '',
      'Public Tags': []
    }
  };
  
  const response = await airtableRequest('POST', `/${METADATA_TABLE}`, data);
  console.log(`✅ Created record: ${response.id}`);
  console.log(`   Display Name: ${response.fields['Document Display Name']}`);
  
  return response;
}

/**
 * Main test function
 */
async function runTests() {
  try {
    console.log('🧪 Testing Direct Airtable API Access\n');
    console.log('=' .repeat(50));
    
    // Test 1: List a few ordinances
    const ordinances = await listOrdinances(3);
    
    // Test 2: Check existing metadata
    const metadata = await listPublicMetadata(5);
    
    // Test 3: Search for Resolution 259-2018
    const search259 = await searchOrdinance('259-2018');
    
    // Test 4: Show what we would create
    if (search259.length > 0) {
      console.log('\n' + '='.repeat(50));
      console.log('📊 Ready to create Public Metadata for Resolution 259-2018');
      await createPublicMetadata(search259[0].id, true); // Dry run
      
      console.log('\n💡 To actually create the record, run:');
      console.log('   node airtable-direct.js --create-for-259');
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

// Handle command line arguments
if (process.argv.includes('--create-for-259')) {
  // Actually create the record for 259-2018
  searchOrdinance('259-2018').then(records => {
    if (records.length > 0) {
      return createPublicMetadata(records[0].id, false); // Not a dry run
    } else {
      console.log('❌ Could not find Resolution 259-2018');
    }
  }).catch(console.error);
} else {
  // Run tests
  runTests();
}