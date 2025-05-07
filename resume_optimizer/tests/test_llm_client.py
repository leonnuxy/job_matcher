"""
Tests for the LLM client module.
"""

import unittest
from unittest.mock import patch, MagicMock
from google.api_core import exceptions

from resume_optimizer.llm_client import (
    call_model, 
    LLMTimeoutError,
    LLMServerError, 
    LLMClientRequestError,
    LLMResponseError
)


class TestLLMClient(unittest.TestCase):
    """Test cases for llm_client module."""

    @patch('resume_optimizer.llm_client.genai')
    @patch('resume_optimizer.llm_client.get_api_key')
    def test_successful_call(self, mock_get_api_key, mock_genai):
        """Test successful LLM call."""
        # Mock API key
        mock_get_api_key.return_value = "fake-api-key"
        
        # Mock generative model and response
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_response = MagicMock()
        mock_response.text = "Sample model response"
        mock_model.generate_content.return_value = mock_response
        
        # Call function
        result = call_model("Test prompt")
        
        # Verify results
        self.assertEqual(result, "Sample model response")
        mock_genai.configure.assert_called_once_with(api_key="fake-api-key")
        mock_genai.GenerativeModel.assert_called_once()
        mock_model.generate_content.assert_called_once_with(
            "Test prompt", 
            timeout=unittest.mock.ANY
        )

    @patch('resume_optimizer.llm_client.genai')
    @patch('resume_optimizer.llm_client.get_api_key')
    def test_timeout_error(self, mock_get_api_key, mock_genai):
        """Test handling of timeout errors."""
        # Mock API key
        mock_get_api_key.return_value = "fake-api-key"
        
        # Mock generative model that raises timeout error
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.side_effect = exceptions.DeadlineExceeded("Request timed out")
        
        # Call function and expect exception
        with self.assertRaises(LLMTimeoutError):
            call_model("Test prompt")

    @patch('resume_optimizer.llm_client.genai')
    @patch('resume_optimizer.llm_client.get_api_key')
    def test_client_error(self, mock_get_api_key, mock_genai):
        """Test handling of client (4xx) errors."""
        # Mock API key
        mock_get_api_key.return_value = "fake-api-key"
        
        # Mock generative model that raises client error
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Create a GoogleAPICallError with code 400
        error = exceptions.GoogleAPICallError("Bad request")
        error.code = 400
        mock_model.generate_content.side_effect = error
        
        # Call function and expect exception
        with self.assertRaises(LLMClientRequestError):
            call_model("Test prompt")

    @patch('resume_optimizer.llm_client.genai')
    @patch('resume_optimizer.llm_client.get_api_key')
    def test_server_error(self, mock_get_api_key, mock_genai):
        """Test handling of server (5xx) errors."""
        # Mock API key
        mock_get_api_key.return_value = "fake-api-key"
        
        # Mock generative model that raises server error
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        # Create a GoogleAPICallError with code 500
        error = exceptions.GoogleAPICallError("Server error")
        error.code = 500
        mock_model.generate_content.side_effect = error
        
        # Call function and expect exception
        with self.assertRaises(LLMServerError):
            call_model("Test prompt")

    @patch('resume_optimizer.llm_client.genai')
    @patch('resume_optimizer.llm_client.get_api_key')
    def test_malformed_response(self, mock_get_api_key, mock_genai):
        """Test handling of malformed responses."""
        # Mock API key
        mock_get_api_key.return_value = "fake-api-key"
        
        # Mock generative model with malformed response
        mock_model = MagicMock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_response = MagicMock()
        # Missing the text attribute
        delattr(mock_response.__class__, 'text')
        mock_model.generate_content.return_value = mock_response
        
        # Call function and expect exception
        with self.assertRaises(LLMResponseError):
            call_model("Test prompt")

    @patch('resume_optimizer.llm_client.get_api_key')
    def test_missing_api_key(self, mock_get_api_key):
        """Test handling of missing API key."""
        # Mock missing API key
        mock_get_api_key.return_value = None
        
        # Call function and expect exception
        with self.assertRaises(ValueError):
            call_model("Test prompt")


if __name__ == "__main__":
    unittest.main()
