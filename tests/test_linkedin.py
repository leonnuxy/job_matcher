#!/usr/bin/env python
"""
Unit tests for the LinkedIn service module.
"""

import os
import pytest
import sys
import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules to be tested
from services.linkedin import (
    extract_job_id_from_url,
    fetch_job_via_api,
    check_job_status,
    extract_job_title,
    extract_company_name,
    extract_location,
    extract_job_description,
    extract_jobs_from_search_url
)


class TestLinkedInService(unittest.TestCase):
    """Test cases for LinkedIn service module functions."""

    def test_extract_job_id_from_url(self):
        """Test extracting job IDs from various LinkedIn URL formats."""
        test_urls = {
            # Standard job view URL
            "https://www.linkedin.com/jobs/view/3535624900": "3535624900",
            # Job view URL with title and company
            "https://www.linkedin.com/jobs/view/senior-developer-at-acme-corp-3535624900": "3535624900",
            # URL with currentJobId parameter
            "https://www.linkedin.com/jobs/view/senior-developer?currentJobId=3535624900": "3535624900",
            # External redirect URL
            "https://www.linkedin.com/jobs/view/external/3535624900": "3535624900",
            # URL with trackingId
            "https://www.linkedin.com/jobs/view/3535624900?trackingId=abcdef": "3535624900",
            # Invalid URL
            "https://www.linkedin.com/company/acme-corp": None,
            # Empty URL
            "": None
        }
        
        for url, expected_id in test_urls.items():
            self.assertEqual(extract_job_id_from_url(url), expected_id)

    @patch('services.linkedin.get_session')
    def test_fetch_job_via_api_success(self, mock_get_session):
        """Test fetching job details with successful API response."""
        # Create a mock response with sample HTML
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        with open('tests/data/linkedin_job_sample.html', 'r', encoding='utf-8') as f:
            mock_response.text = f.read()
        
        # Set up the mock session
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session
        
        # Call the function with a test URL
        result = fetch_job_via_api("https://www.linkedin.com/jobs/view/3535624900")
        
        # Verify the result contains expected fields
        self.assertIn("title", result)
        self.assertIn("company", result)
        self.assertIn("description", result)
        self.assertIn("location", result)
        self.assertEqual(result["id"], "3535624900")

    @patch('services.linkedin.get_session')
    def test_fetch_job_via_api_failure(self, mock_get_session):
        """Test fetching job details with API failure."""
        # Create a mock response that's too small (error case)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Job not found"  # Small response
        
        # Set up the mock session
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session
        
        # Call the function with a test URL
        result = fetch_job_via_api("https://www.linkedin.com/jobs/view/3535624900")
        
        # Verify the result is empty for failed request
        self.assertEqual(result, {})

    def test_check_job_status_active(self):
        """Test checking job status for an active job posting."""
        # Create BeautifulSoup object for active job
        html = """<div class="job-details">
                    <h1>Software Engineer</h1>
                    <div class="apply-button">Apply now</div>
                  </div>"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Should return True for active job
        self.assertTrue(check_job_status(soup))

    def test_check_job_status_inactive(self):
        """Test checking job status for an inactive job posting."""
        # Create BeautifulSoup object for inactive job
        html = """<div class="job-details">
                    <h1>Software Engineer</h1>
                    <div class="apply-button">This job is no longer accepting applications</div>
                  </div>"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Should return False for inactive job
        self.assertFalse(check_job_status(soup))

    def test_extract_job_title(self):
        """Test extracting job title from HTML."""
        # Create BeautifulSoup object with job title in expected format
        html = """<div class="job-details">
                    <h1 class="top-card-layout__title">Senior Python Developer</h1>
                  </div>"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Should extract the correct title
        self.assertEqual(extract_job_title(soup), "Senior Python Developer")

    def test_extract_company_name(self):
        """Test extracting company name from HTML."""
        # Create BeautifulSoup object with company in expected format
        html = """<div class="job-details">
                    <h1>Software Engineer</h1>
                    <span class="jobs-unified-top-card__company-name">Acme Corporation</span>
                  </div>"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Should extract the correct company
        self.assertEqual(extract_company_name(soup), "Acme Corporation")

    @patch('services.linkedin.get_session')
    def test_extract_jobs_from_search_url(self, mock_get_session):
        """Test extracting job listings from search URL."""
        # Create a mock response with sample search results HTML
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        with open('tests/data/linkedin_search_sample.html', 'r', encoding='utf-8') as f:
            mock_response.text = f.read()
        
        # Set up the mock session
        mock_session = MagicMock()
        mock_session.get.return_value = mock_response
        mock_get_session.return_value = mock_session
        
        # Call the function with a test search URL
        results = extract_jobs_from_search_url("https://www.linkedin.com/jobs/search/?keywords=python&location=Canada")
        
        # There should be job listings in the results
        self.assertTrue(len(results) > 0)
        
        # Each job should have the required fields
        for job in results:
            self.assertIn("id", job)
            self.assertIn("title", job)
            self.assertIn("company", job)
            self.assertIn("location", job)
            self.assertIn("url", job)


if __name__ == '__main__':
    # Create test data directory if it doesn't exist
    os.makedirs('tests/data', exist_ok=True)
    
    # Run the tests
    unittest.main()
