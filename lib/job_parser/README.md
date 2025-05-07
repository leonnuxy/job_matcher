# Job Parser Package

This package contains modules for parsing job descriptions and extracting key information.

## Module Structure

- **extract_description.py**: Extracts the main job description content from HTML or plain text
- **extract_requirements.py**: Identifies skills, technologies, and qualifications from job descriptions
- **extract_location.py**: Determines job location from job descriptions
- **parser_utils.py**: Shared utilities and constants

## Usage

```python
from lib.job_parser import (
    extract_job_description,
    extract_job_requirements, 
    extract_job_location
)

# Extract job description
description = extract_job_description(job_text)

# Extract requirements
skills = extract_job_requirements(job_text)

# Extract location
location = extract_job_location(job_text)
```

## Implementation Notes

- Uses a combination of NLP techniques including Rake-nltk, spaCy, and regex patterns
- Handles both HTML and plain text job postings
- Filters out common non-skill words via stop word list
- Prioritizes and normalizes technology keywords
