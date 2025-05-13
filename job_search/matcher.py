"""
Job matching module that compares job listings with resumes and generates cover letters.
"""
import os
import re
import sys
import json
import logging
import pandas as pd
from typing import List, Dict, Tuple, Optional, Any, Union
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Configure vectorizer with optimized parameters
_TFIDF = TfidfVectorizer(
    stop_words="english", 
    max_df=1.0,  # Allow terms that appear in all documents
    min_df=1,    # Keep terms that appear at least once
    ngram_range=(1, 2),  # Use both unigrams and bigrams
    max_features=5000  # Limit features to prevent overfitting
)

# Add parent directory to sys.path if running as a module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from optimizer.optimize import optimize_resume
from services.utils import save_optimized_resume
from services.cover_letter import load_cover_letter_template, generate_cover_letter, save_cover_letter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define file paths
RESUME_PATH = os.path.join(parent_dir, "data", "resume.txt")
RESULTS_DIR = os.path.join(parent_dir, "data", "job_search_results")
PROMPT_PATH = os.path.join(parent_dir, "prompt.txt")
OUTPUT_DIR = os.path.join(parent_dir, "data", "optimization_results")


def normalize(txt: str) -> str:
    """
    Normalize text by converting to lowercase, removing non-alphanumeric characters,
    and standardizing whitespace.
    
    Args:
        txt: Text to normalize
    
    Returns:
        Normalized text
    """
    txt = txt.lower()
    txt = re.sub(r"[^a-z0-9\s]", " ", txt)
    txt = re.sub(r"\s+", " ", txt).strip()
    return txt


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


def find_matching_jobs(resume: str, jobs: List[Dict], match_threshold: float = 0.4) -> pd.DataFrame:
    """
    Find jobs that match the resume above a certain threshold.
    
    Args:
        resume: Resume text
        jobs: List of job dictionaries
        match_threshold: Minimum match score (0-1)
        
    Returns:
        DataFrame of matching jobs sorted by match score (descending)
    """
    # Normalize resume once
    resume = normalize(resume)
    records = []
    
    for job in jobs:
        # Skip jobs without descriptions
        if 'description' not in job or not job['description']:
            continue
        
        # Calculate match score using TF-IDF and cosine similarity
        score = calculate_match_score(resume, job)
        
        if score >= match_threshold:
            records.append({
                "id": job.get("id"),
                "title": job.get("title"),
                "company": job.get("company"),
                "score": score,
                "location": job.get("location"),
                "link": job.get("link"),
                # Include the full job for later use
                "job": job
            })
    
    # Create and return a sorted DataFrame
    df = pd.DataFrame(records)
    if df.empty:
        return df
    return df.sort_values("score", ascending=False)


def create_matching_profile(matching_mode="standard"):
    """
    Create a simplified matching profile with predefined settings based on mode.
    
    Args:
        matching_mode: Matching mode (standard, strict, lenient)
        
    Returns:
        Dictionary with matching profile configuration
    """
    # Determine threshold multipliers based on matching mode
    if matching_mode == "strict":
        threshold_multiplier = 1.0  # Higher threshold for strict mode
    elif matching_mode == "lenient":
        threshold_multiplier = 1.5  # Boost scores by 50% for lenient mode
    elif matching_mode == "very_lenient":
        threshold_multiplier = 2.2  # Ultra lenient - more than double the scores
    else:  # standard
        threshold_multiplier = 1.1  # Make standard mode 10% more lenient by default
    
    # Note: We've simplified by removing custom weights
    # The calculation function now uses fixed weights
    return {
        "threshold_multiplier": threshold_multiplier,
        "mode": matching_mode
    }


