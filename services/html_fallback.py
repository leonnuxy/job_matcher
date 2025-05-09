# html_fallback.py

import os
import re
import logging
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from .config import REQUEST_TIMEOUT
from .config import USER_AGENT
from .utils import regex_search
from urllib.parse import urljoin, urlparse
import requests



SIMULATION_MODE = os.getenv("SIMULATION_MODE", "false").lower() in ("true", "1", "yes")
session = requests.Session()


def extract_job_listings(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    domain = urlparse(base_url).netloc.lower()
    if "linkedin.com"   in domain: return _extract_linkedin(soup)
    if "indeed."       in domain: return _extract_indeed(soup)
    if "glassdoor.com" in domain: return _extract_glassdoor(soup)
    return _extract_generic(soup, base_url)

# implement _extract_linkedin, _extract_indeed, _extract_glassdoor, _extract_generic
# exactly as you had before, but *only* listing code.

def _text_or_none(soup: BeautifulSoup, selectors: List[str]) -> Optional[str]:
    """
    Extract text from the first matching selector or return None.
    """
    for selector in selectors:
        element = soup.select_one(selector)
        if element:
            return element.get_text(strip=True)
    return None


def _link_or_none(soup: BeautifulSoup, selector: str, base: Optional[str] = None) -> Optional[str]:
    """
    Extract a link from the first matching selector or return None.
    """
    element = soup.select_one(selector)
    if element and element.has_attr('href'):
        href = element['href']
        return urljoin(base, href) if base else href
    return None

def _extract_linkedin(soup: BeautifulSoup) -> List[Dict]:
    jobs = []
    for card in soup.select('.job-card-container, .jobs-search-results__list-item'):
        title = _text_or_none(card, ['.job-card-list__title', '.job-card-container__link'])
        link  = _link_or_none(card, 'a.job-card-container__link', base='https://www.linkedin.com')
        comp  = _text_or_none(card, ['.job-card-container__company-name', '.jobs-search-results__company-name'])
        loc   = _text_or_none(card, ['.job-card-container__metadata-item', '.job-card-container__metadata-location'])
        if title and link:
            jobs.append({'title': title, 'company': comp, 'location': loc, 'link': link})
    return jobs


def _extract_indeed(soup: BeautifulSoup) -> List[Dict]:
    jobs = []
    for card in soup.select('.job_seen_beacon, .jobsearch-ResultsList > div'):
        title = _text_or_none(card, ['.jobTitle', '.jcs-JobTitle'])
        link  = _link_or_none(card, 'a.jcs-JobTitle', base='https://www.indeed.com')
        comp  = _text_or_none(card, ['.companyName'])
        loc   = _text_or_none(card, ['.companyLocation'])
        snippet = _text_or_none(card, ['.job-snippet', '.job-snippet-container'])
        if title and link:
            jobs.append({'title': title, 'company': comp, 'location': loc, 'link': link, 'snippet': snippet})
    return jobs


def _extract_glassdoor(soup: BeautifulSoup) -> List[Dict]:
    jobs = []
    for card in soup.select('.react-job-listing, .jobListItem'):
        title = _text_or_none(card, ['.job-title', '.jobTitle'])
        job_id = card.get('data-id')
        link = f'https://www.glassdoor.com/job-listing/{job_id}' if job_id else None
        comp  = _text_or_none(card, ['.jobInfoItem', '.employerName'])
        loc   = _text_or_none(card, ['.jobInfoItem', '.location'])
        snippet = _text_or_none(card, ['.job-snippet', '.jobDescriptionContent'])
        if title and link:
            jobs.append({'title': title, 'company': comp, 'location': loc, 'link': link, 'snippet': snippet})
    return jobs


def _extract_generic(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    jobs = []
    for card in soup.select('.job-listing, .job-card'):
        title = _text_or_none(card, ['.job-title', '.title'])
        link  = _link_or_none(card, 'a.job-link', base=base_url)
        comp  = _text_or_none(card, ['.company-name', '.company'])
        loc   = _text_or_none(card, ['.location', '.job-location'])
        snippet = _text_or_none(card, ['.job-snippet', '.description'])
        if title and link:
            jobs.append({'title': title, 'company': comp, 'location': loc, 'link': link, 'snippet': snippet})
    return jobs

# parse details:
def extract_job_details(job_url: str, job_info: Optional[Dict] = None) -> Dict:
    """
    Scrape or reuse snippet for detailed job info, with graceful fallback on errors.
    
    Args:
        job_url: URL of the job posting to scrape
        job_info: Optional dictionary with existing job information (e.g., snippet)
        
    Returns:
        Dictionary containing extracted job details, with at minimum a description if available
    """
    # In simulation mode, return full description if available
    if SIMULATION_MODE and job_info:
        if job_info.get("full_description"):
            return {"description": job_info["full_description"]}
        elif job_info.get("description"):
            return {}

    # If the snippet is already substantial, use it without making a request
    if job_info and job_info.get("snippet") and len(job_info["snippet"]) > 100:
        return {"description": job_info["snippet"]}

    # Skip common URLs that are known to block scraping or require login
    if any(blocker in job_url.lower() for blocker in [
        'linkedin.com/jobs', 'glassdoor.com/job', 'dice.com/job-detail'
    ]):
        logging.debug(f"Skipping fetch for {job_url} - known to block scraping")
        if job_info and job_info.get("snippet"):
            return {"description": job_info["snippet"]}
        return {}

    # Try to fetch the job details from the URL
    try:
        logging.debug(f"Fetching details from {job_url}")
        
        # Use a more browser-like headers to avoid detection
        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        resp = session.get(job_url, headers=headers, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        
        # Parse the HTML response
        soup = BeautifulSoup(resp.text, 'lxml')
        job_details = _parse_job_details(soup)
        
        # If we got a description, return it
        if job_details.get('description'):
            return job_details
        
        # If no description found but we have a snippet, use that
        if not job_details.get('description') and job_info and job_info.get("snippet"):
            job_details['description'] = job_info["snippet"]
            
        return job_details
    
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response else None
        if status in (403, 429, 401, 404):
            logging.debug(f"Access blocked (status {status}) for {job_url}, using snippet if available")
        else:
            logging.warning(f"HTTP error {status} extracting details from {job_url}")
            
        # Fall back to snippet if available
        if job_info and job_info.get("snippet"):
            return {"description": job_info["snippet"]}
        return {}
        
    except requests.exceptions.Timeout:
        logging.debug(f"Timeout fetching details from {job_url}, using snippet if available")
        if job_info and job_info.get("snippet"):
            return {"description": job_info["snippet"]}
        return {}
        
    except Exception as e:
        logging.warning(f"Error extracting details from {job_url}: {type(e).__name__} - {str(e)}")
        if job_info and job_info.get("snippet"):
            return {"description": job_info["snippet"]}
        return {}
    

def _parse_job_details(soup: BeautifulSoup) -> Dict:
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
        'section.description', 'div[class*="description"]',
        '.job-details-content', '.job-posting-content',
        '.job-view-content', 'article.job-details',
        '.job-body', '.job-listing-body', '.position-summary'
    ]
    info['description'] = _text_or_none(soup, description_selectors)
    
    # If no description found with selectors, try to find it in the page content
    if not info.get('description'):
        # Look for common container headings and extract content after them
        description_heading_patterns = [
            (r'<h[1-3][^>]*>Job Description</h[1-3]>(.*?)<h[1-3]', 1),
            (r'<h[1-3][^>]*>Description</h[1-3]>(.*?)<h[1-3]', 1),
            (r'<h[1-4][^>]*>About the role</h[1-4]>(.*?)<h[1-4]', 1),
            (r'<h[1-4][^>]*>About the job</h[1-4]>(.*?)<h[1-4]', 1),
            (r'<h[1-4][^>]*>What you\'ll do</h[1-4]>(.*?)<h[1-4]', 1),
            (r'<h[1-4][^>]*>Responsibilities</h[1-4]>(.*?)<h[1-4]', 1),
            (r'<strong>Job Description:?</strong>(.*?)(?:<strong>|<h[1-4])', 1),
            (r'<div[^>]*>Description</div>(.*?)(?:<div[^>]*>|<section)', 1),
            (r'<div[^>]*>Job Details</div>(.*?)(?:<div[^>]*>|<section)', 1)
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
        
        # If still no description, try a more comprehensive approach
        if not info.get('description'):
            # Look for job description in the main content area
            main_content_sections = soup.select('main, .main-content, #main-content, article, .content-wrapper')
            if main_content_sections:
                # Analyze content and look for the largest text block that might be a description
                potential_descriptions = []
                for section in main_content_sections:
                    # Find all paragraphs and list items
                    paragraphs = section.find_all(['p', 'li', 'div'])
                    for p in paragraphs:
                        text = p.get_text(strip=True)
                        if len(text) > 100:  # Only consider substantial paragraphs
                            potential_descriptions.append(text)
                
                if potential_descriptions:
                    # Join the longest paragraphs to form a comprehensive description
                    potential_descriptions.sort(key=len, reverse=True)
                    combined_description = ' '.join(potential_descriptions[:5])  # Take up to 5 longest paragraphs
                    if len(combined_description) > 200:  # Must be substantial
                        info['description'] = combined_description
    
    # Extract location information
    location_selectors = [
        '.location', '.job-location', '[data-automation="jobLocation"]',
        '[itemprop="jobLocation"]', '.job-info-location', '.jobLocation',
        '.job-metadata-location', '[data-test="job-location"]'
    ]
    info['location'] = _text_or_none(soup, location_selectors)
    
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
    info['company'] = _text_or_none(soup, company_selectors)
    
    # Clean up description if it exists
    if info.get('description'):
        # Remove extra whitespace
        info['description'] = re.sub(r'\s+', ' ', info['description']).strip()
        
    return {k: v for k, v in info.items() if v}



