#!/usr/bin/python3
"""
Script to identify which Ordinances and Resolutions records 
are missing from the Public Metadata table
"""

import subprocess
import json
import sys

def run_mcp_command(command):
    """Run an MCP command and return the parsed JSON output"""
    try:
        result = subprocess.run(
            ["mcp", "call"] + command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print(f"Error output: {e.stderr}")
        return None
    except json.JSONDecodeError:
        print(f"Could not parse JSON from command output")
        return None

def get_all_ordinances_resolutions():
    """Get all records from Ordinances and Resolutions table"""
    print("Fetching all Ordinances and Resolutions records...")
    result = run_mcp_command("daily-tasks council_ordinances_list maxRecords:200")
    
    if not result:
        print("Failed to fetch ordinances and resolutions")
        return []
    
    records = []
    for record in result:
        rec_id = record.get('id', '')
        fields = record.get('fields', {})
        
        # Get the document identifier - try different field names
        doc_name = fields.get('Name') or fields.get('Ordinance/Resolution') or fields.get('Title', '')
        doc_type = fields.get('Type', '')
        digitized = fields.get('Digitized', False)
        year = fields.get('Year', '')
        
        records.append({
            'id': rec_id,
            'name': doc_name,
            'type': doc_type,
            'digitized': digitized,
            'year': year,
            'fields': fields  # Keep all fields for reference
        })
    
    return records

def get_public_metadata_records():
    """Get all existing Public Metadata records"""
    print("Fetching all Public Metadata records...")
    result = run_mcp_command("daily-tasks council_public_metadata_list maxRecords:200")
    
    if not result:
        print("Failed to fetch public metadata")
        return []
    
    linked_doc_ids = []
    for record in result:
        fields = record.get('fields', {})
        # The Document field contains linked record IDs
        doc_links = fields.get('Document', [])
        if doc_links:
            linked_doc_ids.extend(doc_links)
    
    return linked_doc_ids

def main():
    print("=" * 60)
    print("IDENTIFYING MISSING PUBLIC METADATA ENTRIES")
    print("=" * 60)
    
    # Get all ordinances/resolutions
    all_docs = get_all_ordinances_resolutions()
    print(f"\nFound {len(all_docs)} total Ordinances and Resolutions records")
    
    # Get existing public metadata links
    existing_metadata_links = get_public_metadata_records()
    existing_ids = set(existing_metadata_links)
    print(f"Found {len(existing_ids)} documents with Public Metadata entries")
    
    # Find missing ones
    missing_docs = []
    for doc in all_docs:
        if doc['id'] not in existing_ids:
            # Only include digitized documents
            if doc.get('digitized'):
                missing_docs.append(doc)
    
    print(f"\n{len(missing_docs)} digitized documents are MISSING from Public Metadata:")
    print("=" * 60)
    
    # Group by type
    by_type = {}
    for doc in missing_docs:
        doc_type = doc.get('type', 'Unknown')
        if doc_type not in by_type:
            by_type[doc_type] = []
        by_type[doc_type].append(doc)
    
    # Display missing documents
    for doc_type, docs in sorted(by_type.items()):
        print(f"\n{doc_type.upper()}S ({len(docs)} missing):")
        print("-" * 40)
        for doc in sorted(docs, key=lambda x: x.get('year', 0)):
            print(f"  ID: {doc['id']}")
            print(f"     Name: {doc['name']}")
            print(f"     Year: {doc.get('year', 'N/A')}")
            print()
    
    # Generate commands to create missing entries
    print("\n" + "=" * 60)
    print("MCP COMMANDS TO CREATE MISSING ENTRIES:")
    print("=" * 60)
    
    for doc in missing_docs:
        command = f'council_public_metadata_create fields:{{"Document":"{doc["id"]}","Publication Status":"Published"}}'
        print(f"\nmcp call daily-tasks {command}")
    
    # Save to file
    with open("missing_metadata_commands.txt", "w") as f:
        f.write("# Commands to create missing Public Metadata entries\n\n")
        for doc in missing_docs:
            command = f'mcp call daily-tasks council_public_metadata_create fields:{{"Document":"{doc["id"]}","Publication Status":"Published"}}'
            f.write(f"{command}\n")
    
    print(f"\n\nCommands saved to: missing_metadata_commands.txt")
    print(f"Total missing entries to create: {len(missing_docs)}")

if __name__ == "__main__":
    main()