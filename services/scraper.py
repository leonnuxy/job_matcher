# lib/scraper.py
"""
Robust job board scraper with retry logic, Google CSE support, simulated data mode,
HTML fallback scraping, and unified extraction patterns.
"""
import os
import logging
import re
import random
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Constants
USER_AGENT = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/91.0.4472.124 Safari/537.36'
)
REQUEST_TIMEOUT = 10  # seconds
RETRY_STRATEGY = Retry(
    total=3,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504]
)
SIMULATION_MODE = os.getenv("SIMULATION_MODE", "false").lower() in ("true", "1", "yes")
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID  = os.getenv('GOOGLE_CSE_ID')

# Create a session with retry logic
session = requests.Session()
adapter = HTTPAdapter(max_retries=RETRY_STRATEGY)
session.mount('http://', adapter)
session.mount('https://', adapter)


def search_google_for_jobs(
    term: str,
    location: str = "",
    recency_hours: float = 24,
    cse_id: Optional[str] = None
) -> List[Dict]:
    """
    Search jobs via Google Custom Search API with optional recency filter.
    Returns list of job dicts with keys: title, company, location, link, snippet.
    """
    engine_id = cse_id or GOOGLE_CSE_ID
    if not GOOGLE_API_KEY or not engine_id:
        logging.error("Missing Google CSE credentials")
        return []

    query = f"{term} job"
    if location:
        query += f" in {location}"

    params = {"key": GOOGLE_API_KEY, "cx": engine_id, "q": query, "num": 10}
    # dateRestrict: h1, d1-d7, w1-wN
    if recency_hours > 0:
        if recency_hours <= 1:
            params["dateRestrict"] = "h1"
        elif recency_hours <= 24:
            params["dateRestrict"] = "d1"
        elif recency_hours <= 168:
            days = max(1, int(recency_hours / 24))
            params["dateRestrict"] = f"d{days}"
        else:
            weeks = max(1, int(recency_hours / 168))
            params["dateRestrict"] = f"w{weeks}"

    try:
        logging.info(f"Google CSE: '{query}' recency={recency_hours}h")
        resp = session.get(
            "https://www.googleapis.com/customsearch/v1",
            params=params,
            timeout=REQUEST_TIMEOUT
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])

        jobs: List[Dict] = []
        for item in items:
            raw_title = item.get("title", "").strip()
            link = item.get("link", "")
            snippet = item.get("snippet", "").strip()
            
            # First clean up the title to remove dates, page numbers, etc.
            title = clean_job_title(raw_title, snippet)
            
            # Clean up snippet - remove timestamps and common prefixes
            snippet = clean_job_snippet(snippet)
            
            # Extract company name using various strategies
            company = extract_company_name(title, snippet, link)
                
            # Clean up location name
            loc_name = location.strip() if location else "Not specified"
            
            jobs.append({
                "title": title,
                "company": company,
                "location": location or "Not specified",
                "link": link,
                "snippet": snippet
            })
        return jobs
    except Exception as e:
        logging.error(f"Google search failed: {e}")
        return []


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


def extract_company_name(title: str, snippet: str, link: str) -> str:
    """
    Extract company name using multiple strategies.
    
    Args:
        title: The job title string
        snippet: Job snippet text that might contain company information
        link: URL of the job posting, which might contain company name
        
    Returns:
        company_name: The extracted company name or "Unknown"
    """
    # Strategy 1: Look for common patterns in the title
    company_match = re.search(r'\s+(?:at|@)\s+([A-Z][A-Za-z0-9\s&\.\']+?)(?:\s+in|$)', title)
    if company_match:
        company = company_match.group(1).strip()
        if is_valid_company_name(company):
            return company
    
    # Strategy 2: Look for common patterns in snippet ("Company Name is seeking...")
    hiring_pattern = re.search(r'([A-Z][A-Za-z0-9\s&\.\']+?)\s+is\s+(?:seeking|looking|hiring|searching)', snippet)
    if hiring_pattern:
        company = hiring_pattern.group(1).strip()
        if is_valid_company_name(company):
            return company
    
    # Strategy 3: Extract from URL
    url_company = extract_company_from_url(link)
    if url_company != "Unknown":
        return url_company
    
    # Strategy 4: Look for " - Company Name" pattern in title
    title_company = re.search(r'\s+(?:-|–|—)\s+([A-Z][A-Za-z0-9\s&\.\']+)$', title)
    if title_company:
        company = title_company.group(1).strip()
        if is_valid_company_name(company):
            return company
            
    # Strategy 5: Look for company in snippet that is capitalized
    potential_companies = [
        m.group() for m in re.finditer(r'[A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+){0,3}', snippet)
        if len(m.group()) > 2 and m.group().lower() not in [
            'job', 'description', 'position', 'experience', 'skills', 'required',
            'usa', 'united states', 'new york', 'remote', 'hybrid', 'onsite',
            'bachelor', 'master', 'phd', 'javascript', 'typescript', 'python',
            'monday', 'tuesday', 'wednesday', 'thursday', 'friday'
        ]
    ]
    
    for company in potential_companies:
        if is_valid_company_name(company):
            return company
            
    return "Unknown"


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


