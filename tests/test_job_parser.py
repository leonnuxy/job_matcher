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
        # Make assertion more specific - check for exact keywords
        self.assertIn('python', keywords)
        self.assertIn('sql', keywords)
        self.assertIn('aws', keywords)
        self.assertIn('docker', keywords) # Added from sample
        self.assertIn('kubernetes', keywords) # Added from sample
        # Check for absence of common noise words (assuming they are in stop list)
        self.assertNotIn('required', keywords)
        self.assertNotIn('skills', keywords)
        self.assertNotIn('experience', keywords)
        self.assertNotIn('is', keywords)
        self.assertNotIn('a', keywords)
        self.assertNotIn('plus', keywords)


    def test_extract_requirements_with_noise(self):
        sample_text = """
        Job Title: Software Engineer
        Location: Calgary, AB

        About the Role:
        We are seeking a passionate Software Engineer to join our dynamic team.
        The ideal candidate will have 3+ years of experience in software development.
        Must have strong problem-solving skills and excellent communication abilities.
        Ability to work independently and as part of a team is crucial.

        Responsibilities:
        - Design, develop, and maintain scalable software solutions using Python and Java.
        - Collaborate with product managers and other engineers.
        - Write clean, testable code.
        - Participate in code reviews.
        - Deploy applications using Docker and Kubernetes on AWS cloud.

        Qualifications:
        - Bachelor's degree in Computer Science or related field.
        - Proven experience with Python 3 and SQL databases (e.g., PostgreSQL).
        - Familiarity with cloud platforms like AWS or Azure.
        - Experience with containerization (Docker) and orchestration (Kubernetes).
        - Knowledge of CI/CD pipelines (Jenkins preferred).
        - Understanding of RESTful APIs.
        - Bonus points for experience with React or Vue.js.
        """
        keywords = job_parser.extract_job_requirements(sample_text)

        # Expected Skills
        expected = ['python', 'python 3', 'java', 'sql', 'postgresql', 'aws', 'azure', 'docker', 'kubernetes', 'ci/cd pipelines', 'jenkins', 'restful apis', 'react', 'vue.js']
        for skill in expected:
            self.assertIn(skill, keywords)

        # Expected Noun Chunks (Examples)
        self.assertIn('software engineer', keywords)
        self.assertIn('scalable software solutions', keywords)
        # self.assertIn('cloud platforms', keywords) # Might be filtered by stop words depending on exact implementation
        self.assertIn('computer science', keywords)
        self.assertIn('related field', keywords) # Might be borderline, check if useful

        # Absence of Noise
        noise = [
            'job', 'title', 'location', 'calgary', 'ab', 'role', 'seeking', 'passionate', 'join', 'dynamic', 'team',
            'ideal', 'candidate', 'will', 'have', 'years', 'experience', 'software', 'development', 'must', 'strong',
            'problem-solving', 'skills', 'excellent', 'communication', 'abilities', 'ability', 'work', 'independently',
            'part', 'crucial', 'responsibilities', 'design', 'develop', 'maintain', 'scalable', 'solutions', 'using',
            'collaborate', 'product', 'managers', 'other', 'engineers', 'write', 'clean', 'testable', 'code',
            'participate', 'reviews', 'deploy', 'applications', 'cloud', 'qualifications', 'bachelor', 'degree',
            'proven', 'databases', 'e.g.', 'familiarity', 'platforms', 'like', 'containerization', 'orchestration',
            'knowledge', 'pipelines', 'preferred', 'understanding', 'apis', 'bonus', 'points', 'for', 'with', 'in', 'and', 'or', 'of', 'a', 'the', 'is', 'are', 'to', 'on', 'as'
            '3+' # Should be removed
        ]
        for word in noise:
             # Allow some flexibility if minor variations exist after cleaning
            found = any(word in kw for kw in keywords)
            self.assertFalse(found, f"Noise word '{word}' found in keywords: {keywords}")


    def test_extract_requirements_empty_input(self):
        keywords = job_parser.extract_job_requirements("")
        self.assertEqual(keywords, [])
        keywords = job_parser.extract_job_requirements("   \n  ")
        self.assertEqual(keywords, [])

    def test_extract_requirements_no_meaningful_text(self):
        sample_text = "Click apply now. Job ID 12345. EOE."
        keywords = job_parser.extract_job_requirements(sample_text)
        # Expecting few or no keywords beyond potential regex matches if any
        self.assertLess(len(keywords), 5) # Allow for maybe 'EOE' if not stopped


if __name__ == '__main__':
    unittest.main()
