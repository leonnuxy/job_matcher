import unittest
from lib import job_parser
import logging
# Set level to only show errors in tests
logging.basicConfig(level=logging.ERROR)

class TestExtractJobDescription(unittest.TestCase):

    def test_plain_text_extraction(self):
        job_text = """
        Company: Example Corp
        Location: Remote

        Role Overview:
        As a Python Developer, you will build scalable APIs and work with cloud infrastructure.

        Responsibilities:
        - Develop REST APIs
        - Collaborate with DevOps

        Requirements:
        - Python 3.8+
        - AWS
        - Docker
        """
        desc = job_parser.extract_job_description(job_text)
        self.assertIn("As a Python Developer", desc)
        self.assertIn("build scalable APIs", desc)
        self.assertGreater(len(desc.split()), 5) #Increased strictness

    def test_html_extraction(self):
        job_html = """
        <html><body><h2>Job Description</h2><p>Join our team as a Data Engineer. You will design ETL pipelines and work with big data tools.</p><h3>Requirements</h3><ul><li>Python</li><li>SQL</li></ul></body></html>
        """
        desc = job_parser.extract_job_description(job_html)
        self.assertIn("Join our team as a Data Engineer", desc)
        self.assertIn("design ETL pipelines", desc)
        self.assertGreater(len(desc.split()), 5) #Increased strictness

    def test_fallback_to_sentences(self):
        job_text = "Short posting."
        desc = job_parser.extract_job_description(job_text)
        self.assertIn("Short posting.", desc)
        self.assertEqual("Short posting.", desc)  # Ensure full sentence is returned

    def test_empty_input(self):
        desc = job_parser.extract_job_description("")
        self.assertEqual(desc, "")

        desc = job_parser.extract_job_description(None)
        self.assertEqual(desc, "")

    def test_html_extraction_with_tags(self):
        job_html = """
        <html><body><p><b>Job Title:</b> Software Engineer</p><p>Description: Develop and maintain web applications.</p></body></html>
        """
        desc = job_parser.extract_job_description(job_html)
        self.assertIn("Software Engineer", desc)
        self.assertIn("Develop and maintain web applications", desc)

    def test_html_extraction_with_comments(self):
        job_html = """
        <html><body><!-- This is a comment --><p>Description: Develop and maintain web applications.</p></body></html>
        """
        desc = job_parser.extract_job_description(job_html)
        self.assertIn("Develop and maintain web applications", desc)

    def test_realistic_job_posting(self):
         job_html = """
        <html>
        <body>
            <h1>Software Engineer</h1>
            <div class="job-description">
                <h2>About the Role</h2>
                <p>We are looking for a talented Software Engineer to join our team...</p>
                <h3>Responsibilities</h3>
                <ul>
                    <li>Develop high-quality software</li>
                    <li>Participate in code reviews</li>
                </ul>
                <h3>Qualifications</h3>
                <ul>
                    <li>Bachelor's degree in Computer Science</li>
                    <li>3+ years of experience</li>
                </ul>
            </div>
        </body>
        </html>
        """

         desc = job_parser.extract_job_description(job_html)
         self.assertIn("We are looking for a talented Software Engineer", desc)
         self.assertIn("Develop high-quality software", desc)
         self.assertIn("Participate in code reviews", desc)
         self.assertIn("Bachelor's degree in Computer Science", desc)
         self.assertIn("3+ years of experience", desc)

if __name__ == '__main__':
    unittest.main()