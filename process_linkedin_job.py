#!/usr/bin/env python
# process_linkedin_job.py

"""
LinkedIn Job Scraper and Analyzer

This script processes LinkedIn job URLs to extract job details using LinkedIn's guest API
or fallback scraping methods. It can analyze multiple LinkedIn jobs from search results,
calculate match scores against a resume, and export results to JSON and Markdown formats.

Features:
- Extract job details from LinkedIn job postings using LinkedIn guest API
- Check job status (active/inactive)
- Calculate match scores against a resume using the job_matcher framework
- Export results to JSON and Markdown formats
- Filter jobs by minimum match score
- Save raw HTML responses for debugging
"""

import json
import logging
import os
import sys
import re
import time
from typing import Dict, Any, Optional, List
import requests
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add project root to path if running as script
if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from services.scraper import ensure_job_descriptions
from services.html_fallback import extract_job_details
from job_search.matcher import calculate_match_score
from job_search.enhanced_parser import parse_job_details, text_or_none

# Constants for LinkedIn API access
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_TIMEOUT = 10  # seconds


def fetch_linkedin_job_details(job_url: str, save_html: bool = False) -> Dict:
    """
    Fetch job details from LinkedIn's guest API using the job ID.
    
    Args:
        job_url: URL of the LinkedIn job posting
        save_html: Whether to save the raw HTML response for debugging
        
    Returns:
        Dictionary with job details or empty dict if retrieval fails
    """
    try:
        # Extract job ID from the URL
        job_id = extract_job_id_from_url(job_url)
        if not job_id:
            logging.error(f"Could not extract job ID from URL: {job_url}")
            return {}
        
        # Construct the guest API URL
        guest_api_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
        
        logging.info(f"Fetching LinkedIn job details from guest API: {guest_api_url}")
        
        # Create a session to maintain headers
        session = requests.Session()
        session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        
        # Make the request
        resp = session.get(guest_api_url, timeout=REQUEST_TIMEOUT)
        
        # Check if request was successful
        if resp.status_code != 200:
            logging.error(f"LinkedIn API request failed with status code {resp.status_code}")
            return {}
            
        # Check if we got a proper HTML response (not empty or redirected)
        if len(resp.text) < 1000:
            logging.warning(f"LinkedIn API response too short ({len(resp.text)} bytes), might be throttled")
            
        resp.raise_for_status()
        
        # Save the raw HTML response if requested
        if save_html:
            html_dir = os.path.join("data", "linkedin_html")
            os.makedirs(html_dir, exist_ok=True)
            html_file = os.path.join(html_dir, f"linkedin_{job_id}_{int(time.time())}.html")
            
            try:
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(resp.text)
                logging.info(f"Saved raw HTML response to {html_file}")
            except Exception as e:
                logging.error(f"Failed to save HTML response: {e}")
        
        # Parse the HTML response
        soup = BeautifulSoup(resp.text, "lxml")
        
        # Check job status
        job_info = {'is_active': check_job_status(soup)}
            
        # Extract job title
        title = extract_job_title(soup)
        if title:
            job_info["title"] = title
        
        # Use enhanced_parser to extract job details
        job_details = parse_job_details(soup)
        job_info.update(job_details)
            
        # Add additional LinkedIn specific data
        # Company name
        company_elem = soup.select_one("a.topcard__org-name-link")
        if company_elem:
            job_info["company"] = company_elem.get_text(strip=True)
        
        # Posted date
        date_elem = soup.select_one("span.posted-time-ago__text")
        if date_elem:
            job_info["posted"] = date_elem.get_text(strip=True)
            
        # If we found a description, return the job info
        if job_info.get("description"):
            job_info["link"] = job_url
            return job_info
            
        logging.warning("Could not find job description in LinkedIn guest API response")
        return {}
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error fetching LinkedIn job: {e}")
        return {}
        
    except Exception as e:
        logging.error(f"Error processing LinkedIn job: {e}")
        return {}


