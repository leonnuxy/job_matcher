# google_cse.py

import logging
import re
from typing import List, Dict, Optional
from .config import GOOGLE_API_KEY, GOOGLE_CSE_ID, REQUEST_TIMEOUT
from .http_client import SESSION
from .utils import clean_job_title, clean_job_snippet, is_valid_company_name, extract_company_from_url
from .utils import regex_search

def _map_recency(hours: float) -> str:
    if hours <= 1:   return "h1"
    if hours <= 24:  return "d1"
    if hours <= 168: return f"d{max(1,int(hours/24))}"
    return f"w{max(1,int(hours/168))}"


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


def search_google_for_jobs(
    term: str,
    location: str="",
    recency_hours: float=24,
    cse_id: Optional[str]=None
) -> List[Dict]:
    engine = cse_id or GOOGLE_CSE_ID
    if not GOOGLE_API_KEY or not engine:
        logging.error("Missing Google CSE credentials")
        return []
    q = f"{term} job" + (f" in {location}" if location else "")
    params = {
        "key": GOOGLE_API_KEY,
        "cx": engine,
        "q": q,
        "num": 10,
        "dateRestrict": _map_recency(recency_hours)
    }
    try:
        logging.info(f"Google CSE search: '{q}' ({recency_hours}h)")
        r = SESSION.get("https://www.googleapis.com/customsearch/v1",
                        params=params, timeout=REQUEST_TIMEOUT)
        r.raise_for_status()
        items = r.json().get("items", [])
    except Exception as e:
        logging.error(f"Google search failed for '{q}': {e}")
        return []

    jobs = []
    for it in items:
        raw_title = it.get("title","")
        snippet   = it.get("snippet","")
        link      = it.get("link","")
        title     = clean_job_title(raw_title, snippet)
        snippet   = clean_job_snippet(snippet)
        # simple company fallback:
        company   = extract_company_name(title, snippet, link)
        jobs.append({
            "title": title,
            "company": company,
            "location": location or "Not specified",
            "link": link,
            "snippet": snippet
        })
    return jobs
