# main.py
import os
import json
import logging
import re
from datetime import datetime
from lib import api_calls, scraper, resume_parser, job_parser_enhanced as job_parser, matcher, ats
from lib.optimization_utils import generate_optimized_documents # Import the new utility
from lib.console_output import get_console, set_verbose # Import console output
# Comment out database imports for now
# from lib.database import get_db_connection, create_results_table, save_job_result
from config import API_KEY, CSE_ID, MAX_JOB_AGE_HOURS # MAX_JOB_AGE_HOURS is now from config

# Configure logging for file output only (reduce console noise)
def setup_logging():
    """Setup logging configuration for file-based debugging."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # File handler for detailed logging
    log_file = os.path.join(logs_dir, f"job_matcher_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    
    # Console handler for errors only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return log_file

# Initialize logging
log_file = setup_logging()

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
    # Get console output instance
    console = get_console()
    
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

        # Display header with resume and search info
        console.job_search_header(resume_file, len(resume_skills), search_terms)
        
        # Show search progress header
        console.section("🔎 SEARCHING FOR JOBS")
        print("┌─────────────────────────────────────────────────────────────┐")

        # Dictionary to store all results by keyword
        all_results = {}
        total_jobs = 0
        high_potential_jobs = 0
        resumes_generated = 0
        cover_letters_generated = 0

        for search_idx, keyword in enumerate(search_terms, 1):
            # Show search progress
            console.search_progress(search_idx, len(search_terms), keyword, 0)
            
            logging.info(f"=== Searching for: {keyword} ===") # Keep for file logging
            search_results = api_calls.search_jobs(keyword, max_age_hours=MAX_JOB_AGE_HOURS)
            if not search_results:
                logging.warning("No results found with CSE API, try Web Scraper") # Keep for file logging
                console.search_progress(search_idx, len(search_terms), keyword, 100)
                continue
            
            scored_results = []
            total_results = len(search_results)
            
            for result_idx, result in enumerate(search_results):
                # Update progress
                progress = int(((result_idx + 1) / total_results) * 100)
                console.search_progress(search_idx, len(search_terms), keyword, progress)
                # --- Filter out 'Senior' roles --- START
                job_title = result.get('title') or ''
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
                # Skip scraping for Indeed URLs
                if job_url and "indeed" in job_url.lower():
                    logging.info(f"Skipping scraping for Indeed URL: {job_url}")
                elif job_url and (not result.get('location') or not result.get('company')):
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
                
                # If the job is a good match, get resume optimization using custom prompt
                if similarity_score > 70:  # Only optimize for promising matches
                    high_potential_jobs += 1
                    job_title = result.get('title') or 'Unknown Job Title'
                    company_name = result.get('company') or 'Unknown Company'
                    
                    # Show optimization status to user
                    console.optimization_status(job_title, company_name)
                    logging.info(f"High potential match! Generating documents for: {job_title} at {company_name}")
                    
                    optimized_resume, cover_letter, _ = generate_optimized_documents(resume_text, job_description)

                    if not optimized_resume and not cover_letter:
                        logging.warning(f"Could not generate documents for {job_title}")
                        # Continue to next result or handle as appropriate
                        # For now, we'll just not save files if generation failed.
                    else:
                        # Create sanitized job info for filenames
                        # Handle case where job_title might be None
                        title_safe = job_title if job_title is not None else "Unknown_Job"
                        sanitized_job_title = re.sub(r'[^\w\s-]', '', title_safe).strip().replace(' ', '_')[:50]
                        # Handle case where company_name might be None
                        company_safe = company_name if company_name is not None else "Unknown_Company"
                        sanitized_company = re.sub(r'[^\w\s-]', '', company_safe).strip().replace(' ', '_')[:30]
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        # Ensure this path is correct, consider using RESULTS_DIR from config
                        output_dir_name = "optimization_results" # Subdirectory within data or results
                        # Let's assume optimization_results is a subdir of DATA_DIR from config
                        # from config import DATA_DIR
                        # output_dir = os.path.join(DATA_DIR, output_dir_name)
                        # For now, keeping original relative path logic for output_dir
                        output_dir = os.path.join(os.path.dirname(__file__), "data", "optimization_results")
                        os.makedirs(output_dir, exist_ok=True)
                        
                        resume_file_path = None
                        if optimized_resume:
                            resume_file_path = os.path.join(output_dir, f"Resume_{sanitized_job_title}_{sanitized_company}_{timestamp}.md")
                            with open(resume_file_path, 'w', encoding='utf-8') as file:
                                file.write(optimized_resume)
                            logging.info(f"Saved optimized resume to {resume_file_path}")
                            resumes_generated += 1
                        
                        if cover_letter:
                            cover_letter_file = os.path.join(output_dir, f"CoverLetter_{sanitized_job_title}_{sanitized_company}_{timestamp}.md")
                            with open(cover_letter_file, 'w', encoding='utf-8') as file:
                                file.write(cover_letter)
                            logging.info(f"Saved cover letter to {cover_letter_file}")
                            cover_letters_generated += 1
                            
                            # Save as latest cover letter for easy access
                            with open(os.path.join(output_dir, "latest_cover_letter.md"), 'w', encoding='utf-8') as file:
                                file.write(cover_letter)
                        
                        # Store optimization results in the job data
                        result['resume_optimization'] = optimized_resume
                        result['cover_letter'] = cover_letter
                        result['resume_file_path'] = resume_file_path
                
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
                total_jobs += 1

            # Sort results by similarity_score descending
            scored_results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Store results for this keyword
            all_results[keyword] = scored_results
            
            # Update progress to 100% for this search
            console.search_progress(search_idx, len(search_terms), keyword, 100)
            
            # Log detailed results to file only
            for idx, result in enumerate(scored_results, 1):
                logging.info(f"\nResult {idx}:") # Use logging
                logging.info(f"Title: {result['title']}")
                logging.info(f"Link: {result['url']}")
                logging.info(f"Extracted Keywords: {result['job_requirements']}")
                logging.info(f"Similarity Score: {result['similarity_score']}%")
                logging.info(f"ATS Simulation Score: {result['ats_score']}%")
        
        # Close progress box
        print("└─────────────────────────────────────────────────────────────┘")
        
        # Display search summary
        console.search_summary(total_jobs, high_potential_jobs, resumes_generated, cover_letters_generated)
        
        # Collect all jobs for top matches display
        all_jobs = []
        for keyword_results in all_results.values():
            all_jobs.extend(keyword_results)
        
        # Sort all jobs by similarity score
        all_jobs.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Display top matching jobs
        console.display_top_jobs(all_jobs)
        
        # Save all results to JSON file
        results_file = None
        if all_results:
            results_file = save_results_to_json(all_results, "all_searches")
        
        # Display file save summary
        optimization_dir = "./data/optimization_results/"
        if results_file:
            console.files_saved_summary(results_file, optimization_dir)
        
        # Show detailed log location
        console.info(f"📋 Detailed logs saved to: {log_file}")

    # Finally block updated to remove database closing
    finally:
        # if conn and conn.is_connected():
        #     conn.close()
        #     logging.info("Database connection closed.")
        pass

if __name__ == "__main__":
    main()
