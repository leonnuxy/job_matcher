# utils.py
"""
Utility functions for the job_matcher application.
"""
import os
import re
import datetime
from urllib.parse import urlparse
from typing import Optional, List
import sys

# Add parent directory to sys.path if running as a module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)
def clean_job_title(raw_title: str, snippet: str = "") -> str:
    """
    Clean a job title by removing dates, page numbers, and other irrelevant information.
    
    Args:
        raw_title: The raw job title string
        snippet: Optional snippet text that might contain relevant job title information
        
    Returns:
        cleaned_title: A cleaner version of the job title
    """
    # Check if this is likely a job search results page
    is_search_page = re.search(r'^\d+\+?\s+|jobs|employment|careers', raw_title.lower()) is not None
    
    # Remove dates (various formats) from title
    cleaned_title = re.sub(r'\s+\d+\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*,?\s+202\d\s*[\|\-]?.*$', '', raw_title)
    cleaned_title = re.sub(r'\s+\d+\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?$', '', cleaned_title)
    
    # Remove year references
    cleaned_title = re.sub(r'\s+202\d\s*[\|\-]?.*$', '', cleaned_title)
    cleaned_title = re.sub(r'\s+202\d$', '', cleaned_title)
    
    # Remove job board suffixes 
    cleaned_title = re.sub(r' - (Job Posting|Career|Job Application|Jobs|Careers|Job Opportunity|Apply Now).*$', '', cleaned_title)
    
    # Clean up leading numbers (like "50+ Python Jobs")
    cleaned_title = re.sub(r'^\d+\+?\s+', '', cleaned_title)
    
    # Remove other common suffixes
    cleaned_title = re.sub(r' – Apply Now$', '', cleaned_title)
    cleaned_title = re.sub(r'\s+in\s+[A-Za-z, ]+\.\.\.?$', '', cleaned_title)
    cleaned_title = re.sub(r'\s*\|.*$', '', cleaned_title)
    cleaned_title = re.sub(r'Employment.*$', '', cleaned_title)
    
    # Clean up common prefixes
    cleaned_title = re.sub(r'^(?:Job:|Position:|Hiring:)\s*', '', cleaned_title)
    
    # If this looks like a job search results page, try to extract specific job titles
    if is_search_page:
        # Try to extract job titles from the title and snippet
        combined_text = f"{cleaned_title} {snippet}"
        
        # Look for common patterns in job search titles
        search_title_match = re.search(r'(?:^\d+\+?\s+)?(.*?)(?:\s+Jobs|$)', cleaned_title)
        if search_title_match:
            job_type = search_title_match.group(1).strip()
            if job_type and len(job_type) > 3:
                cleaned_title = job_type
                
        # Try to find specific job titles in the combined text
        job_title_patterns = [
            # Python roles
            r'((?:Senior|Staff|Principal|Junior|Lead|Mid)\s*Python\s+Developer)',
            r'(Python\s+(?:Software|Backend|Full\s*Stack)\s+Engineer)',
            # Developer roles
            r'((?:Senior|Staff|Principal|Junior|Lead|Mid)\s*(?:Software|Full\s*Stack|Frontend|Backend)\s+(?:Developer|Engineer))',
            # Data/ML roles  
            r'((?:Senior|Staff|Principal|Junior|Lead|Mid)\s*Data\s+Scientist)',
            r'((?:Senior|Staff|Principal|Junior|Lead|Mid)\s*Machine\s+Learning\s+Engineer)',
            # Other roles
            r'((?:Senior|Staff|Principal|Junior|Lead|Mid)\s*DevOps\s+Engineer)'
        ]
        
        for pattern in job_title_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                return match.group(1)
    
    # Final cleanup and standardization
    cleaned_title = cleaned_title.strip()
    
    # Standardize common job title variations
    cleaned_title = re.sub(r'(?i)software engineer(?:ing)?', 'Software Engineer', cleaned_title)
    cleaned_title = re.sub(r'(?i)sr\.?\s+', 'Senior ', cleaned_title)
    cleaned_title = re.sub(r'(?i)jr\.?\s+', 'Junior ', cleaned_title)
    
    # Default to raw title if our cleaning made it too short
    return cleaned_title if len(cleaned_title) > 3 else raw_title.strip()


