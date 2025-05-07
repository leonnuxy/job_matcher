"""
Job Location Extraction Module

This module handles extracting location information from job descriptions
using regular expression patterns to identify common location formats.
"""
import re
import logging

def extract_job_location(job_text):
    """
    Extracts job location information from job description.

    Args:
        job_text (str): The job description text.

    Returns:
        str: The extracted location or None if not found.
    """
    logging.info("Extracting job location")

    if not job_text or not job_text.strip():
        logging.warning("Empty job text provided for location extraction.")
        return None

    try:
        # Common location patterns in North American job postings (Improved)
        location_patterns = [
            # Explicit Location: City, Province/State (Full or Abbr.)
            r'(?:Location|located in|based in|position in|job in)\s*:\s*([A-Za-z\s]+,\s*[A-Za-z]{2,})',
            r'([A-Za-z\s]+,\s*[A-Za-z]{2,})\s*(?:$|[\s,])',
            # Implicit Location: Often after "in" or "within" followed by a city and state/province
            r'in\s+([A-Za-z\s]+),\s*([A-Za-z]{2,})',
            r'within\s+([A-Za-z\s]+),\s*([A-Za-z]{2,})',
            # Remote or Flexible Locations
            r'\b(remote|flexible|work from home|telecommute|anywhere)\b',
            # Specific patterns for Canada and USA (using capturing groups instead of look-behind)
            r'\bcanada\s*:\s*([A-Za-z\s]+)',
            r'\bin\s*canada,\s*([A-Za-z\s]+)',
            r'\busa\s*:\s*([A-Za-z\s]+)',
            r'\bin\s*usa,\s*([A-Za-z\s]+)',
        ]

        # Normalize whitespace and remove extra commas/spaces
        job_text_cleaned = re.sub(r'\s+', ' ', job_text.replace('\n', ' ')).strip()
        job_text_cleaned = re.sub(r',\s*', ', ', job_text_cleaned) # Normalize comma spacing

        logging.debug(f"Cleaned job text for location extraction: {job_text_cleaned}")

        # Extract locations based on patterns
        locations = set()
        for pattern in location_patterns:
            matches = re.findall(pattern, job_text_cleaned, re.I)
            for match in matches:
                if isinstance(match, tuple):
                    # For patterns with multiple groups, join the groups
                    location = ', '.join(filter(None, match)).strip()
                    if location:
                        locations.add(location)
                else:
                    if match:
                        locations.add(match.strip())

        # Prioritize specific patterns: City, State/Country
        prioritized_locations = sorted(locations, key=lambda loc: (len(loc.split(',')), loc)) # Fewer commas first

        # Log the found locations
        logging.info(f"Found locations: {prioritized_locations}")

        # Return the best candidate or None if no valid location found
        return prioritized_locations[0] if prioritized_locations else None

    except Exception as e:
        logging.exception(f"Unexpected error during job location extraction: {e}. Text snippet: '{job_text[:100]}...'")
        return None
