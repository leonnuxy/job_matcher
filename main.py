#!/usr/bin/env python3
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
    python main.py linkedin --url "https://www.linkedin.com/jobs/view/123456789"
    python main.py api --port 8000
    python main.py web
"""
import os
import sys
import argparse
import logging
from dotenv import load_dotenv

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
        return search_main()
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
    # Import necessary modules
    import sys
    
    # Set up the path to find modules
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Import process_linkedin_job functionality
    # Since the main functionality is in process_linkedin_job.py, we'll import from there
    sys.argv = [sys.argv[0]]
    
    # Add command line arguments
    if args.url:
        sys.argv.extend(["--url", args.url])
    if args.search_url:
        sys.argv.extend(["--search-url", args.search_url])
    if args.resume:
        sys.argv.extend(["--resume", args.resume])
    if args.min_score is not None:
        sys.argv.extend(["--min-score", str(args.min_score)])
    if args.output_dir:
        sys.argv.extend(["--output-dir", args.output_dir])
    if args.save_html:
        sys.argv.append("--save-html")
    if args.debug:
        sys.argv.append("--debug")
        
    try:
        # Import and run the main function from process_linkedin_job.py
        from process_linkedin_job import main
        return main()
    except Exception as e:
        logging.error(f"Error in LinkedIn command: {e}")
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
    linkedin_parser.add_argument("--resume", default="data/resume.txt", help="Resume file path")
    linkedin_parser.add_argument("--min-score", type=float, default=0.0, help="Minimum match score filter (0-1)")
    linkedin_parser.add_argument("--output-dir", default="data/linkedin_jobs", help="Output directory")
    linkedin_parser.add_argument("--save-html", action="store_true", help="Save raw HTML responses")
    linkedin_parser.add_argument("--debug", action="store_true", help="Enable debug logging")
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