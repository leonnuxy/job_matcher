import unittest
from lib import resume_parser, job_parser, matcher

class TestFullPipelineRealData(unittest.TestCase):
    def test_full_pipeline(self):
        # 1. Extract resume text from real file
        resume_path = 'data/resume.txt'
        resume_text = resume_parser.extract_resume_text(resume_path)
        self.assertTrue(resume_text)

        # 2. Extract skills from resume
        resume_skills = resume_parser.extract_resume_skills(resume_text)
        self.assertIsInstance(resume_skills, list)
        self.assertGreater(len(resume_skills), 0)

        # 3. Use a realistic job description
        job_text = """
        We are seeking a Senior Python Developer to join our cloud engineering team. The ideal candidate will have experience with AWS, Docker, and Kubernetes. Responsibilities include designing scalable backend systems, working with REST APIs, and collaborating in an Agile environment. Required skills: Python, SQL, AWS, Docker, Kubernetes, REST, Agile, CI/CD, Linux.
        Preferred qualifications: Experience with Terraform, Prometheus, Grafana, GitHub Actions, Jenkins.
        """
        job_skills = job_parser.extract_job_requirements(job_text)
        self.assertIsInstance(job_skills, list)
        self.assertGreater(len(job_skills), 0)

        # 4. Calculate similarity
        score = matcher.calculate_similarity(resume_skills, job_skills)
        print(f"Resume-Job Similarity Score: {score}%")
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)

if __name__ == '__main__':
    unittest.main()
