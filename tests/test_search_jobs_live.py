import unittest
from lib import api_calls

class TestSearchJobsLive(unittest.TestCase):
    def test_search_jobs_live(self):
        api_key = "YOUR_API_KEY"
        cse_id = "a078e663aec764a4b"
        query = "Python developer Calgary"
        results = api_calls.search_jobs(query, api_key, cse_id)
        print("Results:", results)
        self.assertIsInstance(results, list)
        if results:
            for item in results:
                self.assertIn('title', item)
                self.assertIn('link', item)
                self.assertIn('snippet', item)

if __name__ == '__main__':
    unittest.main()
