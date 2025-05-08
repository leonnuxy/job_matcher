"""
Script to run the job search and matching process.
"""
import argparse
import logging
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from job_search.search import main as search_main
from job_search.matcher import main as matcher_main

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """
    Main entry point for job search and matching.
    """
    parser = argparse.ArgumentParser(description="Run job search and resume matching")
    parser.add_argument("--search-only", action="store_true", help="Only run job search, not matching")
    parser.add_argument("--match-only", action="store_true", help="Only run job matching, not search")
    parser.add_argument("--simulate", action="store_true", help="Run in simulation mode")
    parser.add_argument("--terms", nargs="+", help="Search terms to use (overrides search_terms.txt)")
    parser.add_argument("--locations", nargs="+", default=["Remote", "Canada", "USA"], 
                       help="Locations to search in")
    parser.add_argument("--recency", type=float, default=24, 
                       help="Recency in hours (e.g., 0.1, 1, 5, 24, 72)")
    parser.add_argument("--google", action="store_true", default=True,
                       help="Use Google Custom Search API if available (default)")
    parser.add_argument("--no-google", action="store_false", dest="google", 
                       help="Don't use Google Custom Search API")
    parser.add_argument("--max-jobs", type=int, default=10, 
                       help="Maximum jobs to fetch per board/location")
    args = parser.parse_args()
    
    # Set simulation mode environment variable if requested
    if args.simulate:
        os.environ["SIMULATION_MODE"] = "1"
        logging.info("Running in simulation mode")
    elif os.getenv("TESTING", "").lower() in ("true", "1", "yes"):
        # Also enable simulation mode during testing
        os.environ["SIMULATION_MODE"] = "1"
        logging.info("Running in simulation mode (TESTING=true)")
    
    # Check for Google Custom Search API credentials
    from dotenv import load_dotenv
    load_dotenv()
    has_google_api = bool(os.getenv('GOOGLE_API_KEY') and os.getenv('GOOGLE_CSE_ID'))
    
    if args.google and not has_google_api:
        logging.warning("Google Custom Search API credentials not found in environment variables.")
        logging.warning("Set GOOGLE_API_KEY and GOOGLE_CSE_ID in .env file or use --no-google")
    
    search_args = []
    if args.terms:
        search_args.extend(["--terms"] + args.terms)
    if args.locations:
        search_args.extend(["--locations"] + args.locations)
    if args.recency:
        search_args.extend(["--recency", str(args.recency)])
    if args.google:
        search_args.append("--google")
    else:
        search_args.append("--no-google")
    if args.max_jobs:
        search_args.extend(["--max-jobs", str(args.max_jobs)])
    
    if args.search_only:
        # Run only job search
        logging.info("Running job search only...")
        import sys
        sys.argv = [sys.argv[0]] + search_args
        search_main()
    elif args.match_only:
        # Run only job matching
        logging.info("Running job matching only...")
        matcher_main()
    else:
        # Run both
        logging.info("Running job search and matching...")
        import sys
        sys.argv = [sys.argv[0]] + search_args
        search_main()
        matcher_main()
    
    logging.info("Process complete!")

if __name__ == "__main__":
    main()