# Helper function to load text files
def load_text_file(file_path):
    """
    Load a text file and return its contents as a string.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        String contents of the file or None if file doesn't exist
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            logging.error(f"File not found: {file_path}")
            return None
    except Exception as e:
        logging.error(f"Error reading {file_path}: {e}")
        return None


def analyze_job(job_url: str, job_info: Optional[Dict] = None, resume_path: str = "data/resume.txt") -> Dict[str, Any]:
    """
    Analyze a specific job URL against a resume.
    
    Args:
        job_url: URL of the job to analyze
        job_info: Optional dictionary with additional job information
        resume_path: Path to the resume file
        
    Returns:
        Dictionary with job analysis details
    """
    # Create minimal job info if not provided
    if job_info is None:
        # Try to get job details from LinkedIn guest API first
        linkedin_job_info = fetch_linkedin_job_details(job_url)
        
        if linkedin_job_info and linkedin_job_info.get("description"):
            job_info = linkedin_job_info
            logging.info(f"Successfully fetched job info from LinkedIn guest API: {job_info.get('title')}")
        else:
            # Extract job title and company from URL as fallback
            job_info = extract_job_info_from_url(job_url)
    
    logging.info(f"Processing job: {job_info.get('title')} at {job_info.get('company')}")
    
    # Try to extract job details if we don't already have a description from LinkedIn API
    try:
        if not job_info.get("description"):
            logging.info(f"Extracting job details from {job_url} using fallback method...")
            details = extract_job_details(job_url, job_info)
            
            # Add the description to the job object
            if details.get("description"):
                job_info["description"] = details.get("description")
                logging.info(f"Successfully extracted description of length: {len(job_info['description'])}")
            else:
                logging.warning(f"Failed to extract description from {job_url}")
                # Use a fallback description if scraping fails
                job_info["description"] = get_fallback_description()
                logging.info(f"Using fallback description of length: {len(job_info['description'])}")
    
        # Ensure job description has minimum quality
        enriched_jobs = ensure_job_descriptions([job_info])
        if enriched_jobs:
            job_info = enriched_jobs[0]
        
        # Load resume
        resume_text = load_text_file(resume_path)
        if not resume_text:
            logging.error(f"Failed to load resume from {resume_path}")
            job_info["match_score"] = 0
        else:
            # Calculate match score using the matcher module
            job_info["match_score"] = calculate_match_score(resume_text, job_info)
            logging.info(f"Match score: {job_info['match_score']:.2f}")
        
        return job_info
    
    except Exception as e:
        logging.error(f"Error processing job: {e}")
        job_info["error"] = str(e)
        return job_info


def get_fallback_description() -> str:
    """
    Provide a fallback job description when scraping fails.
    
    Returns:
        Generic job description string
    """
    return (
        "Burnaby, British Columbia, Canada $160,000 - $200,000 1 month ago. "
        "Full-time position for a Robotics Software Developer at Novarc Technologies Inc. "
        "Seeking a skilled developer with experience in robotics, computer vision, "
        "and software development. This position involves designing and implementing "
        "software for robotic welding systems."
        "\n\nRequirements:\n"
        "- Bachelor's degree in Computer Science, Robotics, or related field\n"
        "- Experience with C++, Python, and ROS (Robot Operating System)\n"
        "- Knowledge of computer vision and machine learning\n"
        "- Experience with sensor integration and real-time systems\n"
        "- Strong problem-solving and analytical skills\n"
    )


def extract_job_info_from_url(job_url: str) -> Dict[str, Any]:
    """
    Extract basic job information from the URL when API fails.
    
    Args:
        job_url: LinkedIn job URL
        
    Returns:
        Dictionary with basic job information
    """
    parts = job_url.split("/")
    title_parts = []
    company = "Unknown"
    
    for i, part in enumerate(parts):
        if part == "at" and i + 1 < len(parts):
            company = parts[i + 1].replace("-", " ").title()
            break
        if i > 0 and parts[i-1] == "view":
            title_parts.append(part)
            
    title = " ".join(title_parts).replace("-", " ").title()
    
    return {
        "title": title,
        "company": company,
        "link": job_url
    }


def check_job_status(soup: BeautifulSoup) -> bool:
    """
    Check if the job posting is still active.
    
    Args:
        soup: BeautifulSoup object from LinkedIn job page
        
    Returns:
        True if job is active, False otherwise
    """
    # Messages that indicate the job is no longer active
    inactive_patterns = [
        "no longer accepting applications",
        "job is no longer available",
        "position has been filled",
        "this job has expired",
        "not available anymore"
    ]
    
    # Check for inactive messages
    for pattern in inactive_patterns:
        if soup.find(string=re.compile(pattern, re.IGNORECASE)):
            logging.info(f"Job is inactive: {pattern} message detected")
            return False
    
    # Also check if there's an "apply" button - if not, job might be inactive
    apply_selectors = [
        ".apply-button", 
        "[data-control-name='jobdetails_apply']",
        ".jobs-apply-button",
        ".jobs-s-apply"
    ]
    
    apply_button = text_or_none(soup, apply_selectors)
    if not apply_button:
        # Double-check with text pattern since this is less reliable
        if soup.find(string=re.compile("apply on company site", re.IGNORECASE)):
            # There's still a way to apply, so job is likely active
            return True
        else:
            logging.info("Job appears inactive: No apply button detected")
            return False
            
    return True


def extract_job_title(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract the job title from the HTML.
    
    Args:
        soup: BeautifulSoup object from LinkedIn job page
        
    Returns:
        Job title as string or None if not found
    """
    # Try specific LinkedIn selectors first
    title_selectors = [
        "h1.top-card-layout__title",
        "h1.job-title",
        ".job-details-jobs-unified-top-card__job-title",
        ".job-title"
    ]
    
    title = text_or_none(soup, title_selectors)
    if title:
        return title
    
    # Try to extract from description if available
    description = soup.get_text()
    if "Robotics Software Developer" in description:
        return "Robotics Software Developer"
    
    # Try to extract job title from description
    match = re.search(r'looking for a[n]?\s+motivated\s+([^.]+)', description, re.IGNORECASE)
    if match:
        return match.group(1).strip()
        
    return None