def calculate_match_score(resume: str, job: Union[Dict, str], matching_profile=None) -> float:
    """
    Calculate a match score between a resume and a job using a simplified approach:
    1. TF-IDF and cosine similarity for semantic matching
    2. Direct keyword matching for technical skills
    3. Job title relevance for role fit
    
    Args:
        resume: Resume text
        job: Job dictionary with 'description' field or job description string
        matching_profile: Optional matching profile (simplified - mainly affects thresholds)
        
    Returns:
        Match score between 0 and 1
    """
    try:
        # Extract text and keywords
        if isinstance(job, dict):
            desc = job.get("description", "")
            job_keywords = job.get("keywords", [])
            job_title = job.get("title", "")
        else:
            desc = job
            job_keywords = []
            job_title = ""
        
        if not desc:
            logging.warning("Empty job description, cannot calculate match score")
            return 0.0
            
        # Normalize texts
        resume_norm = normalize(resume)
        desc_norm = normalize(desc)
        
        logging.debug(f"[calculate_match_score] raw desc length={len(desc)}")
        
        # 1. Create a fresh vectorizer for each document pair 
        # (this ensures we're not influenced by previous calculations)
        docs = [resume_norm, desc_norm]
        X = _TFIDF.fit_transform(docs)  # fit on both documents
        tfidf_score = float(cosine_similarity(X[0:1], X[1:2])[0,0])
        
        # Boost the TF-IDF score more aggressively (they tend to be very small naturally)
        # Increasing from 2.5x to 2.75x for more lenient matching
        tfidf_score = min(tfidf_score * 3.0, 1.0)  # Increase TF-IDF boost multiplier
        
        # Add a minimum floor to ensure we don't get too many zeros
        # This ensures even slight matches get some score
        if tfidf_score > 0:
            tfidf_score = max(tfidf_score, 0.18)  # Increased minimum floor from 0.15 to 0.18
        
        # 2. Enhanced keyword matching with higher leniency
        keyword_score = 0.0
        if job_keywords:
            resume_lower = resume.lower()
            matched_count = 0
            partial_matches = 0
            
            for kw in job_keywords:
                kw_lower = kw.lower()
                # Check for exact matches or common variations (plural/singular)
                if (kw_lower in resume_lower or 
                    (kw_lower.endswith('s') and kw_lower[:-1] in resume_lower) or 
                    (kw_lower + 's' in resume_lower)):
                    matched_count += 1
                else:
                    # More lenient approach: Check for word parts
                    # If keyword is at least 4 chars and a substantial part is in resume
                    if len(kw_lower) >= 4:
                        # Try to find the first 3+ characters of the keyword in the resume (reduced from 4)
                        if kw_lower[:3] in resume_lower or kw_lower[-3:] in resume_lower:
                            partial_matches += 0.7  # Further increase partial match weight
            
            # Add the partial matches to the count            
            matched_count += partial_matches
                    
            keyword_score = matched_count / max(1, len(job_keywords))
            
            # Even more lenient bonus structure
            # Give a bonus for high keyword matches (reduced threshold to 2+ from 3+)
            if matched_count >= 2:
                keyword_score = min(keyword_score * 1.6, 1.0)  # 60% bonus for high keyword matches
        
        # 3. Improved job title matching with higher leniency
        title_score = 0.2  # Increase base score for title relevance
        if job_title:
            # Include more meaningful title words (length > 2)
            title_words = [w for w in normalize(job_title).split() if len(w) > 2]
            if title_words:
                resume_words = set(resume_norm.split())
                matches = 0
                
                for word in title_words:
                    if word in resume_words:
                        matches += 1.3  # Increased from 1.2 to 1.3 for more weight
                    else:
                        # More lenient partial matching
                        for resume_word in resume_words:
                            # Check for partial matches with even shorter minimum length (reduced to 2 characters)
                            if (word in resume_word and len(word) > 2) or (resume_word in word and len(resume_word) > 2):
                                matches += 0.8  # Increased from 0.7 to 0.8 for more weight
                                break
                
                # Calculate score but ensure it doesn't go below the base score
                calculated_score = matches / len(title_words)
                title_score = max(title_score, calculated_score)
                
                # Give stronger bonuses for important role matches
                # Added more job roles to the list of keywords
                role_keywords = ['developer', 'engineer', 'analyst', 'scientist', 'manager', 'designer', 
                                'programmer', 'consultant', 'specialist', 'administrator', 'architect', 'lead']
                for role in role_keywords:
                    if role in job_title.lower() and role in resume.lower():
                        title_score = min(title_score + 0.35, 1.0)  # Increased from 0.3 to 0.35
                        break
        
        # Calculate final score with slightly adjusted weights to emphasize keywords more
        # 55% TF-IDF (down from 60%), 35% keywords (up from 30%), 10% title (unchanged)
        # This gives more weight to specific skill matches which tend to be more reliable
        final_score = (0.55 * tfidf_score) + (0.35 * keyword_score) + (0.1 * title_score)
        
        # Apply a threshold multiplier if provided (for compatibility with existing code)
        if matching_profile and "threshold_multiplier" in matching_profile:
            mult = matching_profile["threshold_multiplier"]
            # Simple boost for lenient mode, reduction for strict mode
            final_score = min(final_score * mult, 1.0)
        
        # Ensure we never exceed 1.0
        final_score = min(final_score, 1.0)
        
        return round(final_score, 3)
    except Exception as e:
        logging.error(f"Error calculating match score: {e}")
        return 0.0


