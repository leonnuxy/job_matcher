#!/usr/bin/env python3
"""
Analyze job search results with enhanced analysis capabilities.
"""
import json
import sys
import os
import re
from collections import Counter, defaultdict
from typing import Dict, List, Any

def analyze_jobs_file(filename):
    """Analyze the jobs in the given JSON file with enhanced analytics."""
    try:
        with open(filename, 'r') as f:
            jobs = json.load(f)
    except Exception as e:
        print(f"Error loading file {filename}: {e}")
        return
    
    print(f"Total jobs found: {len(jobs)}")
    
    # Analyze locations
    locations = Counter([job.get('location', 'Unknown') for job in jobs])
    print("\nJobs by location:")
    for loc, count in locations.most_common():
        print(f"  {loc}: {count}")
    
    # Analyze companies
    companies = Counter([job.get('company', 'Unknown') for job in jobs])
    print("\nTop 10 companies:")
    for company, count in companies.most_common(10):
        print(f"  {company}: {count}")
    
    # Get the count of unknown companies
    unknown_companies = companies.get('Unknown', 0)
    if unknown_companies > 0:
        print(f"\n⚠️  {unknown_companies} jobs ({unknown_companies / len(jobs) * 100:.1f}%) have unknown company names")
    
    # Analyze job titles
    job_titles = Counter()
    job_title_words = Counter()
    seniority_levels = Counter()
    
    # Track common job keywords
    job_categories = {
        'python': [],
        'data': [],
        'machine_learning': [],
        'full_stack': [],
        'frontend': [],
        'backend': [],
        'cloud': [],
        'devops': []
    }
    
    # Patterns for extracting seniority levels
    seniority_pattern = r'(Senior|Junior|Lead|Staff|Principal|Mid-Level|Mid)'
    
    for job in jobs:
        title = job.get('title', '').lower()
        
        # Extract words from title for frequency analysis
        words = re.findall(r'\b[a-zA-Z]+\b', title)
        for word in words:
            job_title_words[word] += 1
        
        # Check for seniority level
        match = re.search(seniority_pattern, job.get('title', ''), re.IGNORECASE)
        if match:
            seniority = match.group(1).title()
            seniority_levels[seniority] += 1
        
        # Categorize by job type
        if 'python' in title:
            job_categories['python'].append(job)
        if any(term in title for term in ['data', 'scientist', 'analyst']):
            job_categories['data'].append(job)
        if any(term in title for term in ['machine learning', 'ml', 'ai']):
            job_categories['machine_learning'].append(job)
        if any(term in title for term in ['full stack', 'fullstack', 'full-stack']):
            job_categories['full_stack'].append(job)
        if any(term in title for term in ['frontend', 'front end', 'front-end']):
            job_categories['frontend'].append(job)
        if any(term in title for term in ['backend', 'back end', 'back-end']):
            job_categories['backend'].append(job)
        if any(term in title for term in ['cloud', 'aws', 'azure', 'gcp']):
            job_categories['cloud'].append(job)
        if any(term in title for term in ['devops', 'sre', 'reliability']):
            job_categories['devops'].append(job)
    
    # Print job categories
    print("\nJobs by category:")
    for category, jobs_list in job_categories.items():
        print(f"  {category.replace('_', ' ').title()}: {len(jobs_list)}")
    
    # Print seniority levels
    if seniority_levels:
        print("\nJobs by seniority level:")
        for level, count in seniority_levels.most_common():
            print(f"  {level}: {count}")
    
    # Top job title keywords (excluding common words)
    common_words = {'jobs', 'job', 'employment', 'hiring', 'for', 'and', 'the', 'in', 'at', 'with'}
    print("\nTop job title keywords:")
    for word, count in job_title_words.most_common(15):
        if word not in common_words and len(word) > 2:
            print(f"  {word}: {count}")
    
    # Sample jobs for various categories
    for category_name, category_jobs in job_categories.items():
        if category_jobs:
            pretty_name = category_name.replace('_', ' ').title()
            print(f"\nSample {pretty_name} job:")
            job = category_jobs[0]
            print(f"  Title: {job.get('title', 'N/A')}")
            print(f"  Company: {job.get('company', 'N/A')}")
            print(f"  Location: {job.get('location', 'N/A')}")
            print(f"  Link: {job.get('link', 'N/A')}")
            snippet = job.get('snippet', '')
            if len(snippet) > 100:
                snippet = snippet[:97] + '...'
            print(f"  Snippet: {snippet}")
    
    # Check for issues in the data
    issues = []
    issues_by_type = defaultdict(list)
    
    for i, job in enumerate(jobs):
        if not job.get('title'):
            issues.append(f"Job {i+1} is missing a title")
            issues_by_type['missing_title'].append(i+1)
        if not job.get('location'):
            issues.append(f"Job {i+1} is missing a location") 
            issues_by_type['missing_location'].append(i+1)
        if not job.get('link'):
            issues.append(f"Job {i+1} is missing a link")
            issues_by_type['missing_link'].append(i+1)
        if job.get('company') == 'Unknown':
            issues.append(f"Job {i+1} has unknown company")
            issues_by_type['unknown_company'].append(i+1)
        if any(time_marker in job.get('title', '').lower() for time_marker in ['hours ago', 'days ago', '2025', 'may']):
            issues.append(f"Job {i+1} title contains time markers")
            issues_by_type['time_in_title'].append(i+1)
    
    if issues:
        print("\nData quality issues:")
        for issue_type, job_ids in issues_by_type.items():
            print(f"  {issue_type.replace('_', ' ').title()}: {len(job_ids)} issues")
            
        print("\nSample issues (first 10):")
        for issue in issues[:10]:
            print(f"  {issue}")
        if len(issues) > 10:
            print(f"  ... and {len(issues) - 10} more issues")
    else:
        print("\nNo data quality issues found!")
    
    # Provide summary and recommendations
    print("\nSummary and Recommendations:")
    if unknown_companies / len(jobs) > 0.3:
        print("  ⚠️  High percentage of unknown companies - consider improving company name extraction")
    
    # Calculate percentage of jobs with time markers in title
    if len(issues_by_type.get('time_in_title', [])) / len(jobs) > 0.1:
        print("  ⚠️  Multiple job titles contain date/time information - improve title cleaning")
    
    # Recommendations based on job categories
    strongest_categories = sorted(
        [(cat, len(jobs_list)) for cat, jobs_list in job_categories.items()],
        key=lambda x: x[1], 
        reverse=True
    )[:3]
    
    if strongest_categories:
        print("  ✅ Most common job categories in results:")
        for cat, count in strongest_categories:
            if count > 0:
                print(f"      - {cat.replace('_', ' ').title()}: {count} jobs")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        # Use most recent file in the job_search_results directory
        directory = "data/job_search_results"
        files = [os.path.join(directory, f) for f in os.listdir(directory) if f.startswith('job_search_') and f.endswith('.json')]
        if not files:
            print("No job search result files found.")
            sys.exit(1)
        filename = max(files, key=os.path.getmtime)
        print(f"Using most recent file: {filename}")
    
    analyze_jobs_file(filename)
