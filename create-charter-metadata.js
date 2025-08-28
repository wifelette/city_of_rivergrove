#!/usr/bin/env node
/**
 * Create Public Metadata entry for City Charter
 */

const https = require('https');
require('dotenv').config();

// Airtable configuration
const AIRTABLE_API_KEY = process.env.AIRTABLE_API_KEY;
const AIRTABLE_BASE_ID = process.env.AIRTABLE_BASE_ID || 'appnsWognX10X9TDL';

if (!AIRTABLE_API_KEY) {
  console.error('Error: AIRTABLE_API_KEY environment variable is required');
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
 * Find City Charter in Airtable
 */
async function findCityCharter() {
  console.log('🔍 Searching for City Charter in Ordinances table...\n');
  
  // Search for records with Type = "Other" or name containing "Charter"
  const formulas = [
    "OR(SEARCH('Charter', {ID}), {Type} = 'Other')",
    "{ID} = 'City Charter'",
    "SEARCH('Charter', {Name})"
  ];
  
  for (const formula of formulas) {
    try {
      const response = await airtableRequest('GET', 
        `/Ordinances%20and%20Resolutions?filterByFormula=${encodeURIComponent(formula)}&maxRecords=10`
      );
      
      console.log(`Search with formula: ${formula}`);
      console.log(`Found ${response.records.length} record(s):\n`);
      
      if (response.records.length > 0) {
        response.records.forEach(record => {
          console.log(`  ID: ${record.id}`);
          console.log(`  Name/ID: ${record.fields.ID || record.fields.Name || 'N/A'}`);
          console.log(`  Type: ${record.fields.Type || 'N/A'}`);
          console.log(`  Year: ${record.fields.Year || 'N/A'}`);
          console.log(`  Digitized: ${record.fields.Digitized || false}`);
          console.log();
        });
        
        // Look for the Charter
        const charter = response.records.find(r => 
          r.fields.ID?.includes('Charter') || 
          r.fields.Name?.includes('Charter') ||
          (r.fields.Type === 'Other' && r.fields.Year === 1974)
        );
        
        if (charter) {
          return charter;
        }
      }
    } catch (error) {
      console.error(`Error with formula "${formula}":`, error.message);
    }
  }
  
  return null;
}

/**
 * Check if metadata already exists
 */
async function checkExistingMetadata(documentId) {
  const response = await airtableRequest('GET', 
    `/${METADATA_TABLE}?filterByFormula=${encodeURIComponent(`SEARCH('${documentId}', ARRAYJOIN({Document}))`)}`
  );
  
  return response.records.length > 0;
}

/**
 * Create Public Metadata record
 */
async function createMetadata(documentId, name) {
  const data = {
    fields: {
      'Document': [documentId],
      'Publication Status': 'Published',
      'Digitization Notes': 'City Charter - Foundational Document',
      'Public Tags': []
    }
  };
  
  const response = await airtableRequest('POST', `/${METADATA_TABLE}`, data);
  return response;
}

/**
 * Main process
 */
async function main() {
  console.log('📜 City Charter Public Metadata Creation\n');
  console.log('='.repeat(60) + '\n');
  
  // Find the Charter
  const charter = await findCityCharter();
  
  if (!charter) {
    console.log('❌ City Charter not found in Airtable!');
    console.log('\nPossible reasons:');
    console.log('  - It might be named differently');
    console.log('  - It might not have Type = "Other"');
    console.log('  - It might not be digitized yet');
    return;
  }
  
  console.log('='.repeat(60));
  console.log('\n✅ Found City Charter:');
  console.log(`  Record ID: ${charter.id}`);
  console.log(`  Name: ${charter.fields.ID || charter.fields.Name}`);
  console.log(`  Type: ${charter.fields.Type}`);
  
  // Check if metadata already exists
  console.log('\n🔍 Checking for existing metadata...');
  const hasMetadata = await checkExistingMetadata(charter.id);
  
  if (hasMetadata) {
    console.log('✅ City Charter already has Public Metadata!');
    return;
  }
  
  // Create metadata
  console.log('📝 Creating Public Metadata...');
  try {
    const result = await createMetadata(charter.id, charter.fields.ID || 'City Charter');
    console.log(`✅ Successfully created Public Metadata!`);
    console.log(`   Metadata Record ID: ${result.id}`);
  } catch (error) {
    console.error('❌ Failed to create metadata:', error.message);
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('\n✅ Done!');
}

main().catch(console.error);