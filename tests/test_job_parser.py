import unittest
from lib import job_parser

class TestExtractJobRequirements(unittest.TestCase):
    def test_extract_job_requirements_returns_list(self):
        sample_text = """
        We are looking for a Python developer with experience in SQL and AWS. 
        Responsibilities include building scalable applications and working with cloud infrastructure.
        """
        keywords = job_parser.extract_job_requirements(sample_text)
        self.assertIsInstance(keywords, list)
        for kw in keywords:
            self.assertIsInstance(kw, str)

    def test_extract_job_requirements_expected_keywords(self):
        sample_text = """
        Required skills: Python, SQL, AWS, Docker, Kubernetes. 
        Experience with cloud platforms and automation is a plus.
        """
        keywords = job_parser.extract_job_requirements(sample_text)
        joined = ' '.join(keywords).lower()
        self.assertIn('python', joined)
        self.assertIn('sql', joined)
        self.assertIn('aws', joined)

if __name__ == '__main__':
    unittest.main()
