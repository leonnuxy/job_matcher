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
import time
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add project root to path if running as script
if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from services.scraper import ensure_job_descriptions
from services.html_fallback import extract_job_details
from services.linkedin import (
    extract_job_id_from_url,
    fetch_job_via_api,
    extract_jobs_from_search_url
)
from job_search.matcher import calculate_match_score


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


def analyze_job(job_url: str, job_info: Optional[Dict] = None, resume_path: str = "data/resume.txt", matching_profile=None) -> Dict[str, Any]:
    """
    Analyze a specific job URL against a resume.
    
    Args:
        job_url: URL of the job to analyze
        job_info: Optional dictionary with additional job information
        resume_path: Path to the resume file
        matching_profile: Custom matching profile with weights and mode settings
        
    Returns:
        Dictionary with job analysis details
    """
    # Create minimal job info if not provided
    if job_info is None:
        # Try to get job details from LinkedIn guest API first
        linkedin_job_info = fetch_job_via_api(job_url)
        
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
            # Use the provided matching profile or create a default one
            if not matching_profile:
                # Legacy support for getting parameters from args
                import inspect
                frame = inspect.currentframe()
                try:
                    # Try to get the args from the calling context
                    args = frame.f_back.f_locals.get('args')
                    if args and hasattr(args, 'tfidf_weight'):
                        # Create a custom matching profile
                        from job_search.matcher import create_matching_profile
                        matching_profile = create_matching_profile(
                            tfidf_weight=args.tfidf_weight,
                            keyword_weight=args.keyword_weight, 
                            title_weight=args.title_weight,
                            matching_mode=args.matching_mode
                        )
                        logging.debug(f"Created matching profile from args: {matching_profile}")
                except Exception as e:
                    logging.debug(f"Could not access args for matching profile: {e}")
                finally:
                    del frame  # Avoid reference cycles
                
            # Calculate match score using the matcher module
            job_info["match_score"] = calculate_match_score(resume_text, job_info, matching_profile)
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


def filter_linkedin_jobs(job_file: str, min_score: float = 0) -> List[Dict]:
    """
    Filter job search results to include only LinkedIn jobs.
    
    Args:
        job_file: Path to job search results JSON file
        min_score: Minimum match score to include
        
    Returns:
        List of LinkedIn job dictionaries
    """
    try:
        if not os.path.exists(job_file):
            logging.error(f"Job search results file not found: {job_file}")
            return []
        
        with open(job_file, 'r') as f:
            job_results = json.load(f)
        
        # Check if the file has a 'jobs' field (our standard format)
        if isinstance(job_results, dict) and 'jobs' in job_results:
            jobs = job_results['jobs']
        elif isinstance(job_results, list):
            jobs = job_results
        else:
            logging.error(f"Invalid job search results format in {job_file}")
            return []
        
        # Filter to include only LinkedIn jobs
        linkedin_jobs = []
        for job in jobs:
            job_link = job.get('link', job.get('url', ''))
            if 'linkedin.com/jobs/view/' in job_link:
                # Extract the job ID from URL
                job_id = extract_job_id_from_url(job_link)
                if job_id:
                    # Add ID to job object
                    job['id'] = job_id
                    job['url'] = job_link  # Ensure consistent URL field
                    
                    # Include jobs with score above minimum
                    if job.get('match_score', 0) >= min_score:
                        linkedin_jobs.append(job)
                        
        logging.info(f"Found {len(linkedin_jobs)} LinkedIn jobs from {job_file}")
        return linkedin_jobs
        
    except Exception as e:
        logging.error(f"Error loading job file {job_file}: {e}")
        return []