def optimize_for_job(resume: str, job: Dict, generate_cover_letter_flag: bool = False) -> Tuple[str, str, Optional[str]]:
    """
    Optimize a resume for a specific job and optionally generate a cover letter.
    
    Args:
        resume: Resume text
        job: Job dictionary with 'description' field
        generate_cover_letter_flag: Whether to generate a cover letter
        
    Returns:
        Tuple of (optimized_resume, resume_output_path, cover_letter_output_path)
    """
    job_title = job.get('title', 'Unknown Job')
    job_company = job.get('company', 'Unknown Company')
    job_description = job.get('description', '')
    
    if not job_description:
        logging.error(f"No job description found for {job_title} at {job_company}")
        return None, None, None
    
    # Load prompt template for resume
    prompt_template = load_prompt_template()
    if not prompt_template:
        return None, None, None
    
    # Generate optimized resume
    logging.info(f"Optimizing resume for: {job_title} at {job_company}")
    optimized_md = optimize_resume(resume, job_description, prompt_template)
    
    if not optimized_md:
        logging.error("Failed to optimize resume")
        return None, None, None
    
    # Create safe filename components
    job_title_safe = "".join(c if c.isalnum() else "_" for c in job_title)
    company_safe = "".join(c if c.isalnum() else "_" for c in job_company)
    custom_suffix = f"{job_title_safe}_{company_safe}"
    
    # Save optimized resume
    resume_output_path = save_optimized_resume(
        optimized_md,
        OUTPUT_DIR,
        include_timestamp=True,
        custom_suffix=custom_suffix
    )
    
    cover_letter_path = None
    if generate_cover_letter_flag:
        # Generate cover letter
        logging.info(f"Generating cover letter for: {job_title} at {job_company}")
        cover_letter_template = load_cover_letter_template()
        
        if cover_letter_template:
            # Fill in the template with job details
            filled_letter = generate_cover_letter(job, cover_letter_template)
            
            if filled_letter:
                # Save the cover letter
                cover_letter_path = save_cover_letter(
                    filled_letter,
                    OUTPUT_DIR,
                    include_timestamp=True,
                    custom_suffix=custom_suffix
                )
                if cover_letter_path:
                    logging.info(f"Cover letter saved to: {cover_letter_path}")
                else:
                    logging.error("Failed to save cover letter")
            else:
                logging.error("Failed to generate cover letter")
        else:
            logging.warning("Cover letter template not found, skipping cover letter generation")
    
    return optimized_md, resume_output_path, cover_letter_path


