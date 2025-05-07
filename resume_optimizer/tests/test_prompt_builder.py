"""
Tests for the prompt_builder module.
"""

import unittest
from resume_optimizer.prompt_builder import build_prompt, load_prompt_template


class TestPromptBuilder(unittest.TestCase):
    """Test cases for prompt_builder module."""

    def test_load_prompt_template(self):
        """Test loading the prompt template."""
        template = load_prompt_template()
        self.assertIsInstance(template, str)
        self.assertIn("{resume_text}", template)
        self.assertIn("{job_description}", template)
        self.assertIn("JSON", template)

    def test_build_prompt(self):
        """Test building a prompt with placeholders filled."""
        resume_text = "Sample resume text"
        job_description = "Sample job description"
        
        # Get template for comparison
        template = load_prompt_template()
        
        # Build prompt
        prompt = build_prompt(resume_text, job_description)
        
        # Verify placeholders are replaced
        self.assertIn(resume_text, prompt)
        self.assertIn(job_description, prompt)
        self.assertNotIn("{resume_text}", prompt)
        self.assertNotIn("{job_description}", prompt)
        
        # Verify the prompt matches the expected format (template with placeholders replaced)
        expected_prompt = template.format(
            resume_text=resume_text, 
            job_description=job_description
        )
        self.assertEqual(prompt, expected_prompt)

    def test_build_prompt_empty_inputs(self):
        """Test that empty inputs raise ValueError."""
        with self.assertRaises(ValueError):
            build_prompt("", "job description")
            
        with self.assertRaises(ValueError):
            build_prompt("resume text", "")
            
        with self.assertRaises(ValueError):
            build_prompt("", "")


if __name__ == "__main__":
    unittest.main()
