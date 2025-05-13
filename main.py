#!/usr/bin/env python3
# main.py
"""
Main entry point for the job_matcher application with a centralized CLI system.

This script provides a unified command-line interface with subcommands for all job_matcher functionalities:
- search: Search for jobs across multiple platforms
- match: Calculate match scores for job listings against a resume
- linkedin: Process and analyze LinkedIn job postings
- api: Start the FastAPI server for the web interface
- web: Start the Flask web application

Examples:
    python main.py search --terms "Python Developer" --locations "Remote" "Canada" --recency 24
    python main.py match --resume "data/resume.txt" --min-score 0.6
    python main.py linkedin --url "https://www.linkedin.com/jobs/view/4219164109" --resume data/resume.txt --min-score 0.5 --output data/linkedin_test.json --debug
    python main.py api --port 8000
    python main.py web
"""
import os
import sys
import argparse
import logging
from dotenv import load_dotenv
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add the project root to the path if running as script
if __name__ == "__main__" and __package__ is None:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def cmd_search(args):
    """Search for jobs across multiple platforms."""
    from job_search.search import main as search_main
    
    # Set simulation mode environment variable if requested
    if args.simulate:
        os.environ["SIMULATION_MODE"] = "1"
        logging.info("Running in simulation mode")
    
    # Prepare arguments for search module
    search_args = []
    if args.terms:
        search_args.extend(["--terms"] + args.terms)
    if args.locations:
        search_args.extend(["--locations"] + args.locations)
    if args.recency is not None:
        search_args.extend(["--recency", str(args.recency)])
    if args.google:
        search_args.append("--google")
    else:
        search_args.append("--no-google")
    if args.max_jobs:
        search_args.extend(["--max-jobs", str(args.max_jobs)])
    if args.output:
        search_args.extend(["--output", args.output])
    
    logging.info("Running job search...")
    # Pass the arguments to the search module's main function
    sys.argv = [sys.argv[0]] + search_args
    try:
        search_main() # Call search_main but don't return its result directly
        return 0 # Indicate success
    except Exception as e:
        logging.error(f"Error in search command: {e}")
        return 1

def cmd_match(args):
    """Calculate match scores for job listings against a resume."""
    from job_search.matcher import main as matcher_main
    
    # Prepare arguments for matcher module
    matcher_args = []
    if args.resume:
        matcher_args.extend(["--resume", args.resume])
    if args.min_score is not None:
        matcher_args.extend(["--min-score", str(args.min_score)])
    if args.output:
        matcher_args.extend(["--output", args.output])
    if args.input:
        matcher_args.extend(["--input", args.input])
    if args.format:
        matcher_args.extend(["--format", args.format])
        
    logging.info("Running job matching...")
    # Pass the arguments to the matcher module's main function
    sys.argv = [sys.argv[0]] + matcher_args
    try:
        return matcher_main()
    except Exception as e:
        logging.error(f"Error in match command: {e}")
        return 1