def clean_job_snippet(snippet: str) -> str:
    """
    Clean a job snippet by removing timestamps, ellipses, and common prefixes.
    
    Args:
        snippet: The raw snippet string
        
    Returns:
        cleaned_snippet: A cleaner version of the snippet
    """
    # Remove timestamps like "5 days ago" from the beginning
    cleaned_snippet = re.sub(r'^\s*(?:\d+\s+(?:hour|day|week|month)s?\s+ago|Posted \d+\s+days?)\s*[:\-\.\s]*', '', snippet)
    
    # Remove common prefixes
    cleaned_snippet = re.sub(r'^\s*(?:Job Description|Description|About the Role|Position Summary)\s*[:\-\.\s]*', '', cleaned_snippet)
    
    # Remove ellipses from the end
    cleaned_snippet = re.sub(r'[\s\.]+…$', '', cleaned_snippet)
    
    return cleaned_snippet.strip()

def regex_search(text: str, patterns: list[str]) -> Optional[str]:
    """
    Search for the first match of any pattern in the text.
    """
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE|re.DOTALL)
        if m:
            return m.group(1).strip()
    return None


def is_valid_company_name(company: str) -> bool:
    """
    Check if a string appears to be a valid company name.
    
    Args:
        company: The potential company name
        
    Returns:
        is_valid: True if the string seems to be a valid company name
    """
    if not company or len(company) < 2:
        return False
        
    # Skip dates
    if re.match(r'\d{1,2}/\d{1,2}|\d{4}', company):
        return False
        
    # Skip common non-company phrases
    invalid_phrases = [
        'job', 'description', 'position', 'experience', 'skills', 'required',
        'full time', 'part time', 'contract', 'permanent', 'USA', 'apply now',
        'united states', 'remote', 'hybrid', 'onsite', 'see more', 'read more',
        'bachelor', 'master', 'phd', 'javascript', 'typescript', 'python',
        'senior', 'junior', 'mid level', 'software', 'developer', 'engineer',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 
        'salary', 'compensation', 'benefits', 'www'
    ]
    
    company_lower = company.lower()
    if any(phrase in company_lower for phrase in invalid_phrases):
        return False
        
    # Skip if it's too long (likely a phrase, not a company)
    if len(company.split()) > 4:
        return False
        
    return True

def extract_company_from_url(url: str) -> str:
    """
    Extract company name from the URL.
    
    Args:
        url: The URL to extract company name from
        
    Returns:
        company_name: The extracted company name or "Unknown"
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    
    # Domain-specific extractors
    if 'linkedin.com' in domain:
        # LinkedIn format: linkedin.com/company/company-name
        path_segments = parsed_url.path.split('/')
        if len(path_segments) >= 3 and path_segments[1] == 'company':
            potential_company = path_segments[2].replace('-', ' ').title()
            if is_valid_company_name(potential_company):
                return potential_company
    
    elif 'indeed.com' in domain:
        # Indeed format: indeed.com/cmp/Company-Name
        path_segments = parsed_url.path.split('/')
        if len(path_segments) >= 3 and path_segments[1] == 'cmp':
            potential_company = path_segments[2].replace('-', ' ').title()
            if is_valid_company_name(potential_company):
                return potential_company
                
    elif 'glassdoor.com' in domain:
        # Glassdoor format: glassdoor.com/company-name
        path_segments = [p for p in parsed_url.path.split('/') if p]
        if path_segments:
            for segment in path_segments:
                if segment and 'reviews' in segment:
                    company_part = segment.split('-reviews')[0].replace('-', ' ').title()
                    if is_valid_company_name(company_part):
                        return company_part
    
    # Generic extraction: Look for company in the URL path
    path_segments = [p for p in parsed_url.path.split('/') if p]
    if len(path_segments) >= 3 and "company" in path_segments:
        company_idx = path_segments.index("company")
        if company_idx + 1 < len(path_segments):
            potential_company = path_segments[company_idx + 1].replace('-', ' ').title()
            if is_valid_company_name(potential_company):
                return potential_company
    
    # Extract from LinkedIn hiring pattern in title
    hiring_match = re.search(r'([A-Z][A-Za-z0-9\s&\.\']+)\s+hiring\s+', url)
    if hiring_match:
        potential_company = hiring_match.group(1).strip()
        if is_valid_company_name(potential_company):
            return potential_company
    
    return "Unknown"


