import os
import unittest
from unittest.mock import patch, MagicMock
from lib import api_calls

class TestAPICallsFunctions(unittest.TestCase):
    @patch('lib.api_calls.build')
    def test_search_jobs_valid(self, mock_build):
        """Test successful job search with valid parameters"""
        # Setup mock
        mock_cse = MagicMock()
        mock_build.return_value = mock_cse
        mock_cse.cse.return_value.list.return_value.execute.return_value = {
            'items': [
                {'title': 'Software Engineer', 'link': 'http://example.com/job1', 
                 'snippet': 'Python developer needed with 2 years experience'},
                {'title': 'Data Scientist', 'link': 'http://example.com/job2', 
                 'snippet': 'Machine learning expertise required'}
            ]
        }
        
        # Call the function
        results = api_calls.search_jobs('python developer')
        
        # Assertions
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'Software Engineer')
        self.assertEqual(results[1]['link'], 'http://example.com/job2')

    @patch('lib.api_calls.build')
    def test_search_jobs_invalid_api_key(self, mock_build):
        """Test handling of invalid API key"""
        from googleapiclient.errors import HttpError
        
        # Simulate an HttpError for invalid credentials
        mock_build.side_effect = HttpError(resp=MagicMock(status=403), content=b'Invalid API key')
        
        # Call the function and check exception handling
        results = api_calls.search_jobs('python developer')
        self.assertEqual(results, [])

    @patch('lib.api_calls.build')
    def test_search_jobs_fields_extraction(self, mock_build):
        """Test extraction of all expected fields from search results"""
        # Setup mock with full field set
        mock_cse = MagicMock()
        mock_build.return_value = mock_cse
        mock_cse.cse.return_value.list.return_value.execute.return_value = {
            'items': [{
                'title': 'Software Engineer', 
                'link': 'http://example.com/job1',
                'snippet': 'Python developer needed with 2 years experience',
                'pagemap': {
                    'metatags': [{
                        'og:description': 'Full job description here',
                        'og:site_name': 'Example Company'
                    }]
                }
            }]
        }
        
        # Call the function
        results = api_calls.search_jobs('python developer')
        
        # Assertions for field extraction
        self.assertEqual(len(results), 1)
        self.assertIn('title', results[0])
        self.assertIn('link', results[0])
        self.assertIn('snippet', results[0])
        self.assertIn('company', results[0])
        
    # Note: The test_optimize_resume_with_gemini test has been removed
    # as the function has been deprecated and removed.
    # See tests/test_resume_optimizer_package.py for the replacement tests.

class TestResumeTextLoading(unittest.TestCase):
    def setUp(self):
        # Create a temporary test file
        self.test_file = 'test_resume.txt'
        with open(self.test_file, 'w') as f:
            f.write('Test resume content')
        
        # Create empty file
        self.empty_file = 'empty_resume.txt'
        open(self.empty_file, 'w').close()
    
    def tearDown(self):
        # Clean up test files
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        if os.path.exists(self.empty_file):
            os.remove(self.empty_file)
    
    def test_extract_resume_text_valid(self):
        """Test loading valid resume text"""
        from lib import resume_parser
        text = resume_parser.extract_resume_text(self.test_file)
        self.assertEqual(text, 'Test resume content')
    
    def test_extract_resume_text_file_not_found(self):
        """Test handling of non-existent file"""
        from lib import resume_parser
        text = resume_parser.extract_resume_text('nonexistent_file.txt')
        self.assertEqual(text, '')
    
    def test_extract_resume_text_empty_file(self):
        """Test handling of empty file"""
        from lib import resume_parser
        text = resume_parser.extract_resume_text(self.empty_file)
        self.assertEqual(text, '')

if __name__ == '__main__':
    unittest.main()