def cmd_linkedin(args):
    """Process and analyze LinkedIn job postings."""
    from services.linkedin import build_search_url, extract_jobs_from_search_url
    from process_linkedin_job import process_linkedin_jobs, save_and_export_results
    from job_search.matcher import create_matching_profile
    
    # Setup debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    
    all_jobs = []  # For storing all processed job listings
    urls = []  # For collecting URLs to process
    
    # Create simplified matching profile
    matching_profile = create_matching_profile(
        matching_mode=args.matching_mode
    )
    
    # Log the simplified profile info
    logging.info(f"Using matching profile: mode={matching_profile['mode']}, "
                f"threshold_multiplier={matching_profile['threshold_multiplier']}")
    
    # 1) Determine which URLs to process
    if args.url:
        # Single direct job URL mode
        urls = [args.url]
    elif args.search_url:
        # Single search URL mode
        urls = [args.search_url]
    elif args.terms_file:
        # Terms file mode - parse search terms and build URLs
        with open(args.terms_file, 'r', encoding='utf-8') as f:
            for line in f:
                # Skip empty lines and comments
                line = line.partition('#')[0].strip()
                if not line:
                    continue
                
                # Parse the line format: "keyword[, location[, recency]]"
                parts = [p.strip() for p in line.split(',', 2)]
                keyword = parts[0]
                location: Optional[str] = None
                recency_hours: Optional[int] = None
                
                # Handle different line formats
                if len(parts) > 1 and parts[1]:  # Location is present
                    location_part = parts[1]
                    
                    # Check if location has a trailing number (space-separated recency)
                    location_parts = location_part.rsplit(' ', 1)
                    if len(location_parts) == 2:
                        potential_loc, potential_rec = location_parts
                        try:
                            # Try to parse the trailing part as a recency value
                            potential_rec_int = int(potential_rec)
                            if potential_rec_int > 0:
                                location = potential_loc
                                recency_hours = potential_rec_int
                            else:
                                location = location_part  # Keep as-is if not positive
                        except ValueError:
                            location = location_part  # Not a number, keep as-is
                    else:
                        location = location_part
                
                # Check for explicit recency as third parameter
                if len(parts) > 2 and parts[2]:
                    try:
                        explicit_rec = int(parts[2])
                        if explicit_rec > 0:
                            # Explicit recency overrides any space-separated one
                            recency_hours = explicit_rec
                    except ValueError:
                        logging.warning(f"Invalid recency value '{parts[2]}' for '{keyword}'. Must be a positive integer.")
                
                # Build the search URL with the parsed parameters
                search_url = build_search_url(keyword, location, recency_hours)
                urls.append(search_url)
                logging.debug(f"Built search URL for '{keyword}': {search_url}")
    else:
        logging.error("No source specified. Please provide --url, --search-url, or --terms-file.")
        return 1
    
    # 2) Process each URL
    for url in urls:
        logging.info(f"Processing URL: {url}")
        
        if "linkedin.com/jobs/view/" in url:
            # Direct job URL - process as a single job
            from process_linkedin_job import analyze_job
            job_result = analyze_job(
                url, 
                resume_path=args.resume,
                matching_profile=matching_profile
            )
            if job_result:
                all_jobs.append(job_result)
        
        elif "linkedin.com/jobs/search" in url:
            # Search URL - extract job listings and process them
            # Load resume for scoring jobs
            resume_text = None
            if os.path.exists(args.resume):
                with open(args.resume, 'r', encoding='utf-8') as f:
                    resume_text = f.read()
                logging.info(f"Loaded resume from {args.resume} for matching")
            
            # Extract jobs with match scores already calculated
            job_listings = extract_jobs_from_search_url(url, args.max_jobs, resume_text, matching_profile)
            if job_listings:
                logging.info(f"Extracted {len(job_listings)} job listings from search URL")
                processed_jobs = process_linkedin_jobs(
                    job_listings,
                    resume_path=args.resume,
                    max_jobs=args.max_jobs,
                    use_api=args.use_api,
                    save_html=args.save_html,
                    matching_profile=matching_profile
                )
                all_jobs.extend(processed_jobs)
            else:
                logging.warning(f"No job listings found in search URL: {url}")
        
        else:
            logging.warning(f"Unsupported URL format: {url}")
    
    # 3) Save all processed jobs
    if all_jobs:
        # Filter jobs by minimum score if specified
        if args.min_score > 0:
            original_count = len(all_jobs)
            all_jobs = [job for job in all_jobs if job.get('match_score', 0) >= args.min_score]
            logging.info(f"Filtered out {original_count - len(all_jobs)} jobs below minimum score of {args.min_score}")
        
        # Determine if we should export as markdown
        export_md = getattr(args, "export_md", False)
        
        # Save results with all URLs as source info
        source_info = ";".join(urls)
        save_and_export_results(
            all_jobs,
            output_path=args.output,
            export_md=export_md,
            source_info=source_info
        )
        return 0
    else:
        logging.error("No job listings were processed successfully.")
        return 1

def cmd_api(args):
    """Start the FastAPI server for the web interface."""
    import importlib.util
    
    # Check if uvicorn is installed
    if importlib.util.find_spec("uvicorn") is None:
        logging.error("uvicorn is required to run the API server. Install with 'pip install uvicorn'")
        return 1
    
    try:
        # Import and run the main function from api/run_api.py
        from api.run_api import main
        port = args.port if args.port else 8000
        host = args.host if args.host else "127.0.0.1"
        
        # Set environment variables if provided
        if port:
            os.environ["API_PORT"] = str(port)
        if host:
            os.environ["API_HOST"] = host
            
        logging.info(f"Starting API server on {host}:{port}")
        return main()
    except Exception as e:
        logging.error(f"Error starting API server: {e}")
        return 1

def cmd_web(args):
    """Start the Flask web application."""
    try:
        # Import and run the main function from web/app.py
        from web.app import main
        logging.info("Starting web application...")
        return main()
    except Exception as e:
        logging.error(f"Error starting web application: {e}")
        return 1