def scrape_job_board(url: str) -> List[Dict]:
    """
    Main entry: returns simulated, Google-CSE, or HTML-scraped listings.
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    term = params.get('keywords', params.get('q', ['']))[0].replace('+', ' ')
    loc = params.get('location', params.get('l', ['']))[0].replace('+', ' ')

    if SIMULATION_MODE:
        logging.info(f"[SIMULATION] {term} in {loc}")
        return generate_simulated_jobs(term)

    if GOOGLE_API_KEY and GOOGLE_CSE_ID:
        return search_google_for_jobs(term, loc)

    # HTML fallback
    try:
        logging.info(f"HTML scrape: {url}")
        resp = session.get(url, headers={'User-Agent': USER_AGENT}, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'lxml')
        return extract_job_listings(soup, url)
    except Exception as e:
        logging.error(f"Fallback scrape failed: {e}")
        return []


def generate_simulated_jobs(search_term: str) -> List[Dict]:
    """
    Produce fake listings for offline development.
    """
    parts = search_term.split()
    title = " ".join(parts[:-1]) if len(parts) > 1 else parts[0]
    loc = parts[-1] if len(parts) > 1 else "Remote"
    companies = ["TechCorp", "DataSoft", "InnovateTech", "CloudWave", "QuantumCode"]
    jobs: List[Dict] = []
    for i in range(random.randint(3, 6)):
        comp = random.choice(companies)
        desc = f"{comp} is seeking a {title} in {loc}."
        jobs.append({
            "title": title,
            "company": comp,
            "location": loc,
            "link": f"https://example.com/job/{i}",
            "description": desc,
            "snippet": desc
        })
    return jobs


def extract_job_details(job_url: str, job_info: Optional[Dict] = None) -> Dict:
    """
    Scrape or reuse snippet for detailed job info, with graceful fallback on errors.
    
    Args:
        job_url: URL of the job posting to scrape
        job_info: Optional dictionary with existing job information (e.g., snippet)
        
    Returns:
        Dictionary containing extracted job details, with at minimum a description if available
    """
    # In simulation mode, return empty dict if description already exists
    if SIMULATION_MODE and job_info and job_info.get("description"):
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


def extract_job_listings(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    domain = urlparse(base_url).netloc.lower()
    if 'linkedin.com' in domain:
        return _extract_linkedin(soup)
    if 'indeed.' in domain:
        return _extract_indeed(soup)
    if 'glassdoor.com' in domain:
        return _extract_glassdoor(soup)
    return _extract_generic(soup, base_url)


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
        'section.description', 'div[class*="description"]'
    ]
    info['description'] = _text_or_none(soup, description_selectors)
    
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
    info['location'] = _text_or_none(soup, location_selectors)
    
    # Try regex if no location found with selectors
    if not info.get('location'):
        location_patterns = [
            r'Location:\s*([^,\n]+),?',
            r'Job Location:?\s*([^,\n]+),?',
            r'Located in:?\s*([^,\n]+),?'
        ]
        info['location'] = _regex_search(soup.get_text(), location_patterns)
    
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


def _regex_search(text: str, patterns: List[str]) -> Optional[str]:
    """
    Search for the first match of any pattern in the text.
    """
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return match.group(1).strip()
    return None


def ensure_job_descriptions(jobs: List[Dict], min_description_length: int = 50) -> List[Dict]:
    """
    Ensure all jobs have a valid description, either from the job details or snippet.
    
    Args:
        jobs: List of job dictionaries
        min_description_length: Minimum acceptable description length
        
    Returns:
        List of jobs with valid descriptions
    """
    enriched_jobs = []
    already_good = 0
    enriched_from_details = 0
    enriched_from_snippet = 0
    skipped_jobs = 0
    
    for job in jobs:
        job_title = job.get("title", "Unknown job")
        
        # Skip if the job already has a good description
        if job.get("description") and len(job["description"]) >= min_description_length:
            enriched_jobs.append(job)
            already_good += 1
            continue
        
        # Try to fetch additional details
        has_valid_description = False
        
        # Only try to fetch if we have a link
        if job.get("link"):
            # Try to get detailed description from the job page
            job_details = extract_job_details(job["link"], job)
            if job_details.get("description") and len(job_details["description"]) >= min_description_length:
                job["description"] = job_details["description"]
                has_valid_description = True
                enriched_from_details += 1
                logging.debug(f"Enhanced description for '{job_title}' by fetching details")
        
        # Fall back to snippet if available and no valid description yet
        if not has_valid_description and job.get("snippet") and len(job["snippet"]) >= min_description_length:
            job["description"] = job["snippet"]
            has_valid_description = True
            enriched_from_snippet += 1
            logging.debug(f"Used snippet as description for '{job_title}'")
            
        # If we still don't have a valid description, check if we have any description at all
        if not has_valid_description and not job.get("description"):
            # Last resort: use snippet even if it's short
            if job.get("snippet"):
                job["description"] = job["snippet"]
                has_valid_description = True
                enriched_from_snippet += 1
                logging.debug(f"Used short snippet as description for '{job_title}'")
        
        # Only keep jobs that have some form of description
        if job.get("description"):
            enriched_jobs.append(job)
        else:
            skipped_jobs += 1
            logging.debug(f"Skipping job '{job_title}' - no valid description")
    
    # Log summary of enrichment process
    logging.info(f"Description enrichment summary:")
    logging.info(f"  - {already_good} jobs already had good descriptions")
    logging.info(f"  - {enriched_from_details} jobs enriched from detailed page extraction")
    logging.info(f"  - {enriched_from_snippet} jobs enriched from snippets")
    
    if skipped_jobs > 0:
        logging.info(f"  - {skipped_jobs} jobs skipped due to no valid description")
    
    return enriched_jobs