def load_text_file(file_path: str) -> Optional[str]:
    """
    Load any text file and return its contents.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        File contents as string or None if failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error loading file {file_path}: {e}")
        return None


def load_job_results(results_dir: str) -> List[Dict]:
    """
    Load job search results from a specified directory.
    
    Args:
        results_dir: Directory containing job search result files
        
    Returns:
        List of job dictionaries
    """
    try:
        if not os.path.exists(results_dir):
            logging.error(f"Job search results directory not found: {results_dir}")
            return []
        
        # Find all job search JSON files
        result_files = [os.path.join(results_dir, f) for f in os.listdir(results_dir) 
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


def preprocess_job_data(jobs: List[Dict]) -> List[Dict]:
    """
    Preprocesses job data to standardize format and extract better titles and companies.
    
    Args:
        jobs: List of job dictionaries
        
    Returns:
        Processed list of job dictionaries with enhanced title and company information
    """
    for job in jobs:
        # If job has no title or has "Unknown Title", try to extract from link
        if not job.get('title') or job.get('title') == 'Unknown Title':
            if job.get('link'):
                # Extract job title from the LinkedIn URL if possible
                link = job.get('link')
                
                # Extract position title from LinkedIn URLs
                if 'linkedin.com/jobs/view/' in link:
                    # Handle different URL formats
                    if '-at-' in link:
                        # Format: job-title-at-company-jobid
                        parts = link.split('linkedin.com/jobs/view/')[1].split('-at-')
                        if len(parts) >= 1:
                            # Clean up the title part
                            title_part = parts[0]
                            # Remove trailing job ID if present (common in some LinkedIn URLs)
                            if title_part and title_part[-1].isdigit():
                                title_part = '-'.join(title_part.split('-')[:-1])
                            
                            title = title_part.replace('-', ' ').strip()
                            # Capitalize first letter of each word for proper title case
                            job['title'] = ' '.join(word.capitalize() for word in title.split())
                            
                            # Extract company from URL if missing
                            if (not job.get('company') or job.get('company') == 'Unknown Company') and len(parts) > 1:
                                # Get company part and remove any URL parameters
                                company_part = parts[1].split('?')[0]
                                company = company_part.replace('-', ' ').title()
                                job['company'] = company.strip()
                    else:
                        # Format: jobid without title in URL
                        # Extract the job ID and use it as a placeholder title
                        try:
                            job_id = link.split('linkedin.com/jobs/view/')[1].split('?')[0]
                            if job_id.isdigit():
                                job['title'] = "LinkedIn Job #" + job_id
                        except:
                            pass
        
        # Add keyword list for better matching if not already present
        if 'keywords' not in job and 'description' in job:
            # Extract keywords from description - focus on technical terms
            desc = job.get('description', '').lower()
            job['keywords'] = extract_keywords(desc)
    
    return jobs


def extract_keywords(text: str) -> List[str]:
    """
    Extract relevant technical keywords from text using a more comprehensive approach.
    
    Args:
        text: Text to extract keywords from
        
    Returns:
        List of extracted keywords
    """
    # Comprehensive list of technical keywords by category
    tech_keywords = {
        # Programming languages
        'languages': [
            'python', 'javascript', 'typescript', 'java', 'c#', 'c++', 'ruby', 'php', 
            'go', 'rust', 'kotlin', 'swift', 'scala', 'r', 'bash', 'shell', 'perl',
            'objective-c', 'groovy', 'powershell', 'lua', 'dart', 'haskell', 'clojure'
        ],
        # Web frameworks
        'web_frameworks': [
            'react', 'angular', 'vue', 'svelte', 'next.js', 'nuxt', 'express', 
            'django', 'flask', 'spring', 'spring boot', 'rails', 'laravel', 'asp.net',
            'fastapi', 'quarkus', 'meteor', 'gatsby'
        ],
        # Cloud platforms
        'cloud': [
            'aws', 'azure', 'gcp', 'google cloud', 'ibm cloud', 'oracle cloud',
            'digitalocean', 'heroku', 'netlify', 'vercel', 'cloudflare', 'linode'
        ],
        # DevOps & Infrastructure
        'devops': [
            'kubernetes', 'k8s', 'docker', 'terraform', 'ansible', 'jenkins', 
            'github actions', 'gitlab ci', 'circleci', 'travis', 'pulumi', 'chef', 
            'puppet', 'prometheus', 'grafana', 'elk', 'nginx', 'apache'
        ],
        # Databases
        'databases': [
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'sqlite', 'redis',
            'elasticsearch', 'dynamodb', 'cassandra', 'couchdb', 'firestore',
            'mariadb', 'oracle', 'sqlserver', 'neo4j', 'graphql'
        ],
        # AI/ML
        'ai_ml': [
            'machine learning', 'ml', 'deep learning', 'ai', 'artificial intelligence',
            'nlp', 'natural language processing', 'tensorflow', 'pytorch', 'keras',
            'scikit-learn', 'opencv', 'computer vision', 'llm', 'large language model'
        ],
        # Roles & methodologies
        'roles': [
            'full stack', 'frontend', 'backend', 'devops', 'data engineer', 'data scientist',
            'sre', 'site reliability', 'qa', 'quality assurance', 'product manager',
            'scrum master', 'agile', 'scrum', 'kanban', 'waterfall', 'ci/cd', 
            'continuous integration', 'continuous delivery'
        ]
    }
    
    # Prepare text
    text_lower = text.lower()
    text_words = set(re.findall(r'\b\w+\b', text_lower))  # Get all whole words
    
    # Find all matching keywords in the text
    found_keywords = []
    
    # Check for exact keyword matches
    for category, keywords in tech_keywords.items():
        for keyword in keywords:
            # Use word boundary check for more precise matching
            # This avoids "react" matching "reactive" but allows multi-word terms
            if ' ' in keyword:  # Multi-word term
                if keyword in text_lower:
                    found_keywords.append(keyword)
            else:  # Single word - use word boundary check
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, text_lower):
                    found_keywords.append(keyword)
    
    # Find capitalized words which might be technologies not in our list
    # (e.g., product names, company-specific tools)
    capitalized_pattern = r'\b[A-Z][a-z]*[A-Z][a-zA-Z]*\b'  # CamelCase or PascalCase words
    for match in re.findall(capitalized_pattern, text):
        if len(match) > 2 and match.lower() not in found_keywords:
            found_keywords.append(match)
    
    return found_keywords


def load_jobs_from_file(file_path: str) -> List[Dict]:
    """
    Load job data directly from a JSON file.
    
    Args:
        file_path: Path to the JSON file containing job data
        
    Returns:
        List of job dictionaries
    """
    try:
        if not os.path.exists(file_path):
            logging.error(f"Job data file not found: {file_path}")
            return []
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Handle different JSON structures
        jobs = []
        if isinstance(data, list):
            # If it's already a list of jobs
            jobs = data
        elif isinstance(data, dict):
            # If it's a container with a 'jobs' key (like LinkedIn format)
            if 'jobs' in data and isinstance(data['jobs'], list):
                jobs = data['jobs']
            # Otherwise, it might be a single job
            elif 'description' in data:
                jobs = [data]
        
        if not jobs:
            logging.error(f"Unrecognized job data format in {file_path}")
            return []
            
        # Preprocess jobs to extract titles and keywords
        jobs = preprocess_job_data(jobs)
        return jobs
    except Exception as e:
        logging.error(f"Error loading jobs from file {file_path}: {e}")
        return []


def main(resume_path=None, results_dir=None, match_threshold=0.5, top_n=3, with_cover_letter=False):
    """
    Main entry point for job matching.
    
    Args:
        resume_path: Path to resume file
        results_dir: Directory with job search results or path to a JSON file
        match_threshold: Minimum match score threshold
        top_n: Number of top matches to process
        with_cover_letter: Whether to generate a cover letter alongside the resume
    """
    logging.info("Starting job matching...")
    
    # Use parameters or defaults
    resume_file = resume_path or RESUME_PATH
    job_results_path = results_dir or RESULTS_DIR
    
    # Load resume
    resume = load_resume() if resume_path is None else load_text_file(resume_file)
    if not resume:
        return
    
    # Load job search results based on whether results_dir is a file or directory
    if results_dir and os.path.isfile(job_results_path):
        # Load directly from a JSON file
        jobs = load_jobs_from_file(job_results_path)
    else:
        # Load from a directory of job search files
        jobs = load_latest_job_results() if results_dir is None else load_job_results(job_results_path)
    
    if not jobs:
        logging.error("No job search results found. Run job search first.")
        return
    
    logging.info(f"Loaded {len(jobs)} jobs from search results")
    
    # Find matching jobs
    logging.info(f"Finding matching jobs with threshold {match_threshold}...")
    df_matches = find_matching_jobs(resume, jobs, match_threshold)
    
    if df_matches.empty:
        logging.info(f"No matching jobs found above the threshold of {match_threshold}. Try lowering the threshold.")
        # Print jobs that might be worth considering
        logging.info("Here are the available job titles:")
        for i, job in enumerate(jobs[:5], 1):
            job_title = job.get("title", "Unknown Title") 
            company = job.get("company", "Unknown Company")
            logging.info(f"{i}. {job_title if job_title != 'Unknown Title' else job.get('link', 'No Title')} at {company}")
        if len(jobs) > 5:
            logging.info(f"...and {len(jobs) - 5} more")
        return
    
    # Save matches to CSV for reference
    csv_path = os.path.join(OUTPUT_DIR, f"top_matches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df_matches[["title", "company", "score", "location"]].to_csv(csv_path, index=False)
    logging.info(f"Saved {len(df_matches)} matching jobs to: {csv_path}")
    
    # Process top N matches
    logging.info(f"Found {len(df_matches)} matching jobs, processing top {top_n}")
    top_matches = df_matches.head(top_n)
    
    for _, row in top_matches.iterrows():
        job = row["job"]
        score = row["score"]
        logging.info(f"Match score: {score:.3f} for {job.get('title')} at {job.get('company')}")
        
        optimized_md, resume_path, cover_letter_path = optimize_for_job(resume, job, with_cover_letter)
        
        if optimized_md and resume_path:
            logging.info(f"Optimized resume saved to: {resume_path}")
            
            if with_cover_letter and cover_letter_path:
                logging.info(f"Cover letter saved to: {cover_letter_path}")
            elif with_cover_letter:
                logging.warning(f"Cover letter generation requested but failed for {job.get('title')}")
        else:
            logging.error(f"Failed to optimize resume for {job.get('title')}")
    
    logging.info("Job matching complete!")
    

if __name__ == "__main__":
    main()