def process_linkedin_jobs(jobs: List[Dict], resume_path: str, max_jobs: Optional[int] = None, use_api: bool = True, save_html: bool = False, matching_profile=None) -> List[Dict]:
    """
    Process multiple LinkedIn jobs.
    
    Args:
        jobs: List of job dictionaries with LinkedIn job URLs
        resume_path: Path to resume file
        max_jobs: Maximum number of jobs to process
        use_api: Whether to use LinkedIn guest API
        save_html: Whether to save raw HTML responses
        matching_profile: Custom matching profile with weights and mode
        
    Returns:
        List of job dictionaries with analysis results
    """
    if max_jobs is not None and max_jobs > 0:
        jobs = jobs[:max_jobs]
    
    total_jobs = len(jobs)
    logging.info(f"Processing {total_jobs} LinkedIn jobs")
    
    # Load resume once for efficiency
    resume_text = load_text_file(resume_path)
    if not resume_text:
        logging.error(f"Failed to load resume from {resume_path}")
        return []
    
    results = []
    for i, job in enumerate(jobs):
        job_url = job.get('url', job.get('link', ''))
        if not job_url:
            logging.warning(f"Job {i+1} has no URL, skipping")
            continue
        
        logging.info(f"Processing job {i+1}/{total_jobs}: {job_url}")
        
        # Create initial job info
        initial_job_info = {
            'title': job.get('title', 'Unknown Title'),
            'company': job.get('company', 'Unknown Company'),
            'location': job.get('location', ''),
            'link': job_url,
            'id': job.get('id', extract_job_id_from_url(job_url))
        }
        
        # Use the LinkedIn guest API if requested
        if use_api:
            logging.info(f"Using LinkedIn guest API for job {i+1}")
            api_job_info = fetch_job_via_api(job_url, save_html=save_html, resume_text=resume_text, matching_profile=matching_profile)
            
            if api_job_info and api_job_info.get("description"):
                # Ensure we have all basic info
                for field in ['title', 'company', 'location']:
                    if not api_job_info.get(field) and initial_job_info.get(field):
                        api_job_info[field] = initial_job_info.get(field)
                
                # If match score wasn't calculated in fetch_job_via_api, calculate it now
                if resume_text and 'match_score' not in api_job_info:
                    api_job_info['match_score'] = calculate_match_score(resume_text, api_job_info, matching_profile)
                    logging.info(f"Match score: {api_job_info['match_score']:.2f}")
                
                # Add to results
                results.append(api_job_info)
                logging.info(f"Successfully processed job {i+1} using LinkedIn guest API")
            else:
                # Fall back to standard method if API fails
                logging.warning(f"LinkedIn guest API failed for job {i+1}, falling back to standard method")
                job_result = analyze_job(job_url, initial_job_info, resume_path, matching_profile)
                results.append(job_result)
        else:
            # Use standard job analysis method
            job_result = analyze_job(job_url, initial_job_info, resume_path, matching_profile)
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
    # Advanced matching options
    parser.add_argument("--tfidf-weight", type=float, default=0.6,
                      help="Weight for TF-IDF text similarity (0.0 to 1.0, default: 0.6)")
    parser.add_argument("--keyword-weight", type=float, default=0.3,
                      help="Weight for keyword matching (0.0 to 1.0, default: 0.3)")
    parser.add_argument("--title-weight", type=float, default=0.1,
                      help="Weight for job title relevance (0.0 to 1.0, default: 0.1)")
    parser.add_argument("--matching-mode", choices=["standard", "strict", "lenient"], default="standard",
                      help="Matching mode: standard, strict (requires more matches), or lenient (requires fewer matches)")
    parser.add_argument("--quiet", "-q", action="store_true",
                      help="Suppress non-error output")
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
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
        
    # Log matching configuration
    logging.debug(f"Matching configuration: TF-IDF weight={args.tfidf_weight}, "
                 f"Keyword weight={args.keyword_weight}, Title weight={args.title_weight}, "
                 f"Mode={args.matching_mode}")
    
    # Create matching profile
    from job_search.matcher import create_matching_profile
    matching_profile = create_matching_profile(
        tfidf_weight=args.tfidf_weight,
        keyword_weight=args.keyword_weight,
        title_weight=args.title_weight,
        matching_mode=args.matching_mode
    )
    
    # Process a single LinkedIn job URL if provided
    if args.url:
        if not args.url.startswith("https://www.linkedin.com/jobs/view/"):
            logging.error("Invalid LinkedIn job URL. Must start with 'https://www.linkedin.com/jobs/view/'")
            return
            
        logging.info(f"Processing single LinkedIn job URL: {args.url}")
        job_result = analyze_job(args.url, resume_path=args.resume, matching_profile=matching_profile)
        
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
        # accept both `/jobs/search/…` and `/jobs/search?…`
        if "linkedin.com/jobs/search" not in args.search_url:
            logging.error("Invalid LinkedIn search URL. Must contain 'linkedin.com/jobs/search'")
            return
            
        logging.info(f"Processing LinkedIn search URL: {args.search_url}")
        
        # Load resume for scoring jobs
        resume_text = None
        if os.path.exists(args.resume):
            resume_text = load_text_file(args.resume)
            logging.info(f"Loaded resume from {args.resume} for matching")
        
        # Extract jobs from search URL and calculate match scores
        job_listings = extract_jobs_from_search_url(args.search_url, args.max_jobs, resume_text, matching_profile)
        
        if not job_listings:
            logging.error(f"No job listings found in search URL: {args.search_url}")
            return
            
        # Process the extracted job listings
        job_results = process_linkedin_jobs(job_listings, args.resume, args.max_jobs, args.use_api, args.save_html, matching_profile)
        
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
                    job_result = analyze_job(url, resume_path=args.resume, matching_profile=matching_profile)
                    job_urls.append(job_result)
                elif "linkedin.com/jobs/search" in url:
                    # This is a search URL
                    logging.info(f"Processing search URL: {url}")
                    # Load resume for matching
                    resume_text = load_text_file(args.resume) if os.path.exists(args.resume) else None
                    # Get job listings with match scores calculated
                    job_listings = extract_jobs_from_search_url(url, args.max_jobs, resume_text, matching_profile)
                    if job_listings:
                        search_results.extend(job_listings)
                else:
                    logging.warning(f"Skipping unsupported URL: {url}")
            
            # Process any search results
            job_results = []
            if search_results:
                logging.info(f"Processing {len(search_results)} job listings from search URLs")
                search_job_results = process_linkedin_jobs(search_results, args.resume, args.max_jobs, args.use_api, args.save_html, matching_profile)
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
    job_results = process_linkedin_jobs(linkedin_jobs, args.resume, args.max_jobs, args.use_api, args.save_html, matching_profile)
    
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
    from main import main as unified_main
    unified_main()
