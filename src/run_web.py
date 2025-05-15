"""
Script to run the Flask web application.
Now serves as a wrapper around the unified CLI in main.py.
"""
from main import main as unified_main

if __name__ == "__main__":
    unified_main()
