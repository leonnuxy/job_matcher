# services/scraper.py
"""
Robust job board scraper with retry logic, Google CSE support, simulated data mode,
HTML fallback scraping, and unified extraction patterns.
"""
import os
import logging
import random
from typing import List, Dict
from urllib.parse import urlparse, parse_qs
from .config import SIMULATION_MODE, GOOGLE_API_KEY, GOOGLE_CSE_ID
from .google_cse import search_google_for_jobs
from .html_fallback import extract_job_listings, extract_job_details
from .http_client import SESSION
from .config import USER_AGENT
from bs4 import BeautifulSoup



def generate_simulated_jobs(search_term: str) -> List[Dict]:
    """
    Produce fake listings for offline development.
    """
    parts = search_term.split()
    title = " ".join(parts[:-1]) if len(parts) > 1 else parts[0]
    loc = parts[-1] if len(parts) > 1 else "Remote"
    companies = ["TechCorp", "DataSoft", "InnovateTech", "CloudWave", "QuantumCode"]
    
    # Job descriptions by role type
    job_descriptions = {
        "Python": """
            We're looking for an experienced Python developer to join our team. 
            
            Requirements:
            - 3+ years experience with Python
            - Experience with web frameworks such as Django or Flask
            - Strong understanding of object-oriented programming
            - Knowledge of database systems like PostgreSQL or MongoDB
            - Familiarity with version control systems (Git)
            
            Responsibilities:
            - Develop and maintain backend services and APIs
            - Write clean, efficient, and well-documented code
            - Collaborate with cross-functional teams
            - Participate in code reviews and testing
            - Troubleshoot and debug applications
            
            Benefits:
            - Competitive salary
            - Remote work options
            - Health insurance
            - Paid time off
            - Professional development opportunities
        """,
        "Developer": """
            We are seeking a skilled Developer to design and implement robust software solutions.
            
            Requirements:
            - Bachelor's degree in Computer Science or related field
            - Strong problem-solving abilities
            - Proficiency in multiple programming languages
            - Experience with agile development methodologies
            - Excellent communication skills
            
            Responsibilities:
            - Design and build scalable applications
            - Write maintainable code following best practices
            - Troubleshoot issues and optimize performance
            - Collaborate with product and design teams
            - Maintain documentation and technical specifications
            
            Benefits:
            - Flexible work schedule
            - Competitive compensation
            - Career advancement opportunities
            - Collaborative work environment
        """,
        "Engineer": """
            Join our engineering team to build innovative solutions for complex problems.
            
            Requirements:
            - Degree in Engineering, Computer Science, or related field
            - Experience in software development and system design
            - Knowledge of cloud platforms (AWS, GCP, or Azure)
            - Understanding of CI/CD pipelines
            - Strong analytical and problem-solving skills
            
            Responsibilities:
            - Design and implement robust technical solutions
            - Write high-quality, maintainable code
            - Review code and provide technical guidance
            - Participate in architectural planning
            - Monitor system performance and troubleshoot issues
            
            Benefits:
            - Competitive salary and bonuses
            - Comprehensive health benefits
            - Stock options
            - Learning and development budget
            - Modern equipment and tools
        """,
        "default": """
            We are looking for a talented professional to join our growing team.
            
            Requirements:
            - Relevant experience in the field
            - Strong problem-solving abilities
            - Excellent communication skills
            - Ability to work independently and as part of a team
            - Attention to detail and organizational skills
            
            Responsibilities:
            - Execute key projects and initiatives
            - Collaborate with cross-functional teams
            - Identify and implement process improvements
            - Maintain documentation and reports
            - Participate in team meetings and planning sessions
            
            Benefits:
            - Competitive compensation package
            - Professional development opportunities
            - Collaborative work environment
            - Work-life balance focus
            - Health and wellness programs
        """
    }
    
    jobs: List[Dict] = []
    for i in range(random.randint(3, 6)):
        comp = random.choice(companies)
        short_desc = f"{comp} is seeking a {title} in {loc}."
        
        # Select an appropriate detailed description based on the job title
        detailed_desc = None
        for key in job_descriptions:
            if key.lower() in title.lower():
                detailed_desc = job_descriptions[key]
                break
        
        # Use default if no specific description matches
        if not detailed_desc:
            detailed_desc = job_descriptions["default"]
        
        # Create a full job description with the company and role information
        full_desc = f"{short_desc}\n\n{detailed_desc.strip()}\n\nLocation: {loc}\nCompany: {comp}\nPosition: {title}"
        
        jobs.append({
            "title": title,
            "company": comp,
            "location": loc,
            "link": f"https://example.com/job/{i}",
            "description": full_desc,
            "snippet": short_desc,
            "full_description": full_desc  # Adding full description field
        })
    return jobs


