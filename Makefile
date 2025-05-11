# Makefile for Job Matcher Project

.PHONY: clean cleanup test run

# Run the cleanup script to remove legacy, cache, and archive old files
tidy:
	./cleanup.sh

# Alias for tidy
tidyup: tidy

# Run all tests

test:
	python -m unittest discover tests

# Run the main job search pipeline
run:
	python run_job_search.py