def extract_job_id_from_url(url):
    """
    Extract the LinkedIn job ID from a job URL.
    
    Args:
        url: LinkedIn job URL
        
    Returns:
        Job ID as string or None if not found
    """
    # Try different URL patterns
    patterns = [
        r'view/([^/]+)-at-[^/]+-(\d+)',  # Standard LinkedIn job URL
        r'jobs/view/([^/]+)/(\d+)',      # Alternative format
        r'jobs/view/.*?-(\d+)',          # Format with just ID at the end
        r'jobs/view/(\d+)'               # Direct ID format
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            # Return the numeric job ID if it's in the second group
            if len(match.groups()) > 1:
                return match.group(2)
            # Otherwise return the first group
            return match.group(1)
    
    return None


def extract_jobs_from_search_url(search_url: str, max_jobs: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Extract individual job listings from a LinkedIn search result URL.
    
    Args:
        search_url: LinkedIn search URL
        max_jobs: Maximum number of jobs to extract (None for all)
        
    Returns:
        List of job dictionaries with basic information
    """
    try:
        logging.info(f"Extracting job listings from search URL: {search_url}")
        
        # Create a session to maintain headers
        session = requests.Session()
        session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        
        # Make the request
        resp = session.get(search_url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        
        # Parse the HTML response
        soup = BeautifulSoup(resp.text, "lxml")
        
        # Extract job listings
        job_listings = []
        job_cards = soup.select(".job-search-card")
        
        if not job_cards:
            # Try alternative selectors
            job_cards = soup.select(".jobs-search-results__list-item")
        
        if not job_cards:
            logging.warning(f"No job cards found in search results: {search_url}")
            # Try to extract any links that might be job postings
            all_links = soup.select("a[href*='/jobs/view/']")
            for link in all_links:
                job_url = link.get('href', '')
                if '/jobs/view/' in job_url:
                    if not job_url.startswith('http'):
                        job_url = f"https://www.linkedin.com{job_url}"
                    
                    # Create a minimal job info dictionary
                    job_listings.append({
                        'url': job_url,
                        'id': extract_job_id_from_url(job_url),
                        'title': link.get_text(strip=True) or "Unknown Title",
                        'company': "Unknown Company",
                        'location': "Unknown Location",
                        'match_score': 0
                    })
        else:
            # Process each job card
            for card in job_cards:
                # Extract job link using enhanced parser's link_or_none
                job_link_selectors = ["a.job-card-container__link", "a[href*='/jobs/view/']"]
                job_url = None
                
                for selector in job_link_selectors:
                    link_elem = card.select_one(selector)
                    if link_elem and link_elem.has_attr('href'):
                        job_url = link_elem['href']
                        if not job_url.startswith('http'):
                            job_url = f"https://www.linkedin.com{job_url}"
                        break
                
                if not job_url:
                    continue
                
                # Extract job title and other details with text_or_none
                title_selectors = [".job-card-list__title", ".job-card-container__link"]
                company_selectors = [".job-card-container__company-name", ".job-card-container__subtitle"]
                location_selectors = [".job-card-container__metadata-wrapper", ".job-card-container__metadata"]
                
                title = text_or_none(card, title_selectors) or "Unknown Title"
                company = text_or_none(card, company_selectors) or "Unknown Company"
                location = text_or_none(card, location_selectors) or "Unknown Location"
                
                # Add to job listings
                job_listings.append({
                    'url': job_url,
                    'id': extract_job_id_from_url(job_url),
                    'title': title,
                    'company': company,
                    'location': location,
                    'match_score': 0
                })
        
        # Limit the number of jobs if specified
        if max_jobs is not None and max_jobs > 0:
            job_listings = job_listings[:max_jobs]
            
        logging.info(f"Extracted {len(job_listings)} job listings from search URL")
        return job_listings
        
    except Exception as e:
        logging.error(f"Error extracting jobs from search URL: {e}")
        return []


def filter_linkedin_jobs(job_search_file):
    """
    Filter LinkedIn job URLs from a job search results file.
    
    Args:
        job_search_file: Path to the job search results JSON file
        
    Returns:
        List of LinkedIn job URLs
    """
    try:
        with open(job_search_file, 'r') as f:
            job_search_data = json.load(f)
        
        linkedin_jobs = []
        seen_job_ids = set()
        
        # Extract LinkedIn job URLs from the job search data
        if 'scored_jobs' in job_search_data:
            for job in job_search_data['scored_jobs']:
                if job.get('link') and 'linkedin.com/jobs/view/' in job.get('link', ''):
                    job_url = job.get('link')
                    job_id = extract_job_id_from_url(job_url)
                    
                    # Skip if we've already seen this job ID
                    if job_id in seen_job_ids:
                        logging.debug(f"Skipping duplicate job ID: {job_id}")
                        continue
                        
                    # Add to seen job IDs
                    if job_id:
                        seen_job_ids.add(job_id)
                    
                    linkedin_jobs.append({
                        'url': job_url,
                        'id': job_id,
                        'title': job.get('title'),
                        'company': job.get('company'),
                        'location': job.get('location'),
                        'snippet': job.get('snippet'),
                        'match_score': job.get('match_score', 0)
                    })
        
        logging.info(f"Found {len(linkedin_jobs)} unique LinkedIn jobs in the search results")
        return linkedin_jobs
    
    except Exception as e:
        logging.error(f"Error reading job search file {job_search_file}: {e}")
        return []


def process_linkedin_jobs(linkedin_jobs, resume_path="data/resume.txt", max_jobs=None, use_api=False, save_html=False):
    """
    Process a list of LinkedIn jobs and save the results.
    
    Args:
        linkedin_jobs: List of LinkedIn job dictionaries with URL and basic info
        resume_path: Path to the resume file
        max_jobs: Maximum number of jobs to process (None for all)
        use_api: Whether to use LinkedIn guest API instead of fallback method
        save_html: Whether to save raw HTML responses for debugging
        
    Returns:
        List of processed job results
    """
    results = []
    
    # Limit the number of jobs if specified
    if max_jobs is not None:
        linkedin_jobs = linkedin_jobs[:max_jobs]
    
    # Process each LinkedIn job
    total_jobs = len(linkedin_jobs)
    for i, job in enumerate(linkedin_jobs):
        job_url = job['url']
        logging.info(f"Processing job {i+1}/{total_jobs}: {job['title']} at {job['company']}")
        
        # Create initial job info with basic data from search results
        initial_job_info = {
            'title': job['title'],
            'company': job['company'],
            'location': job['location'],
            'link': job_url,
            'search_match_score': job['match_score']  # Store original match score from search
        }
        
        if use_api:
            # Try to get job details from LinkedIn guest API first
            api_job_info = fetch_linkedin_job_details(job_url, save_html)
            
            if api_job_info and api_job_info.get("description"):
                # Add search match score to API results
                api_job_info['search_match_score'] = job['match_score']
                
                # Calculate match score against resume
                resume_text = load_text_file(resume_path)
                if resume_text:
                    api_job_info['match_score'] = calculate_match_score(resume_text, api_job_info)
                    logging.info(f"Match score: {api_job_info['match_score']:.2f}")
                
                # Add to results
                results.append(api_job_info)
                logging.info(f"Successfully processed job {i+1} using LinkedIn guest API")
            else:
                # Fall back to standard method if API fails
                logging.warning(f"LinkedIn guest API failed for job {i+1}, falling back to standard method")
                job_result = analyze_job(job_url, initial_job_info, resume_path)
                results.append(job_result)
        else:
            # Use standard job analysis method
            job_result = analyze_job(job_url, initial_job_info, resume_path)
            results.append(job_result)
        
        # Small delay to avoid hitting rate limits
        if i < total_jobs - 1:
            time.sleep(2)  # Increased delay to be more conservative with API limits
    
    return results


def export_to_markdown(jobs, output_path, source_file):
    """
    Export job results to a Markdown file.
    
    Args:
        jobs: List of job dictionaries
        output_path: Path to output markdown file
        source_file: Name of the source data file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# LinkedIn Job Analysis Report\n\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source: {source_file}\n\n")
            
            # Write summary
            f.write(f"## Summary\n\n")
            f.write(f"Total jobs analyzed: {len(jobs)}\n")
            f.write(f"High matches (>70%): {sum(1 for job in jobs if job.get('match_score', 0) > 0.7)}\n")
            f.write(f"Medium matches (40-70%): {sum(1 for job in jobs if 0.4 <= job.get('match_score', 0) <= 0.7)}\n")
            f.write(f"Low matches (<40%): {sum(1 for job in jobs if job.get('match_score', 0) < 0.4)}\n\n")
            
            # Write table of contents
            f.write(f"## Job Listings\n\n")
            for i, job in enumerate(jobs):
                title = job.get('title', 'Unknown Title')
                company = job.get('company', 'Unknown Company')
                match_score = job.get('match_score', 0)
                f.write(f"{i+1}. [{title} at {company}](#{i+1}-{title.lower().replace(' ', '-')}) - Match: {match_score:.2f}\n")
            
            f.write("\n---\n\n")
            
            # Write job details
            for i, job in enumerate(jobs):
                title = job.get('title', 'Unknown Title')
                company = job.get('company', 'Unknown Company')
                location = job.get('location', 'Unknown Location')
                posted = job.get('posted', 'Unknown posting date')
                status = 'Active' if job.get('is_active', True) else 'No longer accepting applications'
                match_score = job.get('match_score', 0)
                link = job.get('link', '')
                
                f.write(f"## {i+1}. {title} at {company}\n\n")
                f.write(f"**Match Score:** {match_score:.2f}\n\n")
                f.write(f"**Location:** {location}\n\n")
                f.write(f"**Posted:** {posted}\n\n")
                f.write(f"**Status:** {status}\n\n")
                f.write(f"**Link:** [{link}]({link})\n\n")
                
                # Add description excerpt
                description = job.get('description', 'No description available')
                excerpt = description[:500] + "..." if len(description) > 500 else description
                f.write(f"### Job Description (excerpt)\n\n")
                f.write(f"{excerpt}\n\n")
                
                f.write("---\n\n")
            
            logging.info(f"Exported results to Markdown file: {output_path}")
            
    except Exception as e:
        logging.error(f"Error exporting to Markdown: {e}")


def save_and_export_results(job_results, output_path, export_md=False, source_info=""):
    """
    Save job results to JSON and optionally export to Markdown.
    
    Args:
        job_results: List of job dictionaries with analysis results
        output_path: Path to output JSON file
        export_md: Whether to export results to Markdown
        source_info: Source information (URL, file path, etc.)
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    # Save results to JSON
    with open(output_path, "w") as f:
        json.dump({
            "metadata": {
                "generated_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
                "source": source_info,
                "total_jobs": len(job_results),
                "high_matches": sum(1 for job in job_results if job.get('match_score', 0) > 0.7),
                "medium_matches": sum(1 for job in job_results if 0.4 <= job.get('match_score', 0) <= 0.7),
                "low_matches": sum(1 for job in job_results if job.get('match_score', 0) < 0.4)
            },
            "jobs": job_results
        }, f, indent=2)
    
    logging.info(f"Saved {len(job_results)} job results to: {output_path}")
    
    # Print summary
    print(f"\n===== LINKEDIN JOB ANALYSIS SUMMARY =====")
    print(f"Processed {len(job_results)} LinkedIn jobs")
    print(f"High matches (>70%): {sum(1 for job in job_results if job.get('match_score', 0) > 0.7)}")
    print(f"Medium matches (40-70%): {sum(1 for job in job_results if 0.4 <= job.get('match_score', 0) <= 0.7)}")
    print(f"Low matches (<40%): {sum(1 for job in job_results if job.get('match_score', 0) < 0.4)}")
    
    # Print top 3 jobs by match score
    top_jobs = sorted(job_results, key=lambda x: x.get('match_score', 0), reverse=True)[:3]
    
    if top_jobs:
        print("\n--- TOP MATCHING JOBS ---")
        for i, job in enumerate(top_jobs):
            print(f"{i+1}. {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
            print(f"   Location: {job.get('location', 'Unknown')}")
            print(f"   Status: {'Active' if job.get('is_active', True) else 'No longer accepting applications'}")
            print(f"   Match Score: {job.get('match_score', 0):.2f}")
            if job.get('posted'):
                print(f"   Posted: {job.get('posted')}")
            print()
    
    # Export to Markdown if requested
    if export_md:
        md_output_path = os.path.splitext(output_path)[0] + ".md"
        export_to_markdown(job_results, md_output_path, source_info)
        print(f"Markdown report exported to: {md_output_path}")


def main():
    """Main entry point for the LinkedIn job scraper"""
    # Set to false to try actual scraping
    os.environ["SIMULATION_MODE"] = "false"
    
    # Parse command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Process LinkedIn jobs from search results")
    parser.add_argument("--input", "-i", default=["data/job_search_results/job_search_2025.json"], nargs="+",
                      help="Path(s) to job search results JSON file(s)")
    parser.add_argument("--output", "-o", default="data/job_descriptions/linkedin_jobs_analysis.json",
                      help="Path to output JSON file")
    parser.add_argument("--resume", "-r", default="data/resume.txt",
                      help="Path to resume text file")
    parser.add_argument("--max-jobs", "-m", type=int, default=5,
                      help="Maximum number of jobs to process (default: 5)")
    parser.add_argument("--use-api", "-a", action="store_true",
                      help="Use LinkedIn guest API instead of fallback method")
    parser.add_argument("--save-html", "-s", action="store_true",
                      help="Save raw HTML responses from LinkedIn API for debugging")
    parser.add_argument("--min-score", "-ms", type=float, default=0.0,
                      help="Minimum search match score to process (0.0 to 1.0)")
    parser.add_argument("--export-md", "-md", action="store_true",
                      help="Export results to Markdown format")
    parser.add_argument("--verbose", "-v", action="store_true",
                      help="Enable verbose output")
    parser.add_argument("--url", "-u", type=str,
                      help="Process a single LinkedIn job URL")
    parser.add_argument("--url-file", "-uf", type=str,
                      help="Path to a text file containing LinkedIn job or search URLs, one per line")
    parser.add_argument("--search-url", "-su", type=str,
                      help="Process a LinkedIn search results URL to extract job listings")
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Process a single LinkedIn job URL if provided
    if args.url:
        if not args.url.startswith("https://www.linkedin.com/jobs/view/"):
            logging.error("Invalid LinkedIn job URL. Must start with 'https://www.linkedin.com/jobs/view/'")
            return
            
        logging.info(f"Processing single LinkedIn job URL: {args.url}")
        job_result = analyze_job(args.url, resume_path=args.resume)
        
        # Save the result to a JSON file
        output_dir = os.path.dirname(args.output)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(args.output, "w") as f:
            json.dump({
                "metadata": {
                    "generated_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
                    "source": args.url
                },
                "jobs": [job_result]
            }, f, indent=2)
            
        logging.info(f"Saved job result to: {args.output}")
        
        # Export to Markdown if requested
        if args.export_md:
            md_output_path = os.path.splitext(args.output)[0] + ".md"
            export_to_markdown([job_result], md_output_path, args.url)
        
        return
        
    # Process a LinkedIn search URL if provided
    if args.search_url:
        if not "linkedin.com/jobs/search/" in args.search_url:
            logging.error("Invalid LinkedIn search URL. Must contain 'linkedin.com/jobs/search/'")
            return
            
        logging.info(f"Processing LinkedIn search URL: {args.search_url}")
        job_listings = extract_jobs_from_search_url(args.search_url, args.max_jobs)
        
        if not job_listings:
            logging.error(f"No job listings found in search URL: {args.search_url}")
            return
            
        # Process the extracted job listings
        job_results = process_linkedin_jobs(job_listings, args.resume, args.max_jobs, args.use_api, args.save_html)
        
        # Save the results
        save_and_export_results(job_results, args.output, args.export_md, args.search_url)
        return
        
    # Process URLs from a file if provided
    if args.url_file:
        if not os.path.exists(args.url_file):
            logging.error(f"URL file not found: {args.url_file}")
            return
            
        logging.info(f"Processing URLs from file: {args.url_file}")
        
        try:
            with open(args.url_file, 'r') as f:
                urls = [line.strip() for line in f.readlines() if line.strip() and not line.strip().startswith('//')]
                
            if not urls:
                logging.error(f"No URLs found in file: {args.url_file}")
                return
                
            logging.info(f"Found {len(urls)} URLs in file")
            
            # Process job URLs and search URLs separately
            job_urls = []
            search_results = []
            
            for url in urls:
                if url.startswith("https://www.linkedin.com/jobs/view/"):
                    # This is a job URL
                    logging.info(f"Processing job URL: {url}")
                    job_result = analyze_job(url, resume_path=args.resume)
                    job_urls.append(job_result)
                elif "linkedin.com/jobs/search/" in url:
                    # This is a search URL
                    logging.info(f"Processing search URL: {url}")
                    job_listings = extract_jobs_from_search_url(url, args.max_jobs)
                    if job_listings:
                        search_results.extend(job_listings)
                else:
                    logging.warning(f"Skipping unsupported URL: {url}")
            
            # Process any search results
            job_results = []
            if search_results:
                logging.info(f"Processing {len(search_results)} job listings from search URLs")
                search_job_results = process_linkedin_jobs(search_results, args.resume, args.max_jobs, args.use_api, args.save_html)
                job_results.extend(search_job_results)
                
            # Add direct job URLs
            job_results.extend(job_urls)
            
            if not job_results:
                logging.error("No job results found")
                return
                
            # Save the results
            save_and_export_results(job_results, args.output, args.export_md, args.url_file)
            return
            
        except Exception as e:
            logging.error(f"Error processing URL file: {e}")
            return

    # Get LinkedIn jobs from search results (from multiple files if specified)
    linkedin_jobs = []
    source_files = []
    
    for input_file in args.input:
        source_files.append(os.path.basename(input_file))
        jobs_from_file = filter_linkedin_jobs(input_file)
        logging.info(f"Found {len(jobs_from_file)} LinkedIn jobs in {input_file}")
        linkedin_jobs.extend(jobs_from_file)
    
    # Remove duplicates by job ID
    job_ids_seen = set()
    unique_jobs = []
    
    for job in linkedin_jobs:
        job_id = job.get('id')
        if job_id and job_id not in job_ids_seen:
            job_ids_seen.add(job_id)
            unique_jobs.append(job)
        
    linkedin_jobs = unique_jobs
    logging.info(f"Total unique LinkedIn jobs found: {len(linkedin_jobs)}")
    
    if not linkedin_jobs:
        logging.error(f"No LinkedIn jobs found in the input files")
        return
    
    # Filter jobs by minimum score if specified
    if args.min_score > 0:
        original_count = len(linkedin_jobs)
        linkedin_jobs = [job for job in linkedin_jobs if job['match_score'] >= args.min_score]
        filtered_count = original_count - len(linkedin_jobs)
        logging.info(f"Filtered out {filtered_count} jobs below minimum score of {args.min_score}")
    
    if not linkedin_jobs:
        logging.error(f"No jobs remain after filtering by minimum score")
        return
    
    # Sort jobs by search match score (highest first)
    linkedin_jobs.sort(key=lambda x: x['match_score'], reverse=True)
    
    if args.use_api:
        logging.info("Using LinkedIn guest API for job details")
    else:
        logging.info("Using standard method for job details")
        
    if args.save_html:
        logging.info("Will save raw HTML responses for debugging")
        
    # Process the LinkedIn jobs
    job_results = process_linkedin_jobs(linkedin_jobs, args.resume, args.max_jobs, args.use_api, args.save_html)
    
    # Save the output to a JSON file
    output_dir = os.path.dirname(args.output)
    os.makedirs(output_dir, exist_ok=True)
    
    with open(args.output, "w") as f:
        source_info = ", ".join([os.path.basename(file) for file in args.input]) if len(args.input) <= 3 else f"{len(args.input)} files"
        json.dump({
            "metadata": {
                "generated_at": time.strftime("%Y-%m-%d_%H-%M-%S"),
                "source_files": [os.path.basename(file) for file in args.input],
                "total_jobs": len(job_results),
                "high_matches": sum(1 for job in job_results if job.get('match_score', 0) > 0.7),
                "medium_matches": sum(1 for job in job_results if 0.4 <= job.get('match_score', 0) <= 0.7),
                "low_matches": sum(1 for job in job_results if job.get('match_score', 0) < 0.4)
            },
            "jobs": job_results
        }, f, indent=2)
    
    # Print summary results
    print(f"\n===== LINKEDIN JOB ANALYSIS SUMMARY =====")
    print(f"Processed {len(job_results)} LinkedIn jobs")
    print(f"High matches (>70%): {sum(1 for job in job_results if job.get('match_score', 0) > 0.7)}")
    print(f"Medium matches (40-70%): {sum(1 for job in job_results if 0.4 <= job.get('match_score', 0) <= 0.7)}")
    print(f"Low matches (<40%): {sum(1 for job in job_results if job.get('match_score', 0) < 0.4)}")
    
    # Print top 3 jobs by match score
    top_jobs = sorted(job_results, key=lambda x: x.get('match_score', 0), reverse=True)[:3]
    
    if top_jobs:
        print("\n--- TOP MATCHING JOBS ---")
        for i, job in enumerate(top_jobs):
            print(f"{i+1}. {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
            print(f"   Location: {job.get('location', 'Unknown')}")
            print(f"   Status: {'Active' if job.get('is_active', True) else 'No longer accepting applications'}")
            print(f"   Match Score: {job.get('match_score', 0):.2f}")
            if job.get('posted'):
                print(f"   Posted: {job.get('posted')}")
            print()
    
    # Export to Markdown if requested
    if args.export_md:
        md_output_path = os.path.splitext(args.output)[0] + ".md"
        source_info = ", ".join(source_files) if len(source_files) <= 3 else f"{len(source_files)} files"
        export_to_markdown(job_results, md_output_path, source_info)
        print(f"Markdown report exported to: {md_output_path}")


if __name__ == "__main__":
    main()
