import unittest
from lib import job_parser

SAMPLE_JOB_DESCRIPTION = """
We are seeking a Senior Python Developer to join our cloud engineering team. The ideal candidate will have experience with AWS, Docker, and Kubernetes. Responsibilities include designing scalable backend systems, working with REST APIs, and collaborating in an Agile environment. Required skills: Python, SQL, AWS, Docker, Kubernetes, REST, Agile, CI/CD, Linux.

Preferred qualifications:
- Experience with Terraform and infrastructure as code
- Familiarity with Prometheus and Grafana for monitoring
- Knowledge of GitHub Actions or Jenkins for CI/CD pipelines
- Strong communication and teamwork skills
"""

class TestExtractJobRequirementsRealistic(unittest.TestCase):
    def test_extract_job_requirements_realistic(self):
        keywords = job_parser.extract_job_requirements(SAMPLE_JOB_DESCRIPTION)
        joined = ' '.join(keywords).lower()
        # Check for presence of key skills
        self.assertIn('python', joined)
        self.assertIn('aws', joined)
        self.assertIn('docker', joined)
        self.assertIn('kubernetes', joined)
        self.assertIn('ci/cd', joined)
        self.assertIn('rest', joined)
        self.assertIn('agile', joined)
        # Check that the result is a list of strings
        self.assertIsInstance(keywords, list)
        for kw in keywords:
            self.assertIsInstance(kw, str)

if __name__ == '__main__':
    unittest.main()
