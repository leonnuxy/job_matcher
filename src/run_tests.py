#!/usr/bin/env python
"""
Test runner script for job_matcher tests.
"""
import os
import sys
import subprocess
import argparse

def run_tests(test_path=None, verbose=False):
    """
    Run pytest with specified options.
    
    Args:
        test_path: Path to specific test file or directory
        verbose: Whether to run tests in verbose mode
    """
    # Base command
    cmd = ["pytest"]
    
    # Add verbose flag if requested
    if verbose:
        cmd.append("-v")
    
    # Add test path if specified
    if test_path:
        cmd.append(test_path)
    
    # Set up environment for testing
    env = os.environ.copy()
    env["TESTING"] = "true"
    env["SIMULATION_MODE"] = "1"
    
    # Run the tests
    result = subprocess.run(cmd, env=env)
    return result.returncode

def main():
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Run tests for job_matcher")
    parser.add_argument("test_path", nargs="?", default=None, 
                        help="Path to specific test file or directory")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Run tests in verbose mode")
    parser.add_argument("--linkedin", action="store_true",
                        help="Run only LinkedIn-related tests")
    
    args = parser.parse_args()
    
    # Select test path based on arguments
    test_path = args.test_path
    if args.linkedin:
        test_path = "tests/test_linkedin.py"
    
    # Run the tests
    return run_tests(test_path, args.verbose)

if __name__ == "__main__":
    sys.exit(main())
