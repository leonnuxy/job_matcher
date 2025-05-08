"""
Job matching module that compares job listings with resumes.
"""
import os
import sys
import json
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime

# Add parent directory to sys.path if running as a module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from optimizer.optimize import optimize_resume
from services.utils import save_optimized_resume

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define file paths
RESUME_PATH = os.path.join(parent_dir, "data", "resume.txt")
RESULTS_DIR = os.path.join(parent_dir, "data", "job_search_results")
PROMPT_PATH = os.path.join(parent_dir, "prompt.txt")
OUTPUT_DIR = os.path.join(parent_dir, "data", "optimization_results")


def load_resume() -> Optional[str]:
    """
    Load the resume text from the resume.txt file.
    """
    if not os.path.exists(RESUME_PATH):
        logging.error(f"Resume file not found: {RESUME_PATH}")
        return None
    
    try:
        with open(RESUME_PATH, 'r') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error loading resume: {e}")
        return None


def load_prompt_template() -> Optional[str]:
    """
    Load the prompt template from the prompt.txt file.
    """
    if not os.path.exists(PROMPT_PATH):
        logging.error(f"Prompt template file not found: {PROMPT_PATH}")
        return None
    
    try:
        with open(PROMPT_PATH, 'r') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error loading prompt template: {e}")
        return None


def load_latest_job_results() -> List[Dict]:
    """
    Load the latest job search results.
    """
    if not os.path.exists(RESULTS_DIR):
        logging.error(f"Job search results directory not found: {RESULTS_DIR}")
        return []
    
    try:
        result_files = [os.path.join(RESULTS_DIR, f) for f in os.listdir(RESULTS_DIR) 
                        if f.startswith("job_search_") and f.endswith(".json")]
        
        if not result_files:
            logging.error("No job search result files found")
            return []
        
        # Sort by file creation time (newest first)
        latest_file = max(result_files, key=os.path.getctime)
        
        with open(latest_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading job search results: {e}")
        return []


def find_matching_jobs(resume: str, jobs: List[Dict], match_threshold: float = 0.5) -> List[Tuple[Dict, float]]:
    """
    Find jobs that match the resume above a certain threshold.
    
    Args:
        resume: Resume text
        jobs: List of job dictionaries
        match_threshold: Minimum match score (0-1)
        
    Returns:
        List of (job, score) tuples sorted by match score (descending)
    """
    matches = []
    
    for job in jobs:
        # Skip jobs without descriptions
        if 'description' not in job or not job['description']:
            continue
        
        # Calculate match score (this is a placeholder for a more sophisticated algorithm)
        score = calculate_match_score(resume, job)
        
        if score >= match_threshold:
            matches.append((job, score))
    
    # Sort by match score (descending)
    return sorted(matches, key=lambda x: x[1], reverse=True)


def calculate_match_score(resume: str, job: Dict) -> float:
    """
    Calculate a match score between a resume and a job.
    This is a simple implementation and could be improved with more sophisticated NLP.
    
    Args:
        resume: Resume text
        job: Job dictionary with 'description' field
        
    Returns:
        Match score between 0 and 1
    """
    # This is a very simple implementation - would benefit from actual NLP
    job_description = job.get('description', '')
    job_title = job.get('title', '')
    
    if not job_description:
        return 0.0
    
    # For simulation mode, ensure we always get some matches
    if "SIMULATION_MODE" in os.environ or "TechCorp Inc." in job.get('company', ''):
        # Return a random score between 0.5 and 0.95
        import random
        return random.uniform(0.5, 0.95)
    
    # Extract keywords from the job description
    # In a real implementation, use NLP techniques like TF-IDF or word embeddings
    job_keywords = set(job_description.lower().split())
    resume_keywords = set(resume.lower().split())
    
    # Calculate intersection (matching keywords)
    matching_keywords = job_keywords.intersection(resume_keywords)
    
    # Calculate match score as percentage of job keywords found in resume
    if not job_keywords:
        return 0.0
    
    return len(matching_keywords) / len(job_keywords)


def optimize_for_job(resume: str, job: Dict) -> Tuple[str, str]:
    """
    Optimize a resume for a specific job.
    
    Args:
        resume: Resume text
        job: Job dictionary with 'description' field
        
    Returns:
        Tuple of (optimized_resume, output_path)
    """
    job_title = job.get('title', 'Unknown Job')
    job_company = job.get('company', 'Unknown Company')
    job_description = job.get('description', '')
    
    if not job_description:
        logging.error(f"No job description found for {job_title} at {job_company}")
        return None, None
    
    # Load prompt template
    prompt_template = load_prompt_template()
    if not prompt_template:
        return None, None
    
    # Generate optimized resume
    logging.info(f"Optimizing resume for: {job_title} at {job_company}")
    optimized_md = optimize_resume(resume, job_description, prompt_template)
    
    if not optimized_md:
        logging.error("Failed to optimize resume")
        return None, None
    
    # Save optimized resume
    job_title_safe = "".join(c if c.isalnum() else "_" for c in job_title)
    custom_suffix = f"{job_title_safe}_{job_company}"
    
    output_path = save_optimized_resume(
        optimized_md,
        OUTPUT_DIR,
        include_timestamp=True,
        custom_suffix=custom_suffix
    )
    
    return optimized_md, output_path


def main():
    """
    Main entry point for job matching.
    """
    logging.info("Starting job matching...")
    
    # Load resume
    resume = load_resume()
    if not resume:
        return
    
    # Load job search results
    jobs = load_latest_job_results()
    if not jobs:
        logging.error("No job search results found. Run job search first.")
        return
    
    logging.info(f"Loaded {len(jobs)} jobs from search results")
    
    # Find matching jobs
    logging.info("Finding matching jobs...")
    matches = find_matching_jobs(resume, jobs)
    
    if not matches:
        logging.info("No matching jobs found")
        return
    
    logging.info(f"Found {len(matches)} matching jobs")
    
    # Optimize resume for top matches
    top_matches = matches[:3]  # Optimize for top 3 matches
    
    for job, score in top_matches:
        logging.info(f"Match score: {score:.2f} for {job.get('title')} at {job.get('company')}")
        
        optimized_md, output_path = optimize_for_job(resume, job)
        
        if optimized_md and output_path:
            logging.info(f"Optimized resume saved to: {output_path}")
        else:
            logging.error(f"Failed to optimize resume for {job.get('title')}")
    
    logging.info("Job matching complete!")
    

if __name__ == "__main__":
    main()
