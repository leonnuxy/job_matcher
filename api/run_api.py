"""
Script to run the FastAPI server for the job_matcher API.
"""
import uvicorn
import os
import sys

# Add the parent directory to sys.path if running as a module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def main():
    """Run the FastAPI server."""
    uvicorn.run("api.api:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
