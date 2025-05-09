"""
Job search functionality that leverages scraping services.
"""
import os
import logging
import sys
import json
import datetime
from typing import List, Dict

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import scraping functionality from services
from services.scraper import (
    search_google_for_jobs, generate_simulated_jobs, 
    ensure_job_descriptions, SIMULATION_MODE, GOOGLE_API_KEY, GOOGLE_CSE_ID
)

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    """
    Main function for job searching based on command line arguments.
    Called by run.py as the search_main function.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Search for jobs")
    parser.add_argument("--terms", nargs="+", help="Search terms to use")
    parser.add_argument("--locations", nargs="+", default=["Remote"], help="Locations to search in")
    parser.add_argument("--recency", type=float, default=24, help="Recency in hours")
    parser.add_argument("--google", action="store_true", default=True, help="Use Google CSE")
    parser.add_argument("--no-google", action="store_false", dest="google", help="Don't use Google CSE")
    parser.add_argument("--max-jobs", type=int, default=10, help="Maximum jobs per search")
    args = parser.parse_args()
    
    # Get search terms from arguments or file
    search_terms = args.terms
    if not search_terms:
        try:
            with open("data/search_terms.txt", "r") as f:
                search_terms = [line.strip() for line in f if line.strip()]
        except Exception as e:
            logging.error(f"Failed to read search terms: {e}")
            search_terms = ["Python Developer"]  # Default fallback
    
    logging.info(f"Searching for: {search_terms} in {args.locations}")
    
    # Collection of all jobs
    all_jobs = []
    
    # Set simulation mode if needed
    if os.getenv("SIMULATION_MODE", "false").lower() in ("true", "1", "yes"):
        logging.info("Running in simulation mode")
        for term in search_terms:
            for location in args.locations:
                search_query = f"{term} {location}"
                jobs = generate_simulated_jobs(search_query)
                all_jobs.extend(jobs)
                logging.info(f"Found {len(jobs)} simulated jobs for '{search_query}'")
    else:
        # Real search
        if args.google and (GOOGLE_API_KEY and GOOGLE_CSE_ID):
            for term in search_terms:
                for location in args.locations:
                    jobs = search_google_for_jobs(term, location, recency_hours=args.recency)
                    all_jobs.extend(jobs)
                    logging.info(f"Found {len(jobs)} jobs for '{term}' in '{location}'")
        else:
            logging.warning("Google CSE not available. Using HTML fallback (less reliable).")
            # Would implement HTML scraping here, but stub for now
            logging.warning("HTML fallback not implemented in this example")
    
    # Ensure each job has a proper description
    if all_jobs:
        logging.info(f"Enriching job descriptions for {len(all_jobs)} jobs")
        all_jobs = ensure_job_descriptions(all_jobs)
        logging.info(f"After enrichment: {len(all_jobs)} valid jobs with descriptions")
    
    # Save results to a file
    if all_jobs:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"data/job_search_results/job_search_{timestamp}.json"
        
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, "w") as f:
            json.dump(all_jobs, f, indent=2)
        
        logging.info(f"Saved {len(all_jobs)} jobs to {output_file}")
    else:
        logging.warning("No jobs found!")
    
    return all_jobs
