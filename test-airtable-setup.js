#!/usr/bin/env node
/**
 * Test script for Airtable setup - runs through Claude Code to access MCP tools
 */

async function testAirtableSetup() {
  console.log('🧪 Testing Airtable Setup through Claude Code...\n');
  
  try {
    // Test 1: List a single ordinance record
    console.log('📋 Test 1: Fetching one Ordinance record...');
    const ordinances = await council_ordinances_list({ maxRecords: 1 });
    console.log(`✅ Found ${ordinances.records.length} record(s)`);
    if (ordinances.records.length > 0) {
      const record = ordinances.records[0];
      console.log(`   ID: ${record.fields.ID}`);
      console.log(`   Record ID: ${record.id}`);
    }
    
    // Test 2: Check existing Public Metadata
    console.log('\n🔍 Test 2: Checking Public Metadata...');
    const metadata = await council_public_metadata_list({ maxRecords: 5 });
    console.log(`✅ Found ${metadata.records.length} Public Metadata record(s)`);
    
    // Test 3: Show what would be created (dry run)
    console.log('\n📝 Test 3: What would be created...');
    if (ordinances.records.length > 0) {
      const testRecord = ordinances.records[0];
      console.log('Would create Public Metadata record:');
      console.log(`   Document: ${testRecord.id} (${testRecord.fields.ID})`);
      console.log('   Publication Status: Draft');
      console.log('   Digitization Notes: (empty)');
      console.log('   Public Tags: (empty)');
    }
    
    console.log('\n✅ All tests passed! Ready to run the full setup.');
    console.log('\nNext step: Run the actual setup with:');
    console.log('   node airtable-sync.js --setup --test-single');
    
  } catch (error) {
    console.error('❌ Error during testing:', error.message);
    console.error('Make sure MCP tools are available through Claude Code');
  }
}

// Run the test
testAirtableSetup();