import unittest
from lib import ats

class TestATSFunctions(unittest.TestCase):
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
        
        self.sample_job = """
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
    
    def test_skills_extraction(self):
        """Test extraction of skills from text"""
        skills = ats.extract_skills_simple(self.sample_resume)
        expected_skills = ["python", "javascript", "sql", "django", "flask", "react", "postgresql", "mongodb", "git", "docker"]
        
        skills_lower = [s.lower() for s in skills]
        for skill in expected_skills:
            self.assertIn(skill, skills_lower)
    
    def test_similarity_calculation(self):
        """Test calculation of similarity between resume and job skills"""
        resume_skills = ["python", "javascript", "sql", "django", "flask"]
        job_skills = ["python", "django", "postgresql", "react", "git"]
        
        similarity = ats.calculate_similarity_simple(resume_skills, job_skills)
        # 3 out of 5 skills match (python, django) = 60%
        self.assertEqual(similarity, 60.0)
    
    def test_ats_analysis(self):
        """Test ATS analysis with resume and job text"""
        ats_score = ats.simulate_ats_analysis(self.sample_resume, self.sample_job)
        
        # Verify score is in reasonable range
        self.assertTrue(0 <= ats_score <= 100)
        # Since this example has good matching skills, score should be reasonable
        self.assertGreater(ats_score, 50)
    
    def test_get_matching_skills(self):
        """Test getting matching skills between resume and job"""
        result = ats.get_matching_skills(self.sample_resume, self.sample_job)
        
        self.assertIn('matched_skills', result)
        self.assertIn('missing_skills', result)
        self.assertIn('resume_skills', result)
        self.assertIn('job_skills', result)
        
        # Check that expected skills are in matched skills
        expected_matches = ["python", "django", "flask", "sql", "postgresql", "javascript", "react", "git"]
        matched_lower = [s.lower() for s in result['matched_skills']]
        
        for skill in expected_matches:
            self.assertIn(skill, matched_lower)

class TestATSEdgeCases(unittest.TestCase):
    def test_empty_inputs(self):
        """Test handling of empty inputs"""
        score = ats.simulate_ats_analysis("", "")
        self.assertEqual(score, 0.0)
        
        score = ats.simulate_ats_analysis("Python developer", "")
        self.assertEqual(score, 0.0)
        
        score = ats.simulate_ats_analysis("", "Python developer needed")
        self.assertEqual(score, 0.0)
    
    def test_no_matching_skills(self):
        """Test handling of no matching skills"""
        resume = "Java developer with Spring and Hibernate"
        job = "Looking for a Python developer with Django experience"
        
        score = ats.simulate_ats_analysis(resume, job)
        self.assertLess(score, 50)  # Score should be low but not zero due to section weights

if __name__ == '__main__':
    unittest.main()
