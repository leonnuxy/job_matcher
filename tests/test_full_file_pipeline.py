import unittest
from lib import resume_parser, job_parser, matcher, ats

class TestFileBasedPipeline(unittest.TestCase):
    def test_resume_and_job_file_extraction_and_matching(self):
        # Read resume
        with open('tests/test_resume.txt', 'r', encoding='utf-8') as f:
            resume_text = f.read()
        resume_skills = resume_parser.extract_resume_skills(resume_text)
        self.assertIsInstance(resume_skills, list)
        # Read job description
        with open('tests/test_job_desc.txt', 'r', encoding='utf-8') as f:
            job_text = f.read()
        job_skills = job_parser.extract_job_requirements(job_text)
        self.assertIsInstance(job_skills, list)
        # Calculate similarity
        score = matcher.calculate_similarity(resume_skills, job_skills)
        print(f"Resume-Job Similarity Score: {score}%")
        self.assertIsInstance(score, float)
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)
        # ATS analysis
        ats_score = ats.simulate_ats_analysis(resume_text, job_text, score)
        print(f"ATS Simulation Score: {ats_score}%")
        self.assertIsInstance(ats_score, float)
        self.assertGreaterEqual(ats_score, 0.0)
        self.assertLessEqual(ats_score, 100.0)
    def test_extracted_job_file(self):
        # Read extracted job info
        with open('tests/test_extracted_job.txt', 'r', encoding='utf-8') as f:
            job_info = f.read()
        # Extract job description section
        import re
        desc_match = re.search(r'Description: (.*?)\nLink:', job_info, re.DOTALL)
        job_desc = desc_match.group(1) if desc_match else job_info
        job_skills = job_parser.extract_job_requirements(job_desc)
        self.assertIsInstance(job_skills, list)
        self.assertIn('python 3.9', ' '.join(job_skills).lower())
        self.assertIn('aws', ' '.join(job_skills).lower())
        self.assertIn('docker', ' '.join(job_skills).lower())
        self.assertIn('kubernetes', ' '.join(job_skills).lower())

if __name__ == '__main__':
    unittest.main()
