#!/usr/bin/python3
"""
Audit script to identify documents missing from Airtable Public Metadata table
"""

import os
import json
import re
from pathlib import Path

def get_all_documents():
    """Get all documents from the repository"""
    documents = []
    
    # Ordinances
    ordinances_dir = Path("Ordinances")
    if ordinances_dir.exists():
        for file in ordinances_dir.glob("*.md"):
            if "STUB" not in file.name:  # Exclude stub files for now
                doc_name = extract_document_name(file.name, "Ordinance")
                documents.append({
                    "file": file.name,
                    "type": "Ordinance",
                    "display_name": doc_name,
                    "path": str(file)
                })
    
    # Resolutions
    resolutions_dir = Path("Resolutions")
    if resolutions_dir.exists():
        for file in resolutions_dir.glob("*.md"):
            doc_name = extract_document_name(file.name, "Resolution")
            documents.append({
                "file": file.name,
                "type": "Resolution",
                "display_name": doc_name,
                "path": str(file)
            })
    
    # Interpretations
    interpretations_dir = Path("Interpretations")
    if interpretations_dir.exists():
        for file in interpretations_dir.glob("*.md"):
            doc_name = extract_interpretation_name(file.name)
            documents.append({
                "file": file.name,
                "type": "Interpretation",
                "display_name": doc_name,
                "path": str(file)
            })
    
    # Other documents
    other_dir = Path("Other")
    if other_dir.exists():
        for file in other_dir.glob("*.md"):
            if "Charter" in file.name:
                documents.append({
                    "file": file.name,
                    "type": "Charter",
                    "display_name": "City Charter (1974)",
                    "path": str(file)
                })
            else:
                documents.append({
                    "file": file.name,
                    "type": "Other",
                    "display_name": file.stem.replace("-", " "),
                    "path": str(file)
                })
    
    # Transcripts
    transcripts_dir = Path("Transcripts")
    if transcripts_dir.exists():
        for file in transcripts_dir.glob("*.md"):
            doc_name = extract_transcript_name(file.name)
            documents.append({
                "file": file.name,
                "type": "Transcript",
                "display_name": doc_name,
                "path": str(file)
            })
    
    return sorted(documents, key=lambda x: (x["type"], x["display_name"]))

def extract_document_name(filename, doc_type):
    """Extract a clean document name from filename"""
    # Remove .md extension
    name = filename.replace(".md", "")
    
    # Extract parts for ordinances/resolutions
    if doc_type in ["Ordinance", "Resolution"]:
        # Pattern: YYYY-Ord-#XX-Topic or YYYY-Res-#XX-Topic
        match = re.match(r'(\d{4})-(?:Ord|Res)-#?(\d+(?:-\d+)?(?:[A-Z])?)-(.+)', name)
        if match:
            year, number, topic = match.groups()
            # Clean up topic
            topic = topic.replace("-", " ").title()
            return f"{doc_type} #{number} {topic} ({year})"
    
    return name.replace("-", " ").title()

def extract_interpretation_name(filename):
    """Extract interpretation name from filename"""
    # Remove .md extension
    name = filename.replace(".md", "")
    
    # Pattern: YYYY-MM-DD-RE-section-topic
    match = re.match(r'(\d{4}-\d{2}-\d{2})-RE-(.+)', name)
    if match:
        date, rest = match.groups()
        # Clean up the rest
        parts = rest.split("-")
        
        # Check if first part looks like a section number
        if parts[0] and (parts[0][0].isdigit() or parts[0].lower() == "balanced" or parts[0].lower() == "lots" or parts[0].lower() == "duplicate" or parts[0].lower() == "adu" or parts[0].lower() == "multi"):
            # Format as topic
            topic = " ".join(parts).title()
            topic = topic.replace("Adu", "ADU")
            return f"PC Interpretation - {topic} ({date})"
        else:
            # Has section number
            section = parts[0]
            topic = " ".join(parts[1:]).title() if len(parts) > 1 else ""
            return f"PC Interpretation - Section {section} {topic} ({date})".strip()
    
    return name.replace("-", " ").title()

def extract_transcript_name(filename):
    """Extract transcript name from filename"""
    # Remove .md extension
    name = filename.replace(".md", "")
    
    # Pattern like "02-2024 Transcript"
    if "Transcript" in name:
        name = name.replace(" Transcript", "")
        parts = name.split("-")
        if len(parts) == 2:
            month, year = parts
            month_names = {
                "01": "January", "02": "February", "03": "March", "04": "April",
                "05": "May", "06": "June", "07": "July", "08": "August",
                "09": "September", "10": "October", "11": "November", "12": "December"
            }
            month_name = month_names.get(month, month)
            return f"{month_name} {year} Council Meeting Transcript"
    
    return name.replace("-", " ").title()

def generate_airtable_data(documents):
    """Generate data needed for Airtable Public Metadata entries"""
    airtable_data = []
    
    for doc in documents:
        entry = {
            "Document Display Name": doc["display_name"],
            "Type": doc["type"],
            "GitHub Path": f"https://github.com/wifelette/city_of_rivergrove/blob/main/{doc['path']}",
            "Status": "Published"
        }
        
        # Extract year if available
        year_match = re.search(r'(\d{4})', doc["file"])
        if year_match:
            entry["Year"] = int(year_match.group(1))
        
        # Extract document number if applicable
        if doc["type"] in ["Ordinance", "Resolution"]:
            num_match = re.search(r'#(\d+)', doc["display_name"])
            if num_match:
                entry["Doc Number"] = int(num_match.group(1))
        
        airtable_data.append(entry)
    
    return airtable_data

def main():
    print("=" * 60)
    print("AIRTABLE COVERAGE AUDIT")
    print("=" * 60)
    
    # Get all documents
    all_docs = get_all_documents()
    
    # Count by type
    type_counts = {}
    for doc in all_docs:
        doc_type = doc["type"]
        type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
    
    print(f"\nTotal documents found: {len(all_docs)}")
    print("\nBreakdown by type:")
    for doc_type, count in sorted(type_counts.items()):
        print(f"  {doc_type}: {count}")
    
    print("\n" + "=" * 60)
    print("ALL DOCUMENTS (for Airtable Public Metadata)")
    print("=" * 60)
    
    # Group by type for display
    by_type = {}
    for doc in all_docs:
        doc_type = doc["type"]
        if doc_type not in by_type:
            by_type[doc_type] = []
        by_type[doc_type].append(doc)
    
    for doc_type in sorted(by_type.keys()):
        print(f"\n{doc_type.upper()}S ({len(by_type[doc_type])} documents):")
        print("-" * 40)
        for doc in by_type[doc_type]:
            print(f"  {doc['display_name']}")
    
    # Generate Airtable data
    print("\n" + "=" * 60)
    print("AIRTABLE DATA (JSON format)")
    print("=" * 60)
    
    airtable_data = generate_airtable_data(all_docs)
    
    # Save to JSON file
    with open("airtable_metadata_all_documents.json", "w") as f:
        json.dump(airtable_data, f, indent=2)
    
    print(f"\nGenerated data for {len(airtable_data)} documents")
    print("Saved to: airtable_metadata_all_documents.json")
    
    # Create a checklist
    print("\n" + "=" * 60)
    print("CHECKLIST FOR VERIFICATION")
    print("=" * 60)
    print("\nDocuments to verify in Airtable Public Metadata:")
    
    for i, doc in enumerate(all_docs, 1):
        print(f"[ ] {i}. {doc['display_name']} ({doc['type']})")

if __name__ == "__main__":
    main()