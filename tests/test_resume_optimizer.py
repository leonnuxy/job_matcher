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

    @patch('lib.api_calls.genai')
    def test_optimize_resume_with_gemini(self, mock_genai):
        """Test that Gemini AI integration works for resume optimization"""
        # Set up mock response
        mock_model = MagicMock()
        mock_genai.configure.return_value = None
        mock_genai.GenerativeModel.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "1. Add Django experience\n2. Highlight AWS knowledge\n3. Emphasize Python skills"
        mock_model.generate_content.return_value = mock_response
        
        # Call the function
        result = api_calls.optimize_resume_with_gemini(self.resume_text, self.job_description)
        
        # Check that the function called the AI model correctly
        mock_genai.configure.assert_called_once()
        mock_genai.GenerativeModel.assert_called_once_with('gemini-pro')
        mock_model.generate_content.assert_called_once()
        
        # Check that the prompt included both resume and job description
        call_args = mock_model.generate_content.call_args[0][0]
        self.assertIn("RESUME:", call_args)
        self.assertIn("JOB DESCRIPTION:", call_args)
        
        # Check the result
        self.assertEqual(result, "1. Add Django experience\n2. Highlight AWS knowledge\n3. Emphasize Python skills")
        
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
        
        # Mock the AI function to avoid actual API calls
        with patch('lib.api_calls.optimize_resume_with_gemini') as mock_ai:
            mock_ai.return_value = "Mocked AI optimization response"
            
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
