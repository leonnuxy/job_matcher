"""
Utility functions for the job_matcher application.
"""
import os
import re
import datetime
from typing import Optional
import sys

# Add parent directory to sys.path if running as a module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

def get_job_description_name(path: str) -> str:
    """Extract job description name from file path."""
    return os.path.splitext(os.path.basename(path))[0]

def generate_filename(include_timestamp=True, custom_suffix=None) -> str:
    """Generate a filename for an optimized resume."""
    base = "Noel_Ugwoke_Resume"
    if custom_suffix:
        base += f"_{custom_suffix}"
    if include_timestamp:
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base += f"_{ts}"
    # sanitize
    name = re.sub(r'[^\w\-\.]', '', base) + ".md"
    return name

def save_optimized_resume(optimized_md: str, output_dir: str, 
                          include_timestamp: bool = True, 
                          custom_suffix: Optional[str] = None) -> str:
    """
    Save the optimized resume and update the latest symlink.
    Returns the path to the saved file.
    """
    os.makedirs(output_dir, exist_ok=True)
    filename = generate_filename(include_timestamp, custom_suffix)
    output_path = os.path.join(output_dir, filename)
    
    with open(output_path, "w") as f:
        f.write(optimized_md)
        
    # Update symlink to latest resume
    latest = os.path.join(output_dir, "latest_resume.md")
    try:
        if os.path.exists(latest) or os.path.islink(latest):
            os.remove(latest)
        rel = os.path.relpath(output_path, os.path.dirname(latest))
        os.symlink(rel, latest)
    except Exception as e:
        print(f"Note: Could not create symbolic link to latest resume: {e}")
        
    return output_path
