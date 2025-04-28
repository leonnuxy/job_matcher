import unittest
import os
from lib import resume_parser, job_parser

class TestResumeParser(unittest.TestCase):
    def setUp(self):
        self.sample_resume = """
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
    
    def test_extract_resume_skills_returns_list(self):
        """Test that extract_resume_skills returns a list"""
        skills = resume_parser.extract_resume_skills(self.sample_resume)
        self.assertIsInstance(skills, list)
        self.assertGreater(len(skills), 0)
    
    def test_extract_resume_skills_expected_keywords(self):
        """Test that extract_resume_skills extracts expected keywords"""
        skills = resume_parser.extract_resume_skills(self.sample_resume)
        expected_skills = ["python", "javascript", "sql", "django", "flask", "react", "postgresql", "mongodb", "git"]
        
        # Check that each expected skill is found (using lowercase for case-insensitive comparison)
        skills_lower = [s.lower() for s in skills]
        for skill in expected_skills:
            self.assertIn(skill.lower(), skills_lower)

class TestJobParser(unittest.TestCase):
    def setUp(self):
        self.sample_job_description = """
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
        
        self.html_job_description = """
        <html>
        <body>
        <h1>Software Developer</h1>
        <div class="requirements">
        <h2>Requirements:</h2>
        <ul>
        <li>3+ years experience with Python</li>
        <li>Experience with web frameworks like Django or Flask</li>
        <li>Knowledge of databases (SQL, PostgreSQL)</li>
        </ul>
        </div>
        </body>
        </html>
        """
    
    def test_extract_job_requirements_returns_list(self):
        """Test that extract_job_requirements returns a list"""
        requirements = job_parser.extract_job_requirements(self.sample_job_description)
        self.assertIsInstance(requirements, list)
        self.assertGreater(len(requirements), 0)
    
    def test_extract_job_requirements_expected_keywords(self):
        """Test that extract_job_requirements extracts expected keywords"""
        requirements = job_parser.extract_job_requirements(self.sample_job_description)
        expected_skills = ["python", "django", "flask", "sql", "postgresql", "javascript", "react", "git"]
        
        # Check that each expected skill is found (using lowercase for case-insensitive comparison)
        requirements_lower = [r.lower() for r in requirements]
        for skill in expected_skills:
            self.assertIn(skill.lower(), requirements_lower)
    
    def test_extract_job_description_from_html(self):
        """Test extracting job description from HTML"""
        description = job_parser.extract_job_description(self.html_job_description)
        self.assertIn("Python", description)
        self.assertIn("Django", description)
    
    def test_extract_job_description_plain_text(self):
        """Test extracting job description from plain text"""
        description = job_parser.extract_job_description(self.sample_job_description)
        self.assertEqual(description, self.sample_job_description.strip())
    
    def test_empty_input(self):
        """Test handling of empty input"""
        description = job_parser.extract_job_description("")
        self.assertEqual(description, "")
        
        requirements = job_parser.extract_job_requirements("")
        self.assertEqual(requirements, [])

class TestRealisticJobParsing(unittest.TestCase):
    def test_job_description_extraction_realistic(self):
        """Test extracting job description from a realistic job posting"""
        job_text = """
        Senior Python Developer
        
        Company: TechCorp Inc.
        Location: Remote, US
        
        About the Role:
        We're looking for an experienced Python Developer to join our team.
        
        Requirements:
        * 5+ years of professional Python experience
        * Experience with Django, Flask, or similar frameworks
        * Proficiency with SQL and NoSQL databases
        * Knowledge of RESTful APIs and microservices architecture
        * Experience with Git and CI/CD pipelines
        
        Benefits:
        * Competitive salary
        * Health insurance
        * 401(k) matching
        * Remote work flexibility
        """
        
        extracted = job_parser.extract_job_description(job_text)
        self.assertIn("Python", extracted)
        self.assertIn("microservices", extracted)
        
        requirements = job_parser.extract_job_requirements(job_text)
        expected = ["python", "django", "flask", "sql", "nosql", "restful", "microservices", "git", "ci/cd"]
        requirements_lower = [r.lower() for r in requirements]
        
        for req in expected:
            self.assertIn(req, requirements_lower, f"Missing: {req}")

if __name__ == '__main__':
    unittest.main()
