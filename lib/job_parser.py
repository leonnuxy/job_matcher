"""
Job Parser Module

This module provides functions for parsing job descriptions to extract
key information such as main description text, job requirements/skills,
and location details.

This module now serves as a wrapper to import and re-export functions from the 
job_parser package for backward compatibility.
"""

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Simply re-export the functions from the new package structure
from lib.job_parser.extract_description import extract_job_description
from lib.job_parser.extract_requirements import extract_job_requirements
from lib.job_parser.extract_location import extract_job_location

# For easier importing by other modules
__all__ = ['extract_job_description', 'extract_job_requirements', 'extract_job_location']