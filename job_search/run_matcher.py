#!/usr/bin/env python3
"""
Command-line interface for the job matching functionality.
"""
import os
import argparse
from typing import Dict, Any, Optional
from matcher import main as run_matcher

# Set up the command line argument parser
def parse_args() -> Dict[str, Any]:
    """
    Parse command line arguments.
    
    Returns:
        Dictionary with parsed arguments
    """
    parser = argparse.ArgumentParser(description="Match resume against job listings")
    
    # Required parameters
    parser.add_argument(
        "-r", "--resume-path",
        help="Path to the resume file (defaults to default resume path)",
        type=str
    )
    
    # Optional parameters
    parser.add_argument(
        "-d", "--results-dir",
        help="Directory with job search results or path to a JSON file with job data",
        type=str
    )
    
    parser.add_argument(
        "-t", "--threshold",
        help="Minimum match score threshold (0.0-1.0, default: 0.5)",
        type=float,
        default=0.5
    )
    
    parser.add_argument(
        "-n", "--top-n",
        help="Number of top matches to process (default: 3)",
        type=int,
        default=3
    )
    
    parser.add_argument(
        "-c", "--with-cover-letter",
        help="Generate cover letters for matching jobs",
        action="store_true"
    )
    
    return vars(parser.parse_args())


def main():
    """
    Main entry point for the command-line interface.
    """
    args = parse_args()
    
    # Make path absolute if provided
    if args.get("resume_path") and not os.path.isabs(args["resume_path"]):
        args["resume_path"] = os.path.abspath(args["resume_path"])
    
    if args.get("results_dir") and not os.path.isabs(args["results_dir"]):
        args["results_dir"] = os.path.abspath(args["results_dir"])
    
    # Call the matcher's main function with the parsed arguments
    run_matcher(
        resume_path=args.get("resume_path"),
        results_dir=args.get("results_dir"),
        match_threshold=args.get("threshold"),
        top_n=args.get("top_n"),
        with_cover_letter=args.get("with_cover_letter")
    )


if __name__ == "__main__":
    main()
