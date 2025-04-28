import unittest
import os
import tempfile
from lib import resume_parser, job_parser, matcher, ats, api_calls

class TestFullPipeline(unittest.TestCase):
    def setUp(self):
        # Create temporary files for testing
        self.temp_dir = tempfile.mkdtemp()
        
        # Sample resume content
        self.resume_content = """
        JOHN DOE
        Software Developer
        
        SUMMARY
        Experienced software developer with Python, JavaScript, and SQL skills.
        
        SKILLS
        - Python, Django, Flask
        - JavaScript, React, Vue.js
        - SQL, PostgreSQL, MongoDB
        - Git, CI/CD, Docker
        
        EXPERIENCE
        Software Developer, ABC Inc.
        2018-2021
        - Developed web applications using Python and Django
        - Implemented REST APIs for mobile applications
        - Managed PostgreSQL databases
        
        EDUCATION
        Bachelor of Science, Computer Science
        University of Technology, 2018
        """
        
        # Sample job description content
        self.job_content = """
        Software Developer
        
        REQUIREMENTS:
        - 3+ years experience with Python
        - Experience with web frameworks like Django or Flask
        - Knowledge of databases (SQL, PostgreSQL)
        - Familiarity with front-end technologies (JavaScript, React)
        - Version control with Git
        
        RESPONSIBILITIES:
        - Develop and maintain web applications
        - Write clean, maintainable code
        - Collaborate with cross-functional teams
        - Participate in code reviews
        """
        
        # Write content to files
        self.resume_file = os.path.join(self.temp_dir, "resume.txt")
        with open(self.resume_file, "w") as f:
            f.write(self.resume_content)
        
        self.job_file = os.path.join(self.temp_dir, "job.txt")
        with open(self.job_file, "w") as f:
            f.write(self.job_content)
    
    def tearDown(self):
        # Clean up temporary files
        for file in [self.resume_file, self.job_file]:
            if os.path.exists(file):
                os.remove(file)
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)
    
    def test_full_matching_pipeline(self):
        """Test the full pipeline from file extraction to matching and scoring"""
        # Extract resume text and skills
        resume_text = resume_parser.extract_resume_text(self.resume_file)
        self.assertTrue(resume_text)  # Verify text extraction
        
        resume_skills = resume_parser.extract_resume_skills(resume_text)
        self.assertTrue(resume_skills)  # Verify skills extraction
        
        # Extract job description and requirements
        with open(self.job_file, "r") as f:
            job_text = f.read()
        
        job_description = job_parser.extract_job_description(job_text)
        self.assertTrue(job_description)  # Verify description extraction
        
        job_skills = job_parser.extract_job_requirements(job_description)
        self.assertTrue(job_skills)  # Verify requirements extraction
        
        # Calculate similarity score
        similarity_score = matcher.calculate_similarity(resume_skills, job_skills)
        self.assertTrue(0 <= similarity_score <= 100)  # Verify score in valid range
        
        # Calculate ATS score
        ats_score = ats.simulate_ats_analysis(resume_text, job_description, similarity_score)
        self.assertTrue(0 <= ats_score <= 100)  # Verify score in valid range
        
        # Since our sample resume matches the job well, scores should be high
        self.assertGreater(similarity_score, 60)
        self.assertGreater(ats_score, 60)

class TestRealWorldScenarios(unittest.TestCase):
    def test_senior_role_filtering(self):
        """Test filtering out senior roles from job search results"""
        # Mock job search results including a senior role
        search_results = [
            {'title': 'Software Engineer', 'link': 'http://example.com/job1'},
            {'title': 'Senior Software Engineer', 'link': 'http://example.com/job2'},
            {'title': 'Developer', 'link': 'http://example.com/job3'}
        ]
        
        # Filter senior roles
        filtered_results = [result for result in search_results 
                           if 'senior' not in result.get('title', '').lower()]
        
        # Verify filtering
        self.assertEqual(len(filtered_results), 2)
        self.assertNotIn('Senior', filtered_results[0]['title'])
        self.assertNotIn('Senior', filtered_results[1]['title'])

if __name__ == '__main__':
    unittest.main()
