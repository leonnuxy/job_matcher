# lib/scraper.py
import re
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_job_board(url):
    """
    Scrape job listings from a job board using BeautifulSoup.
    
    Args:
        url (str): URL of the job board to scrape
    
    Returns:
        list: List of job listings with extracted information
    """
    logging.info(f"Scraping job board at: {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        return extract_job_listings(soup, url)
    except Exception as e:
        logging.error(f"Error scraping job board: {e}")
        return []

def extract_job_listings(soup, base_url):
    """
    Extract job listings from a BeautifulSoup object.
    This is a placeholder implementation that should be customized for each job board.
    
    Args:
        soup (BeautifulSoup): Parsed HTML soup
        base_url (str): Base URL of the job board
        
    Returns:
        list: List of job listings with extracted information
    """
    domain = urlparse(base_url).netloc
    job_listings = []
    
    # Different extraction logic based on the domain
    if 'linkedin.com' in domain:
        job_listings = extract_linkedin_jobs(soup)
    elif 'indeed.com' in domain or 'indeed.ca' in domain:
        job_listings = extract_indeed_jobs(soup)
    elif 'glassdoor.com' in domain:
        job_listings = extract_glassdoor_jobs(soup)
    else:
        # Generic extraction logic
        job_listings = extract_generic_jobs(soup)
    
    return job_listings

def extract_job_details(job_url):
    """
    Extract detailed job information from a specific job listing page.
    
    Args:
        job_url (str): URL of the job details page
    
    Returns:
        dict: Detailed job information including description, requirements, and location
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(job_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract job details based on common patterns
        job_info = {}
        
        # Look for job description
        description_elements = soup.select('.job-description, .description, [data-automation="jobDescription"]')
        if description_elements:
            job_info['description'] = description_elements[0].get_text(strip=True)
        
        # Look for location information
        location_elements = soup.select('.location, .job-location, [data-automation="jobLocation"]')
        if location_elements:
            job_info['location'] = location_elements[0].get_text(strip=True)
        else:
            # Try to find location using regex patterns
            text = soup.get_text()
            location_patterns = [
                r'Location:\s*([^,\n]+),\s*([A-Za-z]{2})',
                r'located in\s+([^,\n]+),\s*([A-Za-z]{2})',
            ]
            for pattern in location_patterns:
                match = re.search(pattern, text)
                if match:
                    job_info['location'] = f"{match.group(1)}, {match.group(2)}"
                    break
        
        # Look for company name
        company_elements = soup.select('.company-name, .employer-name, [data-automation="jobEmployer"]')
        if company_elements:
            job_info['company'] = company_elements[0].get_text(strip=True)
        
        return job_info
        
    except Exception as e:
        logging.error(f"Error extracting job details from {job_url}: {e}")
        return {}

def extract_linkedin_jobs(soup):
    """Extract job listings from LinkedIn search results."""
    job_listings = []
    
    # Look for job cards - LinkedIn's structure changes often, so we try multiple selectors
    job_cards = soup.select('.job-card-container, .jobs-search-results__list-item')
    
    for card in job_cards:
        job = {}
        
        # Extract title
        title_elem = card.select_one('.job-card-list__title, .job-card-container__link')
        if title_elem:
            job['title'] = title_elem.get_text(strip=True)
        
        # Extract company
        company_elem = card.select_one('.job-card-container__company-name, .job-card-container__primary-description')
        if company_elem:
            job['company'] = company_elem.get_text(strip=True)
        
        # Extract location
        location_elem = card.select_one('.job-card-container__metadata-item, .job-card-container__metadata-location')
        if location_elem:
            job['location'] = location_elem.get_text(strip=True)
        
        # Extract link
        link_elem = card.select_one('a.job-card-container__link')
        if link_elem and link_elem.has_attr('href'):
            job['link'] = 'https://www.linkedin.com' + link_elem['href'] if not link_elem['href'].startswith('http') else link_elem['href']
        
        # Only add if we have at least title and link
        if job.get('title') and job.get('link'):
            job_listings.append(job)
    
    return job_listings

def extract_indeed_jobs(soup):
    """Extract job listings from Indeed search results."""
    job_listings = []
    
    # Look for job cards
    job_cards = soup.select('.job_seen_beacon, .jobsearch-ResultsList > div')
    
    for card in job_cards:
        job = {}
        
        # Extract title
        title_elem = card.select_one('.jobTitle, .jcs-JobTitle')
        if title_elem:
            job['title'] = title_elem.get_text(strip=True)
        
        # Extract company
        company_elem = card.select_one('.company_location .companyName, .companyName')
        if company_elem:
            job['company'] = company_elem.get_text(strip=True)
        
        # Extract location
        location_elem = card.select_one('.company_location .companyLocation, .companyLocation')
        if location_elem:
            job['location'] = location_elem.get_text(strip=True)
        
        # Extract link
        link_elem = card.select_one('a.jcs-JobTitle')
        if link_elem and link_elem.has_attr('href'):
            href = link_elem['href']
            job['link'] = 'https://www.indeed.com' + href if href.startswith('/') else href
        
        # Extract snippet/description
        snippet_elem = card.select_one('.job-snippet, .job-snippet-container')
        if snippet_elem:
            job['snippet'] = snippet_elem.get_text(strip=True)
        
        # Only add if we have at least title and link
        if job.get('title') and job.get('link'):
            job_listings.append(job)
    
    return job_listings

def extract_glassdoor_jobs(soup):
    """Extract job listings from Glassdoor search results."""
    job_listings = []
    
    # Look for job cards
    job_cards = soup.select('.react-job-listing, .jobListItem')
    
    for card in job_cards:
        job = {}
        
        # Extract title
        title_elem = card.select_one('.job-title, .jobTitle')
        if title_elem:
            job['title'] = title_elem.get_text(strip=True)
        
        # Extract company
        company_elem = card.select_one('.employer-name, .jobEmpolyerName')
        if company_elem:
            job['company'] = company_elem.get_text(strip=True)
        
        # Extract location
        location_elem = card.select_one('.location, .loc')
        if location_elem:
            job['location'] = location_elem.get_text(strip=True)
        
        # Extract link - Glassdoor often uses JS for navigation, so this might need adjustment
        if card.has_attr('data-id'):
            job_id = card['data-id']
            job['link'] = f'https://www.glassdoor.com/job-listing/{job_id}'
        
        # Only add if we have at least title
        if job.get('title'):
            job_listings.append(job)
    
    return job_listings

def extract_generic_jobs(soup):
    """
    Generic extraction logic that looks for common patterns in job listings.
    This is a fallback for unsupported job boards.
    """
    job_listings = []
    
    # Look for common job card patterns
    job_cards = soup.select('.job-card, .job-listing, .job-result, article, .card')
    
    for card in job_cards:
        job = {}
        
        # Extract title - look for h2, h3 or elements with 'title' in class
        title_elem = card.select_one('h2, h3, [class*="title" i]')
        if title_elem:
            job['title'] = title_elem.get_text(strip=True)
        
        # Extract company
        company_elem = card.select_one('[class*="company" i], [class*="employer" i]')
        if company_elem:
            job['company'] = company_elem.get_text(strip=True)
        
        # Extract location
        location_elem = card.select_one('[class*="location" i]')
        if location_elem:
            job['location'] = location_elem.get_text(strip=True)
        
        # Extract link
        link_elem = card.select_one('a')
        if link_elem and link_elem.has_attr('href'):
            job['link'] = link_elem['href']
        
        # Only add if we have at least title
        if job.get('title'):
            job_listings.append(job)
    
    return job_listings
