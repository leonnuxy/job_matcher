import unittest
from lib import job_parser

class TestScrapedJobExtraction(unittest.TestCase):
    def test_html_scraped_job(self):
        with open('tests/test_scraped_job.txt', 'r', encoding='utf-8') as f:
            html = f.read()
        desc = job_parser.extract_job_description(html)
        print("Extracted Description:\n", desc)
        self.assertIn("Senior Backend Engineer", desc)
        self.assertIn("scalable APIs", desc)
        keywords = job_parser.extract_job_requirements(desc)
        print("Extracted Keywords:", keywords)
        joined = ' '.join(keywords).lower()
        self.assertIn('python', joined)
        self.assertIn('aws', joined)
        self.assertIn('docker', joined)
        self.assertIn('rest', joined)

if __name__ == '__main__':
    unittest.main()
