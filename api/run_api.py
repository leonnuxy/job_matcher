"""
Script to run the FastAPI server for the job_matcher API.
Now serves as a library module for the unified CLI in main.py.
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
    # Get port and host from environment variables if set
    port = int(os.environ.get("API_PORT", 8000))
    host = os.environ.get("API_HOST", "127.0.0.1")
    uvicorn.run("api.api:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    from main import main as unified_main
    unified_main()
