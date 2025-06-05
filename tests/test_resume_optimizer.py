import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import logging

# Add the parent directory to path to allow importing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import api_calls, matcher, resume_parser, job_parser

class TestResumeOptimizer(unittest.TestCase):
    def setUp(self):
        # Sample resume and job description for testing
        self.resume_text = """
        John Doe
        Software Developer
        
        SKILLS
        Python, JavaScript, React, Git, SQL
        
        EXPERIENCE
        Software Developer, ABC Inc.
        - Developed web applications using React and JavaScript
        - Created RESTful APIs with Python
        """
        
        self.job_description = """
        Software Engineer
        
        REQUIREMENTS:
        - 3+ years of Python experience
        - Experience with Django and Flask
        - Knowledge of cloud services (AWS)
        - Strong understanding of Git and CI/CD
        """

    @patch('lib.optimization_utils.genai')
    def test_generate_optimized_documents(self, mock_genai):
        """Test that Gemini AI integration works for resume optimization"""
        # Set up mock response
        from lib.optimization_utils import generate_optimized_documents
        
        mock_model = MagicMock()
        mock_genai.configure.return_value = None
        mock_genai.GenerativeModel.return_value = mock_model
        mock_response = MagicMock()
        
        # Mock a response with delimiters
        mock_response.text = """Some text before
        ---BEGIN_RESUME---
        John Doe Resume
        ---END_RESUME---
        
        Some text in between
        
        ---BEGIN_COVER_LETTER---
        Cover letter content
        ---END_COVER_LETTER---
        
        Some text after
        """
        
        mock_model.generate_content.return_value = mock_response
        
        # Call the function
        resume, cover_letter, raw_response = generate_optimized_documents(self.resume_text, self.job_description)
        
        # Check that the function called the AI model correctly
        mock_genai.configure.assert_called_once()
        mock_genai.GenerativeModel.assert_called_once()
        mock_model.generate_content.assert_called_once()
        
        # Check the results
        self.assertEqual(resume.strip(), "John Doe Resume")
        self.assertEqual(cover_letter.strip(), "Cover letter content")
        self.assertEqual(raw_response, mock_response.text)
        
    def test_real_resume_optimization(self):
        """Integration test with real files if available"""
        # Use the sample data directory
        resume_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'resume.txt')
        if not os.path.exists(resume_path):
            self.skipTest("Sample resume file not found")
            
        # Create a sample job description
        job_desc = """
        Python Developer
        
        We're looking for an experienced Python developer with skills in:
        - Django or Flask web frameworks
        - Cloud platforms like AWS or Azure
        - DevOps practices including CI/CD
        - Docker containerization
        - Version control with Git
        """
        
        # Load the resume
        with open(resume_path, 'r') as f:
            resume_text = f.read()
        
        # Mock the optimization utility to avoid actual API calls
        with patch('lib.optimization_utils.generate_optimized_documents') as mock_util:
            mock_util.return_value = ("Mocked resume", "Mocked cover letter", "Mocked raw response")
            
            # Run basic extraction to verify functionality
            resume_skills = resume_parser.extract_resume_skills(resume_text)
            job_skills = job_parser.extract_job_requirements(job_desc)
            
            # Print results for verification
            self.assertTrue(len(resume_skills) > 0, "No skills extracted from resume")
            self.assertTrue(len(job_skills) > 0, "No skills extracted from job description")
            
            print("\nTest Resume Optimization Results:")
            print(f"Resume Skills: {', '.join(resume_skills[:10])}...")
            print(f"Job Skills: {', '.join(job_skills)}")

if __name__ == '__main__':
    unittest.main()
