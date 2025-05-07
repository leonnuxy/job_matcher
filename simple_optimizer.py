#!/usr/bin/env python3
"""
Simple script to test the resume optimizer with Gemini API.
"""

import os
import sys
import logging
from datetime import datetime

# Add parent directory to path to import the lib modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lib.api_calls import optimize_resume_with_gemini

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def optimize_resume_test():
    """Test the resume optimization function with the provided files"""
    
    logging.info("Starting resume optimization test...")
    
    try:
        # Read resume file
        resume_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "resume.txt")
        with open(resume_path, 'r') as file:
            resume_text = file.read()
        
        # Read job description file
        job_desc_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "job_descriptions", "job_description.txt")
        with open(job_desc_path, 'r') as file:
            job_description = file.read()
        
        logging.info("Files loaded successfully. Calling optimize_resume_with_gemini...")
        
        # Call the optimization function
        optimization_result = optimize_resume_with_gemini(resume_text, job_description)
        
        # Create output file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "optimization_results")
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_file = os.path.join(output_dir, f"resume_optimization_{timestamp}.txt")
        
        # Write results to file
        with open(output_file, 'w') as file:
            file.write(optimization_result)
        
        logging.info(f"Optimization complete. Results saved to {output_file}")
        
        # Print a preview of the results
        preview_length = min(500, len(optimization_result))
        print("\nOptimization Preview:")
        print("-" * 80)
        print(optimization_result[:preview_length] + "..." if len(optimization_result) > preview_length else optimization_result)
        print("-" * 80)
        
        return True
    except Exception as e:
        import traceback
        logging.error(f"Exception during optimization: {e}")
        logging.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    optimize_resume_test()