def main():
    """Main entry point for the command line interface."""
    parser = argparse.ArgumentParser(
        description="Job Matcher CLI - unified interface for all job_matcher functionality"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for jobs across multiple platforms")
    search_parser.add_argument("--terms", nargs="+", help="Search terms to use")
    search_parser.add_argument("--locations", nargs="+", default=["Remote", "Canada", "USA"], 
                             help="Locations to search in")
    search_parser.add_argument("--recency", type=float, default=24, 
                             help="Recency in hours (e.g., 0.1, 1, 5, 24, 72)")
    search_parser.add_argument("--google", action="store_true", default=True,
                             help="Use Google Custom Search API if available (default)")
    search_parser.add_argument("--no-google", action="store_false", dest="google",
                             help="Don't use Google Custom Search API")
    search_parser.add_argument("--max-jobs", type=int, default=10,
                             help="Maximum jobs to fetch per board/location")
    search_parser.add_argument("--simulate", action="store_true", help="Run in simulation mode")
    search_parser.add_argument("--output", help="Output file to save results")
    search_parser.set_defaults(func=cmd_search)
    
    # Match command
    match_parser = subparsers.add_parser("match", help="Calculate match scores for job listings against a resume")
    match_parser.add_argument("--resume", default="data/resume.txt", help="Resume file path")
    match_parser.add_argument("--min-score", type=float, default=0.6, help="Minimum match score (0-1)")
    match_parser.add_argument("--input", help="Input JSON file with job listings")
    match_parser.add_argument("--output", help="Output file to save results")
    match_parser.add_argument("--format", choices=["json", "markdown", "both"], default="both",
                            help="Output format (json, markdown, or both)")
    match_parser.set_defaults(func=cmd_match)
    
    # LinkedIn command
    linkedin_parser = subparsers.add_parser("linkedin", help="Process and analyze LinkedIn job postings")
    linkedin_parser.add_argument("--url", help="LinkedIn job URL to process")
    linkedin_parser.add_argument("--search-url", help="LinkedIn search URL to process multiple jobs")
    linkedin_parser.add_argument("--input", "-i", nargs="+", help="Path to JSON file(s) with LinkedIn job listings")
    linkedin_parser.add_argument("--terms-file", "-f", default="data/search_terms.txt", 
                               help="Path to file with search terms in format: 'keyword, location, recency'")
    linkedin_parser.add_argument("--resume", default="data/resume.txt", 
                               help="Resume file path")
    linkedin_parser.add_argument("--min-score", type=float, default=0.0, 
                               help="Minimum match score filter (0-1)")
    linkedin_parser.add_argument("--output", "-o", default="data/linkedin_jobs_analysis.json", 
                               help="Output file (default: data/linkedin_jobs_analysis.json)")
    linkedin_parser.add_argument("--max-jobs", type=int, default=5, 
                               help="Maximum number of jobs to process per search URL (default: 5)")
    linkedin_parser.add_argument("--save-html", action="store_true", 
                               help="Save raw HTML responses")
    linkedin_parser.add_argument("--export-md", action="store_true", 
                               help="Export results to Markdown format")
    linkedin_parser.add_argument("--debug", action="store_true", 
                               help="Enable debug logging")
    linkedin_parser.add_argument("-a", "--use-api", action="store_true", 
                               help="Fetch each job via the LinkedIn guest API instead of using fallback scraping")
    # Advanced matching options
    linkedin_parser.add_argument("--tfidf-weight", type=float, default=0.6,
                               help="Weight for TF-IDF text similarity (0.0 to 1.0, default: 0.6)")
    linkedin_parser.add_argument("--keyword-weight", type=float, default=0.3,
                               help="Weight for keyword matching (0.0 to 1.0, default: 0.3)")
    linkedin_parser.add_argument("--title-weight", type=float, default=0.1,
                               help="Weight for job title relevance (0.0 to 1.0, default: 0.1)")
    linkedin_parser.add_argument("--matching-mode", choices=["standard", "strict", "lenient"], default="standard",
                               help="Matching mode: standard, strict (requires more matches), or lenient (requires fewer matches)")
    linkedin_parser.add_argument("--quiet", "-q", action="store_true",
                               help="Suppress non-error output")
    linkedin_parser.set_defaults(func=cmd_linkedin)
    
    # API command
    api_parser = subparsers.add_parser("api", help="Start the FastAPI server for the web interface")
    api_parser.add_argument("--port", type=int, help="Port to run the API server on (default: 8000)")
    api_parser.add_argument("--host", help="Host to bind the API server to (default: 127.0.0.1)")
    api_parser.set_defaults(func=cmd_api)
    
    # Web command
    web_parser = subparsers.add_parser("web", help="Start the Flask web application")
    web_parser.set_defaults(func=cmd_web)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
        
    # Run the selected command
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
