#!/usr/bin/env node
/**
 * Enhanced matching for Interpretations between repository and Airtable
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
require('dotenv').config();

// Airtable configuration
const AIRTABLE_API_KEY = process.env.AIRTABLE_API_KEY;
const AIRTABLE_BASE_ID = process.env.AIRTABLE_BASE_ID || 'appnsWognX10X9TDL';

if (!AIRTABLE_API_KEY) {
  console.error('Error: AIRTABLE_API_KEY environment variable is required');
  process.exit(1);
}

/**
 * Manual mapping for Interpretations
 * Maps Airtable names to repository filenames
 */
const INTERPRETATION_MAPPINGS = {
  // Format: "Airtable Name": "repo filename pattern"
  "Interpretation of 2.040(h)": "1997-07-07-RE-2.040h-permitting-adus",
  "Interpretation of 4.020": null, // Need to identify which file this is
  "Interpretation of 5.2-4": null, // Need to identify which file this is
  "Interpretation of 5.010 #1": "2002-09-05-RE-duplicate", // Might be the duplicate one?
  "Interpretation of 5.010 #2": null,
  "Interpretation of 5.080 #1": "1998-03-02-RE-5.080-setbacks",
  "Interpretation of 5.080 #2": "1998-06-01-RE-5.080-setback-orientation",
  "Interpretation of 5.080 #3": "1998-07-06-RE-5.080-setback-orientation", 
  "Interpretation of 5.080 #4": "2004-10-11-RE-5.080-setbacks",
  "Interpretation of 9.030 #1": "1997-09-08-RE-9.030-permit-fees-and-completeness",
  "Interpretation of 9.030 #2": "1997-11-03-RE-9.030-permit-fees-and-completeness",
  "Interpretation of ORD 68-2000": null, // Need to identify
};

/**
 * Get interpretation files from repo with their content headers
 */
function analyzeInterpretationFiles() {
  const dir = 'Interpretations';
  if (!fs.existsSync(dir)) return [];
  
  const files = fs.readdirSync(dir)
    .filter(f => f.endsWith('.md'))
    .map(filename => {
      const filepath = path.join(dir, filename);
      const content = fs.readFileSync(filepath, 'utf8');
      
      // Extract key info from content
      const lines = content.split('\n').slice(0, 50); // First 50 lines
      
      // Look for RE: line
      const reLine = lines.find(l => l.startsWith('**RE:**') || l.startsWith('RE:'));
      
      // Look for section references
      const sectionMatch = content.match(/Section\s+([\d.]+(?:\([a-z]\))?)/i);
      
      // Parse date from filename
      const dateMatch = filename.match(/(\d{4}-\d{2}-\d{2})/);
      const date = dateMatch ? dateMatch[1] : null;
      
      return {
        filename,
        filepath,
        date,
        reLine,
        section: sectionMatch ? sectionMatch[1] : null,
        firstLines: lines.slice(0, 10).join('\n')
      };
    });
  
  return files;
}

/**
 * Fetch Airtable Interpretations
 */
