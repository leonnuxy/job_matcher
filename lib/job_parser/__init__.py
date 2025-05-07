"""
Job Parser Package

This package contains modules for parsing different aspects of job descriptions:
- extract_description: Extracts the main job description text
- extract_requirements: Extracts skills, technologies, and qualifications
- extract_location: Extracts job location information
- parser_utils: Shared utilities and constants for job parsing
"""

# Import the functions directly
from .extract_description import extract_job_description
from .extract_requirements import extract_job_requirements
from .extract_location import extract_job_location

# Make them available when importing from this package
__all__ = ['extract_job_description', 'extract_job_requirements', 'extract_job_location']
