"""
File utilities for reading, writing, and saving optimized content.
"""
import os
import datetime
from typing import Optional


def read_text_file(filepath: str) -> Optional[str]:
    """
    Read text from a file with error handling.
    
    Args:
        filepath: Path to the file to read
        
    Returns:
        Text content or None if the file couldn't be read
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None


def write_text_file(content: str, filepath: str, create_dirs: bool = True) -> bool:
    """
    Write text to a file with error handling.
    
    Args:
        content: Text content to write
        filepath: Path to write the file to
        create_dirs: Whether to create parent directories if they don't exist
        
    Returns:
        True if writing was successful, False otherwise
    """
    try:
        if create_dirs:
            os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
        return True
    except Exception as e:
        print(f"Error writing to file {filepath}: {e}")
        return False


def save_optimized_resume(content: str, out_dir: str = None, include_timestamp: bool = True, 
                    custom_suffix: str = "", job_title: str = "", job_company: str = "") -> str:
    """
    Save an optimized resume to a file with proper formatting.
    
    Args:
        content: The content of the optimized resume
        out_dir: Output directory path (optional)
        include_timestamp: Whether to include a timestamp in the filename
        custom_suffix: Optional custom suffix for the filename
        job_title: Optional job title for the filename (legacy support)
        job_company: Optional company name for the filename (legacy support)
        
    Returns:
        str: The path to the saved resume file
    """
    # Create the output directory if it doesn't exist
    if out_dir is None:
        out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                              "data", "optimization_results")
    os.makedirs(out_dir, exist_ok=True)
    
    # Create a filename based on job details and timestamp
    timestamp = ""
    if include_timestamp:
        timestamp = f"_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    
    # Handle different ways of specifying filename
    suffix = ""
    if custom_suffix:
        suffix = f"_{custom_suffix}"
    elif job_title or job_company:
        # Legacy support
        job_info = ""
        if job_title:
            job_info += f"_{job_title.replace(' ', '_')}"
        if job_company:
            job_info += f"_{job_company.replace(' ', '_')}"
        suffix = job_info
    
    filename = f"Resume{suffix}{timestamp}.md"
    filepath = os.path.join(out_dir, filename)
    
    # Create a symlink to the latest resume
    latest_path = os.path.join(out_dir, "latest_resume.md")
    
    # Write the optimized resume to the file
    with open(filepath, "w") as f:
        f.write(content)
    
    # Update the "latest" symlink
    try:
        if os.path.exists(latest_path):
            os.remove(latest_path)
        os.symlink(os.path.basename(filepath), latest_path)
    except Exception as e:
        pass  # Symlink creation is not critical
        
    return filepath