def scrape_job_board(url: str) -> List[Dict]:
    """
    Main entry: returns simulated, Google-CSE, or HTML-scraped listings.
    """
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    term = params.get("keywords", params.get("q", [""]))[0].replace("+"," ")
    loc  = params.get("location", params.get("l", [""]))[0].replace("+"," ")

    if SIMULATION_MODE:
        logging.info(f"[SIM] {term} in {loc}")
        return generate_simulated_jobs(f"{term} {loc}".strip())

    if GOOGLE_API_KEY and GOOGLE_CSE_ID:
        return search_google_for_jobs(term, loc)

    # HTML fallback
    resp = SESSION.get(url, headers={"User-Agent": USER_AGENT})
    if not resp or resp.status_code != 200:
        logging.error(f"Fallback scrape failed: {url}")
        return []
    soup = BeautifulSoup(resp.text, "lxml")
    return extract_job_listings(soup, url)



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
    combined_sources = 0
    short_descriptions = 0
    skipped_jobs = 0
    
    for job in jobs:
        job_title = job.get("title", "Unknown job")
        job_company = job.get("company", "Unknown company")
        
        # Skip if the job already has a good description
        if job.get("description") and len(job["description"]) >= min_description_length:
            # Save full description in a separate field for future reference
            job["full_description"] = job["description"]
            enriched_jobs.append(job)
            already_good += 1
            continue
        
        # Try to fetch additional details
        has_valid_description = False
        detailed_description = None
        
        # Only try to fetch if we have a link and we're not in simulation mode
        if job.get("link") and not SIMULATION_MODE:
            # Try to get detailed description from the job page
            job_details = extract_job_details(job["link"], job)
            if job_details.get("description") and len(job_details["description"]) >= min_description_length:
                detailed_description = job_details["description"]
                has_valid_description = True
                enriched_from_details += 1
                logging.debug(f"Enhanced description for '{job_title}' at {job_company} by fetching details")
        
        # Consider using both sources (enriched and snippet) if available
        snippet = job.get("snippet", "")
        
        # Option 1: Use enriched description if available
        if has_valid_description:
            job["description"] = detailed_description
            job["full_description"] = detailed_description
            
        # Option 2: Combine snippet with other available info if both exist and offer different content
        elif snippet and detailed_description and len(snippet) > 30 and \
             snippet not in detailed_description and detailed_description not in snippet:
            combined = f"{snippet}\n\n{detailed_description}"
            job["description"] = combined
            job["full_description"] = combined
            has_valid_description = True
            combined_sources += 1
            logging.debug(f"Combined sources for '{job_title}' at {job_company}")
        
        # Option 3: Fall back to snippet if available and no valid description yet
        elif not has_valid_description and snippet and len(snippet) >= min_description_length:
            job["description"] = snippet
            job["full_description"] = snippet
            has_valid_description = True
            enriched_from_snippet += 1
            logging.debug(f"Used snippet as description for '{job_title}' at {job_company}")
            
        # Option 4: If we still don't have a valid description, use any available content
        elif not has_valid_description:
            # Use any available description content, even if short
            if detailed_description:
                job["description"] = detailed_description
                job["full_description"] = detailed_description
                has_valid_description = True
                short_descriptions += 1
            elif snippet:
                job["description"] = snippet
                job["full_description"] = snippet
                has_valid_description = True
                short_descriptions += 1
                logging.debug(f"Used short content for '{job_title}' at {job_company}")
        
        # Only keep jobs that have some form of description
        if job.get("description"):
            # Generate synthetic structure if the description is very short
            if len(job["description"]) < 100:
                job["description"] = f"{job_title} position at {job_company}.\n\n{job['description']}"
            enriched_jobs.append(job)
        else:
            skipped_jobs += 1
            logging.debug(f"Skipping job '{job_title}' - no valid description")
    
    # Log summary of enrichment process
    logging.info(f"Description enrichment summary:")
    logging.info(f"  - {already_good} jobs already had good descriptions")
    logging.info(f"  - {enriched_from_details} jobs enriched from detailed page extraction")
    logging.info(f"  - {enriched_from_snippet} jobs enriched from snippets")
    logging.info(f"  - {combined_sources} jobs enriched from combined sources")
    logging.info(f"  - {short_descriptions} jobs using short descriptions")
    
    if skipped_jobs > 0:
        logging.info(f"  - {skipped_jobs} jobs skipped due to no valid description")
    
    # Calculate description quality statistics
    total_jobs = len(enriched_jobs)
    if total_jobs > 0:
        avg_length = sum(len(job.get('description', '')) for job in enriched_jobs) / total_jobs
        max_length = max(len(job.get('description', '')) for job in enriched_jobs) if enriched_jobs else 0
        min_length = min(len(job.get('description', '')) for job in enriched_jobs) if enriched_jobs else 0
        
        logging.info(f"After enrichment: {total_jobs} valid jobs with descriptions")
        logging.debug(f"Description stats - avg: {avg_length:.1f} chars, min: {min_length} chars, max: {max_length} chars")
    
    return enriched_jobs

