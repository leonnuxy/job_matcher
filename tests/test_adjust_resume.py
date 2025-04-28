import unittest
from lib import matcher, resume_parser, job_parser

class TestAdjustResume(unittest.TestCase):
    def test_adjust_resume_suggestions(self):
        resume_text = """
        John Doe
        Python Developer with experience in AWS and Docker.
        """
        job_text = """
        Required: Python, AWS, Docker, Kubernetes, SQL
        """
        job_skills = job_parser.extract_job_requirements(job_text)
        suggestions = matcher.adjust_resume(resume_text, job_skills)
        self.assertIn('kubernetes', suggestions.lower())
        self.assertIn('sql', suggestions.lower())
        self.assertIn('Experience with kubernetes.', suggestions)
        self.assertIn('Experience with sql.', suggestions)
        self.assertNotIn('python', suggestions.lower())
        self.assertNotIn('aws', suggestions.lower())
        self.assertNotIn('docker', suggestions.lower())

    def test_adjust_resume_all_covered(self):
        resume_text = """
        Python Developer with experience in AWS, Docker, Kubernetes, SQL.
        """
        job_text = """
        Required: Python, AWS, Docker, Kubernetes, SQL
        """
        job_skills = job_parser.extract_job_requirements(job_text)
        suggestions = matcher.adjust_resume(resume_text, job_skills)
        self.assertIn('already covers all key job requirements', suggestions.lower())

if __name__ == '__main__':
    unittest.main()
