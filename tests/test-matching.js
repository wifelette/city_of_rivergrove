#!/usr/bin/env node
/**
 * Test document matching between repo and Airtable
 */

const fs = require('fs');
const path = require('path');
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
const ORDINANCES_TABLE = 'Ordinances and Resolutions';

/**
 * Make a request to Airtable API
 */
function airtableRequest(path) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.airtable.com',
      port: 443,
      path: `/v0/${AIRTABLE_BASE_ID}${path}`,
      method: 'GET',
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
          resolve(JSON.parse(body));
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.end();
  });
}

/**
 * Extract document number from various formats
 */
function extractDocNumber(text) {
  // Match patterns like: #88-2017, #74-2004, #259-2018, #72
  const match = text.match(/#(\d+)(?:-(\d+))?/);
  if (match) {
    return {
      number: match[1],
      year: match[2] || null
    };
  }
  return null;
}

/**
 * Find repository files
 */
function findRepoFiles() {
  const files = [];
  const dirs = ['Ordinances', 'Resolutions'];
  
  for (const dir of dirs) {
    if (!fs.existsSync(dir)) continue;
    
    const dirFiles = fs.readdirSync(dir).filter(f => f.endsWith('.md'));
    
    for (const file of dirFiles) {
      const filepath = path.join(dir, file);
      
      // Extract info from filename
      let type = null;
      let number = null;
      let year = null;
      
      if (/^(\d{4})-Ord-#?(\d+)-/.test(file)) {
        const match = file.match(/^(\d{4})-Ord-#?(\d+)-/);
        type = 'Ordinance';
        year = match[1];
        number = match[2];
      } else if (/^(\d{4})-Res-#?(\d+)-/.test(file)) {
        const match = file.match(/^(\d{4})-Res-#?(\d+)-/);
        type = 'Resolution';
        year = match[1];
        number = match[2];
      }
      
      if (type && number) {
        files.push({
          file: filepath,
          type,
          number,
          year
        });
      }
    }
  }
  
  return files;
}

async function testMatching() {
  console.log('🔄 Testing document matching...\n');
  
  // Get Airtable records
  console.log('📋 Fetching Airtable records...');
  const response = await airtableRequest(`/${encodeURIComponent(ORDINANCES_TABLE)}?maxRecords=20`);
  const airtableRecords = response.records;
  
  // Get repo files
  console.log('📂 Scanning repository files...');
  const repoFiles = findRepoFiles();
  
  console.log(`\nFound ${airtableRecords.length} Airtable records`);
  console.log(`Found ${repoFiles.length} repository files\n`);
  
  // Create matches
  console.log('🔗 Matching documents:\n');
  console.log('='.repeat(80));
  
  for (const record of airtableRecords) {
    const airtableId = record.fields.ID;
    const recordId = record.id;
    
    // Extract document info from Airtable ID
    const docInfo = extractDocNumber(airtableId);
    
    if (!docInfo) {
      console.log(`❓ Cannot parse: ${airtableId}`);
      continue;
    }
    
    // Find matching repo file
    const isOrdinance = airtableId.toLowerCase().includes('ordinance');
    const isResolution = airtableId.toLowerCase().includes('resolution');
    
    const matches = repoFiles.filter(f => {
      // Match by number
      if (f.number !== docInfo.number) return false;
      
      // Match by type
      if (isOrdinance && f.type !== 'Ordinance') return false;
      if (isResolution && f.type !== 'Resolution') return false;
      
      // If Airtable has year, try to match it
      if (docInfo.year && f.year !== docInfo.year) return false;
      
      return true;
    });
    
    if (matches.length === 1) {
      console.log(`✅ MATCHED: "${airtableId}" (${recordId})`);
      console.log(`   → ${matches[0].file}`);
    } else if (matches.length > 1) {
      console.log(`⚠️  MULTIPLE: "${airtableId}" (${recordId})`);
      matches.forEach(m => console.log(`   → ${m.file}`));
    } else {
      console.log(`❌ NO MATCH: "${airtableId}" (${recordId})`);
    }
    console.log('');
  }
  
  // Show unmatched repo files
  console.log('='.repeat(80));
  console.log('\n📄 Repository files without Airtable matches:\n');
  
  for (const repoFile of repoFiles) {
    const hasMatch = airtableRecords.some(record => {
      const docInfo = extractDocNumber(record.fields.ID);
      if (!docInfo) return false;
      
      const isOrdinance = record.fields.ID.toLowerCase().includes('ordinance');
      const isResolution = record.fields.ID.toLowerCase().includes('resolution');
      
      if (repoFile.number !== docInfo.number) return false;
      if (isOrdinance && repoFile.type !== 'Ordinance') return false;
      if (isResolution && repoFile.type !== 'Resolution') return false;
      
      return true;
    });
    
    if (!hasMatch) {
      console.log(`  - ${repoFile.type} #${repoFile.number}-${repoFile.year}: ${repoFile.file}`);
    }
  }
}

testMatching().catch(console.error);