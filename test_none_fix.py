#!/usr/bin/env python3
"""
Test script to verify None handling in main.py
"""

import re

def test_none_handling():
    """Test how the main.py logic handles None values"""
    
    # Simulate the problematic case
    test_cases = [
        {'title': None, 'company': None},
        {'title': '', 'company': ''},
        {'title': 'Software Engineer', 'company': None},
        {'title': None, 'company': 'Tech Corp'},
        {'title': 'Product Manager', 'company': 'Amazing Company'},
    ]
    
    print("Testing None handling for job titles and company names:")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test case {i}: {test_case}")
        
        # Simulate the early job_title extraction
        job_title_early = test_case.get('title') or ''
        print(f"  Early job_title: '{job_title_early}'")
        
        # Simulate the later extraction for optimization
        job_title_later = test_case.get('title') or 'Unknown Job Title'
        company_name = test_case.get('company') or 'Unknown Company'
        print(f"  Later job_title: '{job_title_later}'")
        print(f"  Company name: '{company_name}'")
        
        # Test the sanitization logic
        title_safe = job_title_later if job_title_later is not None else "Unknown_Job"
        sanitized_job_title = re.sub(r'[^\w\s-]', '', title_safe).strip().replace(' ', '_')[:50]
        
        company_safe = company_name if company_name is not None else "Unknown_Company"
        sanitized_company = re.sub(r'[^\w\s-]', '', company_safe).strip().replace(' ', '_')[:30]
        
        print(f"  Sanitized title: '{sanitized_job_title}'")
        print(f"  Sanitized company: '{sanitized_company}'")
        print()

if __name__ == "__main__":
    test_none_handling()
