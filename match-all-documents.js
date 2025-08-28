#!/usr/bin/env node
/**
 * Comprehensive document matching between repository and Airtable
 * Handles Ordinances, Resolutions, and Interpretations
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

/**
 * Fetch all Airtable records
 */
function fetchAirtableRecords() {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.airtable.com',
      path: `/v0/${AIRTABLE_BASE_ID}/Ordinances%20and%20Resolutions?maxRecords=100`,
      headers: {
        'Authorization': `Bearer ${AIRTABLE_API_KEY}`
      }
    };

    https.get(options, res => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const data = JSON.parse(body);
          resolve(data.records);
        } catch (e) {
          reject(e);
        }
      });
    }).on('error', reject);
  });
}

/**
 * Get all repository files
 */
function getRepoFiles() {
  const files = [];
  const dirs = ['Ordinances', 'Resolutions', 'Interpretations', 'Other'];
  
  dirs.forEach(dir => {
    if (!fs.existsSync(dir)) return;
    
    const dirFiles = fs.readdirSync(dir)
      .filter(f => f.endsWith('.md'))
      .map(f => ({
        path: path.join(dir, f),
        dir: dir,
        filename: f
      }));
    
    files.push(...dirFiles);
  });
  
  return files;
}

/**
 * Try to match an Airtable record to a repo file
 */
function findMatch(airtableRecord, repoFiles) {
  const airtableId = airtableRecord.fields.ID;
  if (!airtableId) return null;
  
  // Handle different document types
  const isOrdinance = airtableId.toLowerCase().includes('ordinance');
  const isResolution = airtableId.toLowerCase().includes('resolution');
  const isInterpretation = airtableId.toLowerCase().includes('interpretation');
  
  if (isInterpretation) {
    // Extract section number from "Interpretation of X.XXX" or "Interpretation of X.XXX #N"
    const sectionMatch = airtableId.match(/Interpretation of ([\d.]+(?:\([a-z]\))?)/i);
    if (sectionMatch) {
      const section = sectionMatch[1].toLowerCase();
      
      // Look for files containing this section
      return repoFiles.find(f => {
        // Files are like: 1997-07-07-RE-2.040h-permitting-adus.md
        const filename = f.filename.toLowerCase();
        // Convert 2.040(h) to 2.040h for matching
        const normalizedSection = section.replace(/[()]/g, '');
        return filename.includes(normalizedSection) || 
               filename.includes(section.replace('.', '-'));
      });
    }
  } else {
    // Extract document number
    const numMatch = airtableId.match(/#(\d+)(?:-(\d+))?/);
    if (!numMatch) return null;
    
    const docNum = numMatch[1];
    const year = numMatch[2];
    
    return repoFiles.find(f => {
      // Must match document number
      if (!f.filename.includes(`#${docNum}`)) return false;
      
      // Must be in correct directory
      if (isOrdinance && f.dir !== 'Ordinances') return false;
      if (isResolution && f.dir !== 'Resolutions') return false;
      
      // If Airtable has year, verify it matches
      if (year) {
        // Handle 2-digit years (93 -> 1993, 00 -> 2000, 17 -> 2017)
        if (year.length === 2) {
          const fullYear = parseInt(year) > 50 ? '19' + year : '20' + year;
          return f.filename.includes(fullYear) || f.filename.includes(`-${year}-`);
        }
        return f.filename.includes(year);
      }
      
      return true;
    });
  }
  
  return null;
}

/**
 * Main matching process
 */
async function matchDocuments() {
  try {
    console.log('🔄 Comprehensive Document Matching\n');
    console.log('='.repeat(60));
    
    // Get data
    console.log('\n📊 Fetching data...');
    const airtableRecords = await fetchAirtableRecords();
    const repoFiles = getRepoFiles();
    
    console.log(`  Airtable records: ${airtableRecords.length}`);
    console.log(`  Repository files: ${repoFiles.length}`);
    console.log('  - Ordinances:', repoFiles.filter(f => f.dir === 'Ordinances').length);
    console.log('  - Resolutions:', repoFiles.filter(f => f.dir === 'Resolutions').length);
    console.log('  - Interpretations:', repoFiles.filter(f => f.dir === 'Interpretations').length);
    
    // Match documents
    console.log('\n🔗 Matching Results:\n');
    const matches = [];
    const unmatched = [];
    const unmatchedFiles = new Set(repoFiles);
    
    for (const record of airtableRecords) {
      const match = findMatch(record, repoFiles);
      
      if (match) {
        matches.push({ record, file: match });
        unmatchedFiles.delete(match);
        console.log(`✅ ${record.fields.ID}`);
        console.log(`   → ${match.path}`);
      } else {
        unmatched.push(record);
        console.log(`❌ ${record.fields.ID}`);
      }
    }
    
    // Summary
    console.log('\n' + '='.repeat(60));
    console.log('\n📈 Summary:');
    console.log(`  Matched: ${matches.length}/${airtableRecords.length} Airtable records`);
    console.log(`  Unmatched Airtable: ${unmatched.length}`);
    console.log(`  Unmatched Files: ${unmatchedFiles.size}`);
    
    if (unmatched.length > 0) {
      console.log('\n⚠️  Unmatched Airtable records:');
      unmatched.forEach(r => console.log(`  - ${r.fields.ID}`));
    }
    
    if (unmatchedFiles.size > 0) {
      console.log('\n⚠️  Repository files without Airtable match:');
      unmatchedFiles.forEach(f => console.log(`  - ${f.path}`));
    }
    
    // Export matches for use in sync script
    console.log('\n💾 Saving matches to matches.json...');
    const exportData = matches.map(m => ({
      airtableId: m.record.id,
      airtableName: m.record.fields.ID,
      repoPath: m.file.path,
      type: m.file.dir.slice(0, -1) // Remove 's' from Ordinances -> Ordinance
    }));
    
    fs.writeFileSync('matches.json', JSON.stringify(exportData, null, 2));
    console.log('✅ Done! Matches saved to matches.json');
    
    return matches;
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  }
}

// Run if called directly
if (require.main === module) {
  matchDocuments();
}

module.exports = { matchDocuments, findMatch };