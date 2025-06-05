"""
CLI interface for the resume optimizer.

This module provides a command-line interface to the resume optimizer package,
allowing it to be run directly from the command line with arguments.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime

from resume_optimizer import optimize_resume
from lib.optimization_utils import extract_text_between_delimiters, clean_generated_cover_letter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cli_main():
    """Main CLI entry point for the resume optimizer."""
    parser = argparse.ArgumentParser(description="Optimize a resume and generate a cover letter for a specific job")
    parser.add_argument("job_description", help="Path to the job description file")
    parser.add_argument("--resume", "-r", help="Path to the resume file (default: data/resume.txt)")
    parser.add_argument("--output-dir", "-o", help="Output directory for optimized files")
    
    args = parser.parse_args()
    
    # Determine paths
    project_root = Path(__file__).parent.parent
    resume_path = args.resume or project_root / "data" / "resume.txt"
    output_dir = args.output_dir or project_root / "data" / "optimization_results"
    
    # Validate input files
    if not os.path.isfile(args.job_description):
        logger.error(f"Job description file not found: {args.job_description}")
        return 1
        
    if not os.path.isfile(resume_path):
        logger.error(f"Resume file not found: {resume_path}")
        return 1
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Read input files
    try:
        with open(resume_path, "r", encoding='utf-8') as f:
            resume_text = f.read()
        
        with open(args.job_description, "r", encoding='utf-8') as f:
            job_description = f.read()
    except Exception as e:
        logger.error(f"Error reading input files: {e}")
        return 1
    
    # Run optimization
    try:
        logger.info("Optimizing resume...")
        result = optimize_resume(resume_text, job_description)
        
        # Generate output paths
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_name = Path(args.job_description).stem
        base_name = f"{job_name}_{timestamp}"
        
        # For compatibility with the existing prompt.txt format, check if the result 
        # contains delimiter-marked sections for the resume and cover letter
        raw_text = str(result)
        resume_content = extract_text_between_delimiters(raw_text, "---BEGIN_RESUME---", "---END_RESUME---")
        cover_letter_content = extract_text_between_delimiters(raw_text, "---BEGIN_COVER_LETTER---", "---END_COVER_LETTER---")
        
        # If we found delimited content, use that; otherwise use the structured result
        if resume_content:
            logger.info("Found resume content with delimiters")
            resume_file = Path(output_dir) / f"{base_name}_resume.md"
            with open(resume_file, "w", encoding='utf-8') as f:
                f.write(resume_content)
            logger.info(f"Resume saved to: {resume_file}")
        else:
            # Generate a resume file from the structured result
            logger.info("Using structured result for resume content")
            resume_file = Path(output_dir) / f"{base_name}_resume.md"
            with open(resume_file, "w", encoding='utf-8') as f:
                f.write(f"# Resume Optimization Results\n\n")
                f.write(f"## Summary\n{result['summary']}\n\n")
                f.write("## Skills to Add\n")
                for skill in result['skills_to_add']:
                    f.write(f"- {skill}\n")
                f.write("\n## Skills to Remove\n")
                for skill in result['skills_to_remove']:
                    f.write(f"- {skill}\n")
                f.write("\n## Experience Improvements\n")
                for tweak in result['experience_tweaks']:
                    f.write(f"### Original\n{tweak['original']}\n\n")
                    f.write(f"### Improved\n{tweak['optimized']}\n\n")
            logger.info(f"Resume suggestions saved to: {resume_file}")

        # Handle the cover letter
        if cover_letter_content:
            cover_letter_content = clean_generated_cover_letter(cover_letter_content)
            cover_letter_file = Path(output_dir) / f"{base_name}_cover_letter.md"
            
            with open(cover_letter_file, "w", encoding='utf-8') as f:
                f.write(cover_letter_content)
                
            # Also save as latest_cover_letter.md for easy access
            with open(Path(output_dir) / "latest_cover_letter.md", "w", encoding='utf-8') as f:
                f.write(cover_letter_content)
                
            logger.info(f"Cover letter saved to: {cover_letter_file}")
        
        logger.info("Optimization completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error during optimization: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(cli_main())
