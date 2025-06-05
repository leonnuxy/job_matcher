#!/usr/bin/env python3
"""
Test suite for the resume_optimizer package.
This replaces the deprecated test_prompt.py and simple_optimizer.py.
"""

import os
import sys
import unittest
import logging
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path to enable imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import main components for testing
from resume_optimizer import optimize_resume
from lib.optimization_utils import generate_optimized_documents, extract_text_between_delimiters

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class TestResumeOptimizerPackage(unittest.TestCase):
    """Test cases for the resume_optimizer package and utilities"""
    
    def setUp(self):
        """Setup test data for all test cases"""
        # Define test data paths
        data_dir = Path(__file__).parent / "data"
        self.resume_path = data_dir / "test_resume.txt"
        self.job_desc_path = data_dir / "test_job_desc.txt"
        
        # Create test data directory if it doesn't exist
        data_dir.mkdir(exist_ok=True)
        
        # Create test files if they don't exist
        if not self.resume_path.exists():
            with open(self.resume_path, 'w') as f:
                f.write("""
                JOHN DOE
                Software Engineer
                john.doe@email.com | (123) 456-7890 | linkedin.com/in/johndoe
                
                SKILLS
                Programming: Python, JavaScript, React, HTML, CSS
                Tools: Git, Docker, VS Code, Jira
                
                EXPERIENCE
                Software Engineer, ABC Tech
                May 2020 - Present
                - Developed web applications using React and Node.js
                - Improved application performance by 25% through code optimization
                
                EDUCATION
                Bachelor of Science in Computer Science, University of Technology, 2017
                """)
        
        if not self.job_desc_path.exists():
            with open(self.job_desc_path, 'w') as f:
                f.write("""
                Senior Python Developer
                
                Requirements:
                - 5+ years of Python development experience
                - Experience with Flask or Django web frameworks
                - AWS cloud infrastructure knowledge
                - REST API design and implementation
                - SQL database experience
                - CI/CD pipeline setup and maintenance
                
                Responsibilities:
                - Develop and maintain Python-based microservices
                - Collaborate with cross-functional teams
                - Implement automated testing
                - Participate in code reviews
                """)
        
        # Load test data
        with open(self.resume_path, 'r') as f:
            self.resume_text = f.read()
        
        with open(self.job_desc_path, 'r') as f:
            self.job_description = f.read()
    
    @patch('lib.optimization_utils.genai')
    def test_optimization_utility(self, mock_genai):
        """Test the optimization utility function"""
        # Setup the mock response
        mock_model = MagicMock()
        mock_genai.configure.return_value = None
        mock_genai.GenerativeModel.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = """
        ---BEGIN_RESUME---
        JOHN DOE
        Software Engineer
        Skills: Python, JavaScript
        ---END_RESUME---
        
        ---BEGIN_COVER_LETTER---
        Dear Hiring Manager,
        I am writing to apply...
        ---END_COVER_LETTER---
        """
        mock_model.generate_content.return_value = mock_response
        
        resume, cover_letter, raw_response = generate_optimized_documents(self.resume_text, self.job_description)
        
        # Check that we got results
        self.assertIsNotNone(raw_response, "Raw response should not be None")
        
        # At least one of resume or cover letter should be non-None
        self.assertTrue(resume is not None or cover_letter is not None, 
                      "Either resume or cover letter should be non-None")
        
        if resume:
            self.assertIn("JOHN DOE", resume, "Resume should contain the name")
        
        if cover_letter:
            self.assertNotIn("[Date]", cover_letter, "Cover letter should not contain placeholder dates")
    
    def test_extract_delimiters(self):
        """Test the delimiter extraction function"""
        test_text = """Some text before
        
        ---BEGIN_RESUME---
        This is a resume
        Multiple lines
        ---END_RESUME---
        
        Something in between
        
        ---BEGIN_COVER_LETTER---
        This is a cover letter
        ---END_COVER_LETTER---
        
        Text after
        """
        
        resume = extract_text_between_delimiters(test_text, "---BEGIN_RESUME---", "---END_RESUME---")
        cover = extract_text_between_delimiters(test_text, "---BEGIN_COVER_LETTER---", "---END_COVER_LETTER---")
        
        self.assertEqual(resume.strip(), "This is a resume\n        Multiple lines")
        self.assertEqual(cover.strip(), "This is a cover letter")
    
    def test_resume_optimizer_package(self):
        """Test the main resume_optimizer package function"""
        try:
            result = optimize_resume(self.resume_text, self.job_description)
            
            # Check that result is a dictionary with expected keys
            self.assertIsInstance(result, dict, "Result should be a dictionary")
            self.assertIn("summary", result, "Result should have a summary")
            self.assertIn("skills_to_add", result, "Result should have skills_to_add")
            self.assertIn("skills_to_remove", result, "Result should have skills_to_remove")
            
            # Check that skills to add include some expected skills
            skills_to_add = [skill.lower() for skill in result["skills_to_add"]]
            expected_skills = ["flask", "django", "aws"]
            found = any(skill in " ".join(skills_to_add) for skill in expected_skills)
            self.assertTrue(found, f"Skills to add should include at least one of {expected_skills}")
            
        except Exception as e:
            self.fail(f"optimize_resume() raised {type(e).__name__} unexpectedly: {e}")


def main():
    """Run tests from command line"""
    unittest.main()


if __name__ == "__main__":
    main()
