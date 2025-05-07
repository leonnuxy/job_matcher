"""
Improved Job Location Extraction Module

This module handles extracting location information from job descriptions
using regular expression patterns to identify common location formats.
Includes better filtering and ranking of location candidates.
"""
import re
import logging

def extract_job_location(job_text):
    """
    Extracts job location information from job description.
    Uses an improved pattern matching approach with better candidate selection.

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
            # Explicit Location indicators with high confidence
            r'(?:Location|Position Location|Job Location|located in|based in|position in|job in)\s*[:;]\s*([A-Za-z\s]+(?:,\s*[A-Za-z]{2,})?)',
            
            # City, Province/State patterns (most reliable)
            r'([A-Za-z\s]+,\s*(?:AB|BC|MB|NB|NL|NS|NT|NU|ON|PE|QC|SK|YT|Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New\s+Hampshire|New\s+Jersey|New\s+Mexico|New\s+York|North\s+Carolina|North\s+Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode\s+Island|South\s+Carolina|South\s+Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West\s+Virginia|Wisconsin|Wyoming|AL|AK|AZ|AR|CA|CO|CT|DE|FL|GA|HI|ID|IL|IN|IA|KS|KY|LA|ME|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|OH|OK|OR|PA|RI|SC|SD|TN|TX|UT|VT|VA|WA|WV|WI|WY))\s*(?:$|[\s,])',
            
            # More generic City, Region pattern but with boundaries
            r'([A-Za-z][A-Za-z\s]+,\s*[A-Za-z][A-Za-z\s]{2,})\s*(?:$|[\s,\.\;\:])',
            
            # Preposition patterns (lower confidence but useful)
            r'(?:in|within|at|from)\s+([A-Za-z][A-Za-z\s]+),\s*([A-Za-z][A-Za-z\s]{2,})',
            
            # Remote, Hybrid or Flexible work patterns
            r'\b(hybrid|remote|flexible|work from home|telecommute|anywhere|virtual)\b(?:\s*(?:position|role|work|job|opportunity))?\s*',
            
            # Country specific patterns for Canada and USA
            r'\b(?:in|within)\s+(?:canada|usa|united\s+states|america),\s*([A-Za-z][A-Za-z\s]+)',
            r'\b(?:canada|usa)\s*:\s*([A-Za-z][A-Za-z\s]+)',
        ]

        # Valid location format validators
        is_valid_location = lambda loc: (
            loc and 
            len(loc) >= 3 and 
            not loc.isdigit() and
            not re.match(r'^developer|^software|^engineer|^position|^career|^job|^entry|^junior|^senior|^mid|^staff|^role|^team', loc.lower())
        )

        # Normalize whitespace and remove extra commas/spaces
        job_text_cleaned = re.sub(r'\s+', ' ', job_text.replace('\n', ' ')).strip()
        job_text_cleaned = re.sub(r',\s*', ', ', job_text_cleaned) # Normalize comma spacing
        job_text_cleaned = re.sub(r'\s*\(\s*', ' (', job_text_cleaned) # Normalize parentheses

        logging.debug(f"Cleaned job text for location extraction: {job_text_cleaned[:100]}...")

        # Extract locations based on patterns
        location_candidates = []
        for pattern_idx, pattern in enumerate(location_patterns):
            matches = re.findall(pattern, job_text_cleaned, re.I)
            confidence = 10 - pattern_idx  # Earlier patterns have higher confidence
            
            for match in matches:
                if isinstance(match, tuple):
                    # For patterns with multiple groups, join the groups
                    location = ', '.join(filter(None, match)).strip()
                    if is_valid_location(location):
                        location_candidates.append((location, confidence))
                else:
                    if match and is_valid_location(match):
                        location_candidates.append((match.strip(), confidence))

        # Remove duplicate locations (keep highest confidence)
        unique_locations = {}
        for loc, conf in location_candidates:
            loc_lower = loc.lower()
            if loc_lower not in unique_locations or conf > unique_locations[loc_lower][1]:
                unique_locations[loc_lower] = (loc, conf)
        
        # Return locations sorted by confidence
        sorted_locations = sorted(unique_locations.values(), key=lambda x: -x[1])
        location_strings = [loc for loc, conf in sorted_locations]
        
        # Log the found locations with confidence
        logging.info(f"Found locations: {', '.join(location_strings) if location_strings else 'None'}")

        # Return the best candidate or None if no valid location found
        return location_strings[0] if location_strings else None

    except Exception as e:
        logging.exception(f"Unexpected error during job location extraction: {e}. Text snippet: '{job_text[:100]}...'")
        return None
