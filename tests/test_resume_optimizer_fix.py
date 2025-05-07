#!/usr/bin/env python3
"""
Test for the fixed resume optimizer using Gemini API.
"""

import os
import sys
import logging

# Add parent directory to path to import the lib modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.api_calls import optimize_resume_with_gemini

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_optimize_resume_with_gemini():
    """Test the resume optimization function with a sample resume and job description"""
    
    print("Starting test_optimize_resume_with_gemini...")
    
    try:
        # Sample resume
        resume_text = """
        JOHN DOE
        Software Engineer
        john.doe@email.com | (123) 456-7890 | linkedin.com/in/johndoe
        
        SKILLS
        Programming: Python, JavaScript, React, HTML, CSS
        Tools: Git, Docker, VS Code, Jira
        
        EXPERIENCE
        Software Engineer, ABC Tech
        May 2020 - Present
        - Developed and maintained web applications using React and Node.js
        - Collaborated with cross-functional teams to implement new features
        - Improved application performance by 25% through code optimization
        
        Junior Developer, XYZ Software
        Jan 2018 - Apr 2020
        - Built responsive web interfaces using HTML, CSS, and JavaScript
        - Participated in code reviews and testing processes
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology, 2017
        """
        
        # Sample job description - keep it very short for testing purposes
        job_description = """
        Senior Python Developer
        
        Requirements:
        - Python development
        - AWS skills
        - REST APIs
        """
        
        print("Calling optimize_resume_with_gemini...")
        
        # Test the optimization function
        optimization_result = optimize_resume_with_gemini(resume_text, job_description)
        
        print(f"Got result type: {type(optimization_result)}, length: {len(str(optimization_result))}")
        
        # Check if the optimization was successful
        if isinstance(optimization_result, str) and optimization_result.startswith("Resume optimization failed"):
            print("Test failed:", optimization_result)
            return False
        else:
            print("Test passed! Resume optimization successful.")
            print("\nOptimization suggestions (first 500 chars):")
            print(str(optimization_result)[:500] + "..." if len(str(optimization_result)) > 500 else optimization_result)
            return True
    except Exception as e:
        import traceback
        print(f"Exception during test: {e}")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    test_optimize_resume_with_gemini()
