"""
Enhanced job description parsing functionality.
"""
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional

def parse_job_details(soup: BeautifulSoup) -> Dict:
    """
    Extract job details from BeautifulSoup object with enhanced description extraction.
    
    Args:
        soup: BeautifulSoup object of the job page
        
    Returns:
        Dictionary containing job details (description, location, company, etc.)
    """
    info: Dict[str, Optional[str]] = {}
    
    # Try to extract description using common selectors
    description_selectors = [
        '.job-description', '.description', '[data-automation="jobDescription"]',
        '#job-description', '.jobDescriptionText', '.details-info',
        '[data-test="job-description"]', '.job-desc', '.jobDesc',
        '.job_description', '#jobDescriptionText', '.job-details',
        '[itemprop="description"]', '.description-section',
        'section.description', 'div[class*="description"]'
    ]
    info['description'] = text_or_none(soup, description_selectors)
    
    # If no description found with selectors, try to find it in the page content
    if not info.get('description'):
        # Look for common container headings and extract content after them
        description_heading_patterns = [
            (r'<h[1-3][^>]*>Job Description</h[1-3]>(.*?)<h[1-3]', 1),
            (r'<h[1-3][^>]*>Description</h[1-3]>(.*?)<h[1-3]', 1),
            (r'<h[1-4][^>]*>About the role</h[1-4]>(.*?)<h[1-4]', 1),
            (r'<strong>Job Description:?</strong>(.*?)(?:<strong>|<h[1-4])', 1),
            (r'<div[^>]*>Description</div>(.*?)(?:<div[^>]*>|<section)', 1)
        ]
        
        html_str = str(soup)
        for pattern, group in description_heading_patterns:
            match = re.search(pattern, html_str, re.IGNORECASE | re.DOTALL)
            if match:
                # Extract the content and convert to text
                content_html = match.group(group)
                content_soup = BeautifulSoup(content_html, 'lxml')
                description_text = content_soup.get_text(separator=' ', strip=True)
                
                if description_text and len(description_text) > 50:
                    info['description'] = description_text
                    break
    
    # Extract location information
    location_selectors = [
        '.location', '.job-location', '[data-automation="jobLocation"]',
        '[itemprop="jobLocation"]', '.job-info-location', '.jobLocation',
        '.job-metadata-location', '[data-test="job-location"]'
    ]
    info['location'] = text_or_none(soup, location_selectors)
    
    # Try regex if no location found with selectors
    if not info.get('location'):
        location_patterns = [
            r'Location:\s*([^,\n]+),?',
            r'Job Location:?\s*([^,\n]+),?',
            r'Located in:?\s*([^,\n]+),?'
        ]
        info['location'] = regex_search(soup.get_text(), location_patterns)
    
    # Extract company information
    company_selectors = [
        '.company-name', '.employer-name', '[data-automation="jobEmployer"]',
        '[itemprop="hiringOrganization"]', '.CompanyName', '.company',
        '[data-test="company-name"]', '.job-company', '.JobCompany'
    ]
    info['company'] = text_or_none(soup, company_selectors)
    
    # Clean up description if it exists
    if info.get('description'):
        # Remove extra whitespace
        info['description'] = re.sub(r'\s+', ' ', info['description']).strip()
        
    return {k: v for k, v in info.items() if v}

def text_or_none(soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
    """
    Extract text from the first matching selector or return None.
    """
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            return element.get_text(separator=' ', strip=True)
    return None

def link_or_none(soup: BeautifulSoup, selector: str, base: Optional[str] = None) -> Optional[str]:
    """
    Extract a link from the first matching selector or return None.
    """
    from urllib.parse import urljoin
    element = soup.select_one(selector)
    if element:
        link = element.get('href')
        return urljoin(base, link) if base and link else link
    return None

def regex_search(text: str, patterns: List[str]) -> Optional[str]:
    """
    Search for the first match of any pattern in the text.
    """
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None
