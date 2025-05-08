#!/usr/bin/env python3
"""
Quick test script for the job scraper functionality.
"""
import os
import json
import logging
import datetime
from services.scraper import search_google_for_jobs, generate_simulated_jobs, scrape_job_board

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def test_simulation():
    """Test the simulation mode for generating fake job listings."""
    print("\n=== TESTING SIMULATION MODE ===")
    # Enable simulation mode
    os.environ["SIMULATION_MODE"] = "true"
    
    # Test with a simple query
    search_term = "Python Developer Remote"
    print(f"Simulating search for: {search_term}")
    jobs = generate_simulated_jobs(search_term)
    
    # Print the results
    print(f"Found {len(jobs)} simulated jobs:")
    for i, job in enumerate(jobs, 1):
        print(f"\n--- Job {i} ---")
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        print(f"Link: {job['link']}")
        print(f"Description: {job['description'][:100]}..." if len(job.get('description', '')) > 100 else f"Description: {job.get('description', '')}")

def test_google_search():
    """Test the Google Custom Search API for job listings (if credentials available)."""
    print("\n=== TESTING GOOGLE CUSTOM SEARCH ===")
    # Disable simulation mode
    os.environ["SIMULATION_MODE"] = "false"
    
    # Test with a simple query
    search_term = "Python Developer"
    location = "Remote"
    print(f"Searching for: {search_term} in {location}")
    
    jobs = search_google_for_jobs(search_term, location, recency_hours=24)
    
    if not jobs:
        print("No jobs found. This could be due to missing API keys or no search results.")
        return
    
    # Print the results
    print(f"Found {len(jobs)} jobs via Google CSE:")
    for i, job in enumerate(jobs, 1):
        print(f"\n--- Job {i} ---")
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        print(f"Link: {job['link']}")
        print(f"Snippet: {job['snippet'][:100]}..." if len(job.get('snippet', '')) > 100 else f"Snippet: {job.get('snippet', '')}")

def test_job_board_scraper():
    """Test the main job board scraper function."""
    print("\n=== TESTING JOB BOARD SCRAPER ===")
    # Test with a real job board URL
    url = "https://example.com/jobs?keywords=Python+Developer&location=Remote"
    print(f"Scraping from URL: {url}")
    
    # Disable simulation mode for real-time testing
    os.environ["SIMULATION_MODE"] = "false"
    
    jobs = scrape_job_board(url)
    
    if not jobs:
        print("No jobs found from job board scraper.")
        return
    
    # Print the results
    print(f"Found {len(jobs)} jobs via job board scraper:")
    for i, job in enumerate(jobs, 1):
        print(f"\n--- Job {i} ---")
        for key, value in job.items():
            if isinstance(value, str) and len(value) > 100:
                print(f"{key}: {value[:97]}...")
            else:
                print(f"{key}: {value}")
    
    # Save to a JSON file for inspection
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"data/job_search_results/test_scraper_output_{timestamp}.json"
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(jobs, f, indent=2)
    
    print(f"\nSaved results to {output_file}")

def test_multiple_job_searches():
    """Test multiple real-time job searches with different queries."""
    print("\n=== TESTING MULTIPLE JOB SEARCHES ===")
    
    # Disable simulation mode for real searches
    os.environ["SIMULATION_MODE"] = "false"
    
    # Define search terms and locations to test
    search_queries = [
        ("Data Scientist", "Remote"),
        ("Machine Learning Engineer", "USA"),
        ("Python Developer", "New York"),
        ("DevOps Engineer", "San Francisco")
    ]
    
    all_results = {}
    
    for search_term, location in search_queries:
        print(f"\nSearching for: {search_term} in {location}")
        
        jobs = search_google_for_jobs(search_term, location, recency_hours=24)
        
        if not jobs:
            print(f"No jobs found for {search_term} in {location}.")
            continue
            
        print(f"Found {len(jobs)} jobs:")
        
        # Print first 3 jobs as a sample
        for i, job in enumerate(jobs[:3], 1):
            print(f"\n--- Job {i} ---")
            print(f"Title: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['location']}")
            
        all_results[f"{search_term}_{location}"] = jobs
    
    # Save all results to a JSON file
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"data/job_search_results/real_time_searches_{timestamp}.json"
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nSaved all results to {output_file}")

def main():
    """Run the test script."""
    print("Starting job scraper tests...")
    
    # Ask user which test to run
    print("\nWhich test would you like to run?")
    print("1. Test simulation mode")
    print("2. Test Google search with a single query")
    print("3. Test job board scraper")
    print("4. Test multiple real-time job searches")
    print("5. Run all tests")
    
    try:
        choice = input("Enter your choice (1-5): ")
        
        if choice == '1':
            test_simulation()
        elif choice == '2':
            test_google_search()
        elif choice == '3':
            test_job_board_scraper()
        elif choice == '4':
            test_multiple_job_searches()
        elif choice == '5':
            test_simulation()
            test_google_search()
            test_job_board_scraper()
            test_multiple_job_searches()
        else:
            print("Invalid choice. Running all tests.")
            test_simulation()
            test_google_search()
            test_job_board_scraper()
            test_multiple_job_searches()
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        
    print("\nTests completed!")

if __name__ == "__main__":
    main()