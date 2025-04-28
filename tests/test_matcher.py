import unittest
from unittest.mock import patch
from lib import matcher

class TestMatcherFunctions(unittest.TestCase):
    def test_perfect_match(self):
        """Test perfect match between resume and job skills"""
        resume_skills = ["python", "javascript", "sql", "react"]
        job_skills = ["python", "javascript", "sql", "react"]
        score = matcher.calculate_similarity(resume_skills, job_skills)
        self.assertEqual(score, 100.0)
    
    def test_partial_match(self):
        """Test partial match between resume and job skills"""
        resume_skills = ["python", "javascript", "sql"]
        job_skills = ["python", "javascript", "sql", "react", "node.js"]
        score = matcher.calculate_similarity(resume_skills, job_skills)
        self.assertEqual(score, 60.0)  # 3/5 = 60%
    
    def test_no_match(self):
        """Test no match between resume and job skills"""
        resume_skills = ["python", "javascript", "sql"]
        job_skills = ["java", "c++", "ruby"]
        score = matcher.calculate_similarity(resume_skills, job_skills)
        self.assertEqual(score, 0.0)
    
    def test_case_insensitivity(self):
        """Test case insensitivity in matching"""
        resume_skills = ["Python", "JavaScript", "SQL"]
        job_skills = ["python", "javascript", "sql"]
        score = matcher.calculate_similarity(resume_skills, job_skills)
        self.assertEqual(score, 100.0)
    
    def test_empty_job_skills(self):
        """Test handling of empty job skills list"""
        resume_skills = ["python", "javascript", "sql"]
        job_skills = []
        score = matcher.calculate_similarity(resume_skills, job_skills)
        self.assertEqual(score, 0.0)
    
    def test_empty_resume_skills(self):
        """Test handling of empty resume skills list"""
        resume_skills = []
        job_skills = ["python", "javascript", "sql"]
        score = matcher.calculate_similarity(resume_skills, job_skills)
        self.assertEqual(score, 0.0)

class TestResumeAdjustment(unittest.TestCase):
    def test_adjust_resume_suggestions(self):
        """Test generating resume adjustment suggestions"""
        resume_skills = ["python", "javascript", "sql"]
        job_skills = ["python", "javascript", "sql", "react", "docker"]
        suggestions = matcher.adjust_resume(resume_skills, job_skills)
        
        # Check that suggestions include missing skills
        self.assertIn("react", suggestions.lower())
        self.assertIn("docker", suggestions.lower())
    
    def test_adjust_resume_all_covered(self):
        """Test handling when all job skills are already in resume"""
        resume_skills = ["python", "javascript", "sql", "react", "docker"]
        job_skills = ["python", "javascript", "sql"]
        suggestions = matcher.adjust_resume(resume_skills, job_skills)
        
        # Check that suggestions indicate good match
        self.assertIn("good match", suggestions.lower())

class TestResumeOptimization(unittest.TestCase):
    @patch('lib.matcher.optimize_resume')
    def test_advanced_resume_optimization(self, mock_optimize):
        """Test advanced resume optimization functionality"""
        mock_optimize.return_value = "Optimized resume suggestions"
        
        resume_text = "Python developer with 5 years experience"
        job_description = "Looking for a Python developer with JavaScript skills"
        
        result = matcher.advanced_optimize_resume(resume_text, job_description)
        
        self.assertEqual(result, "Optimized resume suggestions")
        mock_optimize.assert_called_once()

if __name__ == '__main__':
    unittest.main()
