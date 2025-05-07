"""
Job Parser Test Script

This script demonstrates how to use the refactored job parsing functionality.
It tests the three main functions:
- extract_job_description
- extract_job_requirements
- extract_job_location

Usage: python test_job_parser_refactored.py
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path for imports
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import the job parser module
from lib import job_parser

def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Sample job description text
    job_text = """
    Job Description
    
    We're looking for a Software Engineer to join our team. 
    In this role, you will design and build web applications using Python and React.
    
    Responsibilities:
    - Develop scalable web applications
    - Implement new features and maintain existing ones
    - Write clean, maintainable code
    - Collaborate with other engineers
    
    Requirements:
    - 3+ years of experience with Python
    - Experience with React, JavaScript, and HTML/CSS
    - Knowledge of SQL and PostgreSQL
    - Strong problem-solving skills
    - Bachelor's degree in Computer Science or related field
    
    Location: San Francisco, CA
    
    This is a remote position with occasional travel to our San Francisco office.
    """
    
    print("Testing job parser refactored modules...")
    
    # Test job description extraction
    description = job_parser.extract_job_description(job_text)
    print("\n--- Job Description ---")
    print(description)
    
    # Test job requirements extraction
    requirements = job_parser.extract_job_requirements(job_text)
    print("\n--- Job Requirements ---")
    for req in requirements:
        print(f"- {req}")
    
    # Test job location extraction
    location = job_parser.extract_job_location(job_text)
    print("\n--- Job Location ---")
    print(location)

if __name__ == "__main__":
    main()
