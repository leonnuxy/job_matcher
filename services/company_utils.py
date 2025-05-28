"""
Utilities for company name extraction and validation.
"""
import re
from urllib.parse import urlparse


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
