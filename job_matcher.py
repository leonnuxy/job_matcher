#!/usr/bin/env python3
"""
Simple wrapper script to run the job_matcher CLI with the correct Python path.
This allows users to run the CLI from anywhere without setting PYTHONPATH manually.
"""
import os
import sys
import subprocess

def main():
    """Run the job_matcher CLI with the correct Python path."""
    # Get the project root directory (parent of this script)
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Add project root to PYTHONPATH
    env = os.environ.copy()
    
    # If PYTHONPATH is already set, append to it, otherwise set it
    python_path = env.get("PYTHONPATH", "")
    if python_path:
        env["PYTHONPATH"] = f"{project_root}:{python_path}"
    else:
        env["PYTHONPATH"] = project_root
    
    # Construct the command to run main.py
    main_script = os.path.join(project_root, "main.py")
    cmd = [sys.executable, main_script] + sys.argv[1:]
    
    # Execute the command with the modified environment
    return subprocess.call(cmd, env=env)

if __name__ == "__main__":
    sys.exit(main())
