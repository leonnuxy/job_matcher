"""
Tests for the optimizer module.
"""

import unittest
import json
from unittest.mock import patch, MagicMock

from resume_optimizer.optimizer import (
    optimize_resume,
    _validate_inputs,
    _parse_llm_response,
    InputValidationError,
    SchemaValidationError,
    OptimizerError
)
from resume_optimizer.llm_client import LLMClientError


class TestOptimizer(unittest.TestCase):
    """Test cases for optimizer module."""

    def test_validate_inputs_success(self):
        """Test successful input validation."""
        # This should not raise exceptions
        _validate_inputs(
            "This is a reasonably sized resume text with enough content for analysis.",
            "This job description has requirements."
        )

    def test_validate_inputs_failures(self):
        """Test input validation failures."""
        # Empty resume
        with self.assertRaises(InputValidationError):
            _validate_inputs("", "Job description")
        
        # Empty job description
        with self.assertRaises(InputValidationError):
            _validate_inputs("Resume text", "")
        
        # Too short resume
        with self.assertRaises(InputValidationError):
            _validate_inputs("Too short", "Job description")
        
        # Too short job description
        with self.assertRaises(InputValidationError):
            _validate_inputs("This is a reasonably sized resume text", "Too short")

    def test_parse_llm_response_success(self):
        """Test successful LLM response parsing."""
        # Valid JSON response
        valid_json = {
            "summary": "Good match",
            "skills_to_add": ["skill1", "skill2"],
            "skills_to_remove": ["irrelevant1"],
            "experience_tweaks": [
                {"original": "Before", "optimized": "After"}
            ],
            "formatting_suggestions": ["suggestion"],
            "collaboration_points": ["point"]
        }
        
        # Convert to string for parsing
        valid_response = json.dumps(valid_json)
        
        # Parse the response
        result = _parse_llm_response(valid_response)
        
        # Verify the parsed result matches the expected structure
        self.assertEqual(result["summary"], "Good match")
        self.assertEqual(len(result["skills_to_add"]), 2)
        self.assertEqual(len(result["skills_to_remove"]), 1)
        self.assertEqual(len(result["experience_tweaks"]), 1)
        self.assertEqual(result["experience_tweaks"][0]["original"], "Before")
        self.assertEqual(result["experience_tweaks"][0]["optimized"], "After")

    def test_parse_llm_response_with_text_wrapper(self):
        """Test parsing LLM response with text before/after JSON."""
        valid_json = {
            "summary": "Good match",
            "skills_to_add": ["skill1", "skill2"],
            "skills_to_remove": ["irrelevant1"],
            "experience_tweaks": [
                {"original": "Before", "optimized": "After"}
            ],
            "formatting_suggestions": ["suggestion"],
            "collaboration_points": ["point"]
        }
        
        # Add text before and after the JSON
        wrapped_response = f"""
        Here's my analysis:
        
        {json.dumps(valid_json)}
        
        Hope this helps!
        """
        
        # Parse the response
        result = _parse_llm_response(wrapped_response)
        
        # Verify extraction worked
        self.assertEqual(result["summary"], "Good match")

    def test_parse_llm_response_invalid_json(self):
        """Test handling of invalid JSON in LLM response."""
        # Invalid JSON (missing closing brace)
        invalid_response = '{"summary": "Incomplete JSON"'
        
        # Attempt to parse should raise exception
        with self.assertRaises(SchemaValidationError):
            _parse_llm_response(invalid_response)

    def test_parse_llm_response_schema_violation(self):
        """Test handling of JSON that violates the schema."""
        # Missing required fields
        invalid_json = {
            "summary": "Incomplete data",
            # Missing other required fields
        }
        
        # Convert to string for parsing
        invalid_response = json.dumps(invalid_json)
        
        # Attempt to parse should raise exception
        with self.assertRaises(SchemaValidationError):
            _parse_llm_response(invalid_response)

    @patch('resume_optimizer.optimizer.call_model')
    @patch('resume_optimizer.optimizer.get_default_cache')
    def test_optimize_resume_cache_hit(self, mock_cache, mock_call_model):
        """Test optimize_resume with cache hit."""
        # Create mock cache that returns a cache hit
        mock_cache_instance = MagicMock()
        mock_cache.return_value = mock_cache_instance
        
        # Set up cache hit
        cached_result = {
            "summary": "Cached result",
            "skills_to_add": ["skill1"],
            "skills_to_remove": [],
            "experience_tweaks": [],
            "formatting_suggestions": [],
            "collaboration_points": []
        }
        mock_cache_instance.get.return_value = cached_result
        
        # Call optimize_resume
        result = optimize_resume(
            "Example resume with sufficient length for analysis",
            "Example job description with sufficient length"
        )
        
        # Verify cache was checked
        mock_cache_instance.get.assert_called_once()
        
        # Verify result matches cache (and LLM wasn't called)
        self.assertEqual(result, cached_result)
        mock_call_model.assert_not_called()

    @patch('resume_optimizer.optimizer._parse_llm_response')
    @patch('resume_optimizer.optimizer.build_prompt')
    @patch('resume_optimizer.optimizer.call_model')
    @patch('resume_optimizer.optimizer.get_default_cache')
    def test_optimize_resume_cache_miss(self, mock_cache, mock_call_model, 
                                       mock_build_prompt, mock_parse_response):
        """Test optimize_resume with cache miss, requiring LLM call."""
        # Create mock cache that returns a cache miss
        mock_cache_instance = MagicMock()
        mock_cache.return_value = mock_cache_instance
        mock_cache_instance.get.return_value = None
        
        # Set up other mocks
        mock_build_prompt.return_value = "Test prompt"
        mock_call_model.return_value = "LLM response"
        
        expected_result = {
            "summary": "LLM result",
            "skills_to_add": ["skill1"],
            "skills_to_remove": [],
            "experience_tweaks": [],
            "formatting_suggestions": [],
            "collaboration_points": []
        }
        mock_parse_response.return_value = expected_result
        
        # Call optimize_resume
        result = optimize_resume(
            "Example resume with sufficient length for analysis",
            "Example job description with sufficient length"
        )
        
        # Verify expected calls
        mock_cache_instance.get.assert_called_once()
        mock_build_prompt.assert_called_once()
        mock_call_model.assert_called_once_with("Test prompt")
        mock_parse_response.assert_called_once_with("LLM response")
        
        # Verify result matches expected
        self.assertEqual(result, expected_result)
        
        # Verify result was cached
        mock_cache_instance.set.assert_called_once()

    @patch('resume_optimizer.optimizer.call_model')
    @patch('resume_optimizer.optimizer.get_default_cache')
    def test_optimize_resume_llm_error(self, mock_cache, mock_call_model):
        """Test optimize_resume handling LLM errors."""
        # Create mock cache that returns a cache miss
        mock_cache_instance = MagicMock()
        mock_cache.return_value = mock_cache_instance
        mock_cache_instance.get.return_value = None
        
        # Set up LLM to raise error
        mock_call_model.side_effect = LLMClientError("Test LLM error")
        
        # Call optimize_resume and expect exception to propagate
        with self.assertRaises(LLMClientError):
            optimize_resume(
                "Example resume with sufficient length for analysis",
                "Example job description with sufficient length"
            )


if __name__ == "__main__":
    unittest.main()
