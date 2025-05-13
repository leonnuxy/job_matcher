#!/usr/bin/env python
"""
Simplified LinkedIn job search and matching script that uses a more lenient matching approach
with lower thresholds to ensure we get results.
"""

import os
import sys
import logging
import argparse
from typing import Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add project root to path if running as script
if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from services.linkedin import build_search_url, extract_jobs_from_search_url
from process_linkedin_job import process_linkedin_jobs, save_and_export_results
from job_search.matcher import create_matching_profile


def run_linkedin_search(
    search_term: str,
    location: str,
    recency_hours: int = 48,
    resume_path: str = "data/resume.txt",
    output_path: Optional[str] = None,
    max_jobs: int = 10,
    min_score: float = 0.01,  # Very low threshold to ensure results
    use_api: bool = True,
    export_md: bool = True
):
    """
    Run a simplified LinkedIn job search and match jobs against a resume.
    
    Args:
        search_term: The job title or keywords to search for
        location: Location for the job search
        recency_hours: How recent jobs should be (in hours)
        resume_path: Path to the resume text file
        output_path: Path for the output file (auto-generated if None)
        max_jobs: Maximum number of jobs to process
        min_score: Minimum match score to include (very low to ensure results)
        use_api: Whether to use LinkedIn guest API
        export_md: Whether to export results as Markdown
    """
    # Create output path if not provided
    if not output_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = "data/job_matches"
        os.makedirs(output_dir, exist_ok=True)
        output_path = f"{output_dir}/linkedin_{search_term.replace(' ', '_')}_{timestamp}.json"
    
    # Build LinkedIn search URL
    search_url = build_search_url(search_term, location, recency_hours)
    logging.info(f"LinkedIn search URL: {search_url}")
    
    # Create more lenient matching profile
    matching_profile = create_matching_profile(matching_mode="lenient")
    logging.info(f"Using lenient matching with threshold multiplier: {matching_profile['threshold_multiplier']}")
    
    # Check if resume exists
    if not os.path.exists(resume_path):
        logging.error(f"Resume file not found: {resume_path}")
        return False
    
    # Load resume for matching
    with open(resume_path, 'r', encoding='utf-8') as f:
        resume_text = f.read()
    
    # Extract jobs from search URL with match scores already calculated
    logging.info(f"Extracting jobs from LinkedIn search for '{search_term}' in {location}")
    job_listings = extract_jobs_from_search_url(
        search_url, 
        max_jobs=max_jobs,
        resume_text=resume_text,
        matching_profile=matching_profile
    )
    
    if not job_listings:
        logging.error(f"No job listings found in search URL: {search_url}")
        return False
        
    logging.info(f"Extracted {len(job_listings)} job listings from search")
    
    # Process the extracted job listings
    job_results = process_linkedin_jobs(
        job_listings,
        resume_path=resume_path,
        max_jobs=max_jobs,
        use_api=use_api,
        save_html=False,
        matching_profile=matching_profile
    )
    
    if not job_results:
        logging.error("No job results were processed successfully.")
        return False
    
    # Filter by minimum score
    original_count = len(job_results)
    job_results = [job for job in job_results if job.get('match_score', 0) >= min_score]
    filtered_count = original_count - len(job_results)
    
    if filtered_count > 0:
        logging.info(f"Filtered out {filtered_count} jobs below minimum score of {min_score}")
    
    if not job_results:
        logging.error(f"No jobs remain after filtering by minimum score")
        return False
    
    # Save results
    save_and_export_results(job_results, output_path, export_md, search_url)
    
    return True


def main():
    """Process command line arguments and run the search"""
    parser = argparse.ArgumentParser(description="Simplified LinkedIn job search and matcher")
    parser.add_argument("--search", "-s", type=str, default="Software Developer", 
                      help="Job search term (default: Software Developer)")
    parser.add_argument("--location", "-l", type=str, default="Canada",
                      help="Job location (default: Canada)")
    parser.add_argument("--recency", "-r", type=int, default=48,
                      help="Job recency in hours (default: 48)")
    parser.add_argument("--resume", type=str, default="data/resume.txt",
                      help="Path to resume text file (default: data/resume.txt)")
    parser.add_argument("--output", "-o", type=str, default=None,
                      help="Output path (default: auto-generated)")
    parser.add_argument("--max-jobs", "-m", type=int, default=5,
                      help="Maximum number of jobs to process (default: 5)")
    parser.add_argument("--min-score", "-ms", type=float, default=0.01,
                      help="Minimum match score (default: 0.01)")
    parser.add_argument("--no-api", action="store_true",
                      help="Don't use LinkedIn guest API")
    parser.add_argument("--no-md", action="store_true",
                      help="Don't export results as Markdown")
    
    args = parser.parse_args()
    
    # Run the search
    success = run_linkedin_search(
        search_term=args.search,
        location=args.location,
        recency_hours=args.recency,
        resume_path=args.resume,
        output_path=args.output,
        max_jobs=args.max_jobs,
        min_score=args.min_score,
        use_api=not args.no_api,
        export_md=not args.no_md
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
