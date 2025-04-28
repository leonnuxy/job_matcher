import unittest
from lib import resume_parser

class TestExtractResumeSkills(unittest.TestCase):
    def test_extract_resume_skills_returns_list(self):
        sample_text = """
        John Doe
        Python Developer with experience in Python 3.9, SQL, AWS, Docker, and Kubernetes.
        Led cloud migration projects using Terraform and Jenkins. Strong background in REST APIs and Agile teams.
        """
        skills = resume_parser.extract_resume_skills(sample_text)
        self.assertIsInstance(skills, list)
        for skill in skills:
            self.assertIsInstance(skill, str)

    def test_extract_resume_skills_expected_keywords(self):
        sample_text = """
        Senior Software Engineer skilled in Python 3.8, SQL, AWS, Docker, Kubernetes, and Linux. Experience with Prometheus, Grafana, and CI/CD pipelines.
        """
        skills = resume_parser.extract_resume_skills(sample_text)
        joined = ' '.join(skills).lower()
        self.assertIn('python 3.8', joined)
        self.assertIn('sql', joined)
        self.assertIn('aws', joined)
        self.assertIn('docker', joined)
        self.assertIn('kubernetes', joined)
        self.assertIn('linux', joined)
        self.assertIn('prometheus', joined)
        self.assertIn('grafana', joined)
        self.assertIn('ci/cd', joined)

if __name__ == '__main__':
    unittest.main()
