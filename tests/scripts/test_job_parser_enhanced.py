"""
Enhanced Job Parser Test Script

This script tests the improved job parsing functions to compare with the original parser.
It processes the same job postings and shows the differences in extraction quality.

Usage: python test_job_parser_enhanced.py
"""

import os
import sys
import logging
import json
from pathlib import Path
import difflib
from pprint import pprint

# Add project root to path for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import both original and enhanced job parser modules
from lib import job_parser
from lib import job_parser_enhanced

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_job_data(file_path):
    """Load job data from a JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def compare_extraction(job, field):
    """Compare extraction between original and enhanced parser for a specific field"""
    print(f"\n=== Comparing {field} extraction ===")
    
    original_value = None
    if field == "job_description":
        original_value = job.get(field, "")
    elif field == "job_requirements":
        original_value = job.get(field, [])
    elif field == "location":
        original_value = job.get(field, None)
    
    # Extract using enhanced parser
    job_text = job.get("job_description", "")
    enhanced_value = None
    
    if field == "job_description":
        enhanced_value = job_parser_enhanced.extract_job_description(job_text)
    elif field == "job_requirements":
        enhanced_value = job_parser_enhanced.extract_job_requirements(job_text)
    elif field == "location":
        enhanced_value = job_parser_enhanced.extract_job_location(job_text)
    
    # Print comparison
    print(f"\nJob Title: {job.get('title', 'Unknown')}")
    
    if field == "job_description":
        # For text fields, print first 200 chars
        print(f"\nOriginal ({len(original_value)} chars):\n{original_value[:200]}...")
        print(f"\nEnhanced ({len(enhanced_value)} chars):\n{enhanced_value[:200]}...")
    elif field == "job_requirements":
        # For lists, print all items
        print(f"\nOriginal ({len(original_value)} items):")
        pprint(original_value)
        print(f"\nEnhanced ({len(enhanced_value)} items):")
        pprint(enhanced_value)
    else:
        # For other fields, print directly
        print(f"\nOriginal: {original_value}")
        print(f"Enhanced: {enhanced_value}")
    
    return original_value, enhanced_value

def main():
    # Load job data
    results_dir = PROJECT_ROOT / "results"
    json_files = list(results_dir.glob("job_search_*.json"))
    
    if not json_files:
        print("No job search result files found. Please run a job search first.")
        return
    
    # Use the most recent file
    latest_file = max(json_files, key=os.path.getmtime)
    print(f"Using most recent job data file: {latest_file.name}")
    
    job_data = load_job_data(latest_file)
    
    # Extract a sample of jobs from the data
    sample_jobs = []
    for search_term, jobs in job_data.items():
        if jobs and len(jobs) > 0:
            # Take the first job from each search term
            sample_jobs.append(jobs[0])
            # And one more if available
            if len(jobs) > 3:
                sample_jobs.append(jobs[3])
                
    # Limit to 6 jobs for cleaner output
    sample_jobs = sample_jobs[:6]
    
    print(f"Testing with {len(sample_jobs)} sample jobs")
    
    # Test extraction for each field
    for job in sample_jobs:
        print("\n" + "="*80)
        print(f"JOB: {job.get('title', 'Unknown')}")
        print("="*80)
        
        # Compare location extraction
        original_loc, enhanced_loc = compare_extraction(job, "location")
        
        # Compare requirements extraction
        original_reqs, enhanced_reqs = compare_extraction(job, "job_requirements")
        
        # Compare description extraction
        original_desc, enhanced_desc = compare_extraction(job, "job_description")
            
if __name__ == "__main__":
    main()