async function fetchAirtableInterpretations() {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: 'api.airtable.com',
      path: `/v0/${AIRTABLE_BASE_ID}/Ordinances%20and%20Resolutions?filterByFormula=${encodeURIComponent("SEARCH('Interpretation', {ID})")}`,
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
 * Smart matching based on content analysis
 */
function findBestMatch(airtableName, repoFiles) {
  // Check manual mapping first
  const manualMap = INTERPRETATION_MAPPINGS[airtableName];
  if (manualMap) {
    return repoFiles.find(f => f.filename.includes(manualMap));
  }
  
  // Extract section from Airtable name
  const sectionMatch = airtableName.match(/of\s+([\d.]+(?:\([a-z]\))?)/i);
  if (sectionMatch) {
    const section = sectionMatch[1].replace(/[()]/g, ''); // Remove parentheses
    
    // Find files with this section
    const candidates = repoFiles.filter(f => {
      const fileSection = f.section ? f.section.replace(/[()]/g, '') : '';
      const filenameHasSection = f.filename.toLowerCase().includes(section.toLowerCase().replace('.', '-')) ||
                                  f.filename.toLowerCase().includes(section.toLowerCase());
      const contentHasSection = f.reLine && f.reLine.toLowerCase().includes(section.toLowerCase());
      
      return filenameHasSection || contentHasSection || fileSection === section;
    });
    
    // If multiple candidates and name has #N, use chronological order
    if (candidates.length > 1 && airtableName.includes('#')) {
      const num = parseInt(airtableName.match(/#(\d+)/)[1]) - 1;
      // Sort by date and pick the Nth one
      candidates.sort((a, b) => (a.date || '').localeCompare(b.date || ''));
      return candidates[num] || null;
    }
    
    return candidates[0] || null;
  }
  
  return null;
}

/**
 * Main process
 */
async function main() {
  console.log('🔍 Interpretation Matching Analysis\n');
  console.log('='.repeat(60));
  
  // Get repo files with content analysis
  console.log('\n📁 Analyzing repository Interpretation files...\n');
  const repoFiles = analyzeInterpretationFiles();
  
  repoFiles.forEach(f => {
    console.log(`File: ${f.filename}`);
    console.log(`  Date: ${f.date}`);
    console.log(`  Section: ${f.section || 'Not found'}`);
    if (f.reLine) console.log(`  RE: ${f.reLine.substring(0, 60)}...`);
    console.log();
  });
  
  // Get Airtable interpretations
  console.log('📊 Fetching Airtable Interpretations...\n');
  const airtableRecords = await fetchAirtableInterpretations();
  
  console.log(`Found ${airtableRecords.length} Interpretations in Airtable:\n`);
  airtableRecords.forEach(r => {
    console.log(`  - ${r.fields.ID}`);
  });
  
  // Match them
  console.log('\n' + '='.repeat(60));
  console.log('\n🔗 MATCHING RESULTS:\n');
  
  const matches = [];
  const unmatched = [];
  const usedFiles = new Set();
  
  for (const record of airtableRecords) {
    const name = record.fields.ID;
    const match = findBestMatch(name, repoFiles);
    
    if (match) {
      matches.push({
        airtableId: record.id,
        airtableName: name,
        repoPath: match.filepath,
        type: 'Interpretation'
      });
      usedFiles.add(match.filename);
      console.log(`✅ ${name}`);
      console.log(`   → ${match.filename}`);
    } else {
      unmatched.push(name);
      console.log(`❌ ${name} - NO MATCH FOUND`);
    }
  }
  
  // Find unmatched repo files
  const unmatchedFiles = repoFiles.filter(f => !usedFiles.has(f.filename));
  
  if (unmatchedFiles.length > 0) {
    console.log('\n⚠️  Repository files without Airtable match:');
    unmatchedFiles.forEach(f => {
      console.log(`  - ${f.filename}`);
      if (f.reLine) console.log(`    ${f.reLine.substring(0, 50)}...`);
    });
  }
  
  // Save interpretation matches
  console.log('\n💾 Saving interpretation matches...');
  fs.writeFileSync('interpretation-matches.json', JSON.stringify(matches, null, 2));
  
  console.log('\n' + '='.repeat(60));
  console.log('\n📊 Summary:');
  console.log(`  Matched: ${matches.length}/${airtableRecords.length}`);
  console.log(`  Unmatched Airtable: ${unmatched.length}`);
  console.log(`  Unmatched Files: ${unmatchedFiles.length}`);
  
  // Suggest manual review
  if (unmatched.length > 0 || unmatchedFiles.length > 0) {
    console.log('\n📝 Manual Review Needed:');
    console.log('Please review the unmatched items and update INTERPRETATION_MAPPINGS');
    console.log('in this script with the correct mappings.');
  }
}

main().catch(console.error);