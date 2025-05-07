# main.py
import os
import json
import logging
import re
from lib import api_calls, scraper, resume_parser, job_parser_enhanced as job_parser, matcher, ats
# Comment out database imports for now
# from lib.database import get_db_connection, create_results_table, save_job_result
from config import API_KEY, CSE_ID

MAX_JOB_AGE_HOURS = 24  # Change this value to set the max age of job postings (in hours)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to save results to a JSON file
def save_results_to_json(results, keyword):
    """Save job search results to a JSON file."""
    # Create results directory if it doesn't exist
    results_dir = os.path.join(os.path.dirname(__file__), 'results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Create a filename based on the search keyword and current time
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(results_dir, f"job_search_{keyword.replace(' ', '_')}_{timestamp}.json")
    
    # Write to JSON file
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    logging.info(f"Saved results to {filename}")
    return filename

def main():
    # Comment out database connection
    # conn = None
    try:
        # Comment out database setup
        # conn = get_db_connection()
        # if not conn:
        #     logging.error("Could not connect to the database. Exiting.")
        #     return
        # create_results_table(conn)

        # Load search terms from file
        search_terms_path = os.path.join('data', 'search_terms.txt')
        with open(search_terms_path, 'r', encoding='utf-8') as f:
            search_terms = [line.strip() for line in f if line.strip() and not line.startswith('#')]

        resume_file = 'data/resume.txt'  # Preset resume path
        resume_text = resume_parser.extract_resume_text(resume_file)
        resume_skills = resume_parser.extract_resume_skills(resume_text)

        # Dictionary to store all results by keyword
        all_results = {}

        for keyword in search_terms:
            logging.info(f"=== Searching for: {keyword} ===") # Use logging
            search_results = api_calls.search_jobs(keyword, max_age_hours=MAX_JOB_AGE_HOURS)
            if not search_results:
                logging.warning("No results found with CSE API, try Web Scraper") # Use logging
                continue
            scored_results = []
            for result in search_results:
                # --- Filter out 'Senior' roles --- START
                job_title = result.get('title', '')
                if 'senior' in job_title.lower():
                    logging.info(f"Skipping Senior role: {job_title}")
                    continue # Skip this job result
                # --- Filter out 'Senior' roles --- END

                # Use robust extraction for job description
                full_job_text = result.get('snippet', '')
                job_description = job_parser.extract_job_description(full_job_text)
                job_requirements = job_parser.extract_job_requirements(job_description)
                
                # If the result has a URL and we don't have good location data, try to scrape more details
                job_url = result.get('link')
                if job_url and (not result.get('location') or not result.get('company')):
                    try:
                        logging.info(f"Fetching additional details from job URL: {job_url}")
                        job_details = scraper.extract_job_details(job_url)
                        
                        # Update result with any additional information found
                        if job_details.get('location'):
                            result['location'] = job_details.get('location')
                            
                        if job_details.get('company') and not result.get('company'):
                            result['company'] = job_details.get('company')
                            
                        if job_details.get('description') and len(job_description) < len(job_details.get('description')):
                            job_description = job_details.get('description')
                            # Re-extract requirements with better description
                            job_requirements = job_parser.extract_job_requirements(job_description)
                    except Exception as e:
                        logging.warning(f"Failed to fetch additional job details: {e}")
                
                # Use the consistent ATS calculation logic
                similarity_score = ats.calculate_similarity_simple(resume_skills, job_requirements)
                ats_score = ats.simulate_ats_analysis(resume_text, job_description, similarity_score)
                
                # If the job is a good match, get resume optimization suggestions
                if similarity_score > 70:  # Only optimize for promising matches
                    logging.info(f"High potential match found! Optimizing resume for: {job_title}")
                    optimized_resume = api_calls.optimize_resume_with_gemini(resume_text, job_description)
                    # Store optimization suggestions
                    result['resume_optimization'] = optimized_resume
                
                # Prepare job data
                # Extract location using multiple methods, prioritizing the most reliable source
                location = result.get('location')  # First try location directly from API results
                
                if not location:
                    # Try to extract from job description
                    location = job_parser.extract_job_location(job_description)
                
                if not location:
                    # Try to extract from snippet
                    location = job_parser.extract_job_location(full_job_text)
                    
                if not location:
                    # Last resort: use the location from search keyword if it has one
                    search_parts = keyword.split()
                    if len(search_parts) > 1:
                        location = search_parts[-1]  # Assume last word might be location
                
                job_data = {
                    'title': result.get('title'),
                    'company': result.get('company'), 
                    'location': location,
                    'url': result.get('link'),
                    'ats_score': ats_score,
                    'similarity_score': similarity_score,
                    'job_description': job_description,
                    'job_requirements': job_requirements,
                    'resume_optimization': result.get('resume_optimization', None)
                }

                # Add to results list instead of saving to database
                scored_results.append(job_data)

            # Sort results by similarity_score descending
            scored_results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Store results for this keyword
            all_results[keyword] = scored_results
            
            # Print results
            for idx, result in enumerate(scored_results, 1):
                logging.info(f"\nResult {idx}:") # Use logging
                logging.info(f"Title: {result['title']}")
                logging.info(f"Link: {result['url']}")
                logging.info(f"Extracted Keywords: {result['job_requirements']}")
                logging.info(f"Similarity Score: {result['similarity_score']}%")
                logging.info(f"ATS Simulation Score: {result['ats_score']}%")
        
        # Save all results to JSON file
        if all_results:
            save_results_to_json(all_results, "all_searches")

    # Finally block updated to remove database closing
    finally:
        # if conn and conn.is_connected():
        #     conn.close()
        #     logging.info("Database connection closed.")
        pass

if __name__ == "__main__":
    main()
