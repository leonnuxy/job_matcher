#!/usr/bin/env python3
"""
Script to test the updated prompt.txt format for resume optimization.

DEPRECATION NOTICE: This script is being maintained for backward compatibility.
For new code, please use the resume_optimizer package CLI instead:
    python -m resume_optimizer.cli <job_description_file>

Or import the package in your code:
    from resume_optimizer import optimize_resume
    result = optimize_resume(resume_text, job_description)
"""

import os
import sys
import logging
import argparse
from datetime import datetime

# Add project root to path so local modules (e.g. config.py) can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Assuming lib is in the project root, and this script is also in the project root.
# If test_prompt.py moves to a tests/ subdirectory, sys.path might need:
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.optimization_utils import generate_optimized_documents, extract_text_between_delimiters, clean_generated_cover_letter

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def optimize_resume_with_custom_prompt(job_desc_path: str = None) -> bool:
    """Test resume optimization with our custom prompt from prompt.txt."""

    logging.info("Starting resume optimization test with custom prompt...")

    try:
        # 1) Read the local resume file
        # Consider using DATA_DIR from config for consistency
        # from config import DATA_DIR
        resume_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "resume.txt") # Assuming script is in project root
        with open(resume_path, 'r') as file:
            resume_text = file.read()

        # 2) Determine which job description to use (argument or default)
        if job_desc_path is None:
            job_desc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "job_desc.txt")

        logging.info(f"Using job description file: {job_desc_path}")
        with open(job_desc_path, 'r') as file:
            job_description = file.read()

        logging.info("Files loaded successfully. Calling generation utility...")
        
        # 3) Call the centralized utility
        resume_content, cover_letter_content, full_response_text = generate_optimized_documents(resume_text, job_description)

        # 6) Prepare output directory and timestamp
        # Consider using RESULTS_DIR from config
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "optimization_results")
        os.makedirs(output_dir, exist_ok=True)

        base_name = f"custom_prompt_resume_optimization_{timestamp}"

        # 7) Extract resume & cover letter sections from the payload
        # This is now handled by generate_optimized_documents

        # 9) If no sections could be extracted, warn + save fallback
        if not resume_content and not cover_letter_content and full_response_text:
            logging.warning("Could not extract resume or cover letter sections from the Gemini response. Saving full response.")
            fallback_file = os.path.join(output_dir, f"{base_name}_fallback.md")
            with open(fallback_file, 'w') as file:
                file.write(full_response_text)
            print("\nWARNING: Could not extract resume or cover letter sections from the Gemini response.")
            print("Saved the full content to:", fallback_file)
            return True
        elif not full_response_text: # Indicates an error during generation
            logging.error("Document generation failed. See previous logs.")
            return False
        # 10) Save resume content
        if resume_content:
            resume_file = os.path.join(output_dir, f"{base_name}_resume.md")
            with open(resume_file, 'w') as file:
                file.write(resume_content)
            logging.info(f"Resume content saved to: {resume_file}")
        else:
            logging.warning("Could not extract resume section from the response.")

        # 11) Save cover letter content
        if cover_letter_content:
            cover_letter_file = os.path.join(output_dir, f"{base_name}_cover.md")
            with open(cover_letter_file, 'w') as file:
                file.write(cover_letter_content)
            logging.info(f"Cover letter content saved to: {cover_letter_file}")
        else:
            logging.warning("Could not extract cover letter section from the response.")

        logging.info(f"Optimization complete. Results saved to {output_dir}")

        # 12) Print a short preview of the result
        preview_length = min(500, len(full_response_text) if full_response_text else 0)
        print("\nOptimization Preview:")
        print("-" * 80)
        if full_response_text and len(full_response_text) > preview_length:
            print(full_response_text[:preview_length] + "...")
        elif full_response_text:
            print(full_response_text)
        print("-" * 80)

        # 13) Print locations of created files
        print(f"\nFiles created:")
        if resume_content:
            print(f"- Resume: {resume_file}")
        if cover_letter_content:
            print(f"- Cover letter: {cover_letter_file}")

        return True

    except Exception as e:
        import traceback
        logging.error(f"Exception during optimization: {e}")
        logging.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Optimize a resume using a custom prompt template.')
    parser.add_argument('--job-desc', dest='job_desc_file', help='Path to the job description file')
    args = parser.parse_args()

    success = optimize_resume_with_custom_prompt(args.job_desc_file)
    if not success:
        sys.exit(1)
