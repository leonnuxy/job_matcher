"""
Enhanced Job Parser Module

This module provides improved functions for parsing job descriptions to extract
key information such as main description text, job requirements/skills, and location details.
Uses the enhanced extraction modules in lib/x_*.py files.

Example:
    from lib.job_parser_enhanced import (
        extract_job_description, 
        extract_job_requirements, 
        extract_job_location
    )
    
    description = extract_job_description(job_text)
    requirements = extract_job_requirements(job_text)  
    location = extract_job_location(job_text)
"""

import logging
from lib.x_desc import extract_job_description
from lib.x_reqs import extract_job_requirements
from lib.x_loc import extract_job_location

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Re-export the main functions
__all__ = ['extract_job_description', 'extract_job_requirements', 'extract_job_location']
