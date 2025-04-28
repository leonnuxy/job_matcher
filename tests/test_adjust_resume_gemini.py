import unittest
from unittest.mock import patch
from lib import matcher

class TestAdjustResumeGeminiAI(unittest.TestCase):
    @patch('lib.api_calls.optimize_resume_with_gemini')
    def test_adjust_resume_with_gemini_ai(self, mock_gemini):
        mock_gemini.return_value = "[Gemini AI] Optimized resume text."
        resume_text = "John Doe\nPython Developer with experience in AWS and Docker."
        job_keywords = ['Python', 'AWS', 'Docker', 'Kubernetes', 'SQL']
        api_key = "fake-key"
        result = matcher.adjust_resume(resume_text, job_keywords, ai_api_key=api_key)
        self.assertIn("[Gemini AI] Optimized resume text.", result)
        mock_gemini.assert_called_once()

if __name__ == '__main__':
    unittest.main()
