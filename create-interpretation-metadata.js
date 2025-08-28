#!/usr/bin/env node
/**
 * Create Public Metadata entries for Interpretations with correct mappings
 */

const fs = require('fs');
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
 * CORRECTED Interpretation mappings based on file content analysis
 */
const INTERPRETATION_MAPPINGS = [
  // These are confirmed matches
  { airtableName: "Interpretation of 2.040(h)", file: "1997-07-07-RE-2.040h-permitting-adus.md" },
  { airtableName: "Interpretation of 9.030 #1", file: "1997-09-08-RE-9.030-permit-fees-and-completeness.md" },
  { airtableName: "Interpretation of 9.030 #2", file: "1997-11-03-RE-9.030-permit-fees-and-completeness.md" },
  { airtableName: "Interpretation of 5.080 #1", file: "1998-03-02-RE-5.080-setbacks.md" },
  { airtableName: "Interpretation of 5.080 #2", file: "1998-06-01-RE-5.080-setback-orientation.md" },
  { airtableName: "Interpretation of 5.080 #3", file: "1998-07-06-RE-5.080-setback-orientation.md" },
  { airtableName: "Interpretation of 5.080 #4", file: "2004-10-11-RE-5.080-setbacks.md" },
  { airtableName: "Interpretation of 5.2-4", file: "2001-05-07-RE-balanced-cut-and-fill.md" },
  
  // These are the corrected mappings based on file content
  { airtableName: "Interpretation of 5.010 #1", file: "2002-08-05-RE-lots-partially-in-floodplain.md" },
  { airtableName: "Interpretation of 5.010 #2", file: "2002-09-05-RE-duplicate.md" },
  { airtableName: "Interpretation of ORD 68-2000", file: "2008-02-04-RE-multi-family.md" },
  { airtableName: "Interpretation of 4.020", file: "2005-04-04-RE-adu-sewer.md" },
];

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
 * Get all Interpretation records from Airtable
 */
async function getInterpretations() {
  console.log('📊 Fetching Interpretation records from Airtable...');
  const response = await airtableRequest('GET', `/Ordinances%20and%20Resolutions?filterByFormula=${encodeURIComponent("SEARCH('Interpretation', {ID})")}`);
  
  const interpretations = {};
  response.records.forEach(record => {
    interpretations[record.fields.ID] = record.id;
  });
  
  console.log(`Found ${Object.keys(interpretations).length} Interpretations`);
  return interpretations;
}

/**
 * Check existing Public Metadata
 */
async function getExistingMetadata() {
  console.log('🔍 Checking existing Public Metadata...');
  const response = await airtableRequest('GET', `/${METADATA_TABLE}?maxRecords=200`);
  
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
      'Publication Status': 'Published',
      'Digitization Notes': '',
      'Public Tags': []
    }
  };
  
  try {
    const response = await airtableRequest('POST', `/${METADATA_TABLE}`, data);
    console.log(`✅ Created metadata for: ${name}`);
    return { success: true, id: response.id };
  } catch (error) {
    console.error(`❌ Failed to create metadata for ${name}:`, error.message);
    return { success: false, error: error.message };
  }
}

/**
 * Main process
 */
async function main() {
  console.log('📚 Creating Public Metadata for Interpretations\n');
  console.log('='.repeat(60));
  
  // Get Airtable data
  const interpretations = await getInterpretations();
  const existingMetadata = await getExistingMetadata();
  
  // Check each interpretation
  console.log('\n📝 Checking Interpretations for metadata:\n');
  
  const toCreate = [];
  
  for (const mapping of INTERPRETATION_MAPPINGS) {
    const airtableId = interpretations[mapping.airtableName];
    
    if (!airtableId) {
      console.log(`⚠️  Not found in Airtable: ${mapping.airtableName}`);
      continue;
    }
    
    if (existingMetadata.has(airtableId)) {
      console.log(`✓ Already has metadata: ${mapping.airtableName}`);
    } else {
      console.log(`❌ Missing metadata: ${mapping.airtableName}`);
      toCreate.push({ id: airtableId, name: mapping.airtableName });
    }
  }
  
  // Create missing metadata
  if (toCreate.length > 0) {
    console.log('\n' + '='.repeat(60));
    console.log(`\n📝 Creating ${toCreate.length} new metadata records...\n`);
    
    for (const item of toCreate) {
      await createMetadataRecord(item.id, item.name);
      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 200));
    }
  } else {
    console.log('\n✅ All Interpretations already have Public Metadata!');
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('\n✅ Done!');
}

main().catch(console.error);