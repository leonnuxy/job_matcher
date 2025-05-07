"""
Example usage of the resume_optimizer package.

This script demonstrates how to use the resume_optimizer package
to optimize a resume for a specific job description.
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import resume_optimizer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resume_optimizer import optimize_resume


def main():
    """Demonstrate resume optimization with example data."""
    # Get paths to sample data
    base_dir = Path(__file__).parent.parent
    resume_path = base_dir / "data" / "resume.txt"
    job_desc_path = base_dir / "data" / "job_descriptions" / "job_description.txt"
    
    # Check if files exist
    if not resume_path.exists() or not job_desc_path.exists():
        print(f"Error: Required files not found. Please ensure these files exist:")
        print(f"  - {resume_path}")
        print(f"  - {job_desc_path}")
        sys.exit(1)
    
    # Read input files
    print(f"Reading resume from: {resume_path}")
    with open(resume_path, "r") as f:
        resume_text = f.read()
    
    print(f"Reading job description from: {job_desc_path}")
    with open(job_desc_path, "r") as f:
        job_description = f.read()
    
    try:
        # Call the optimizer
        print("Optimizing resume...")
        result = optimize_resume(resume_text, job_description)
        
        # Create output directory if it doesn't exist
        output_dir = base_dir / "data" / "optimization_results"
        output_dir.mkdir(exist_ok=True, parents=True)
        
        # Generate output filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"resume_optimization_{timestamp}.txt"
        
        # Write results to file
        with open(output_path, "w") as f:
            # Write a readable summary
            f.write("RESUME OPTIMIZATION RESULTS\n")
            f.write("==========================\n\n")
            
            f.write("SUMMARY\n")
            f.write("-------\n")
            f.write(result["summary"])
            f.write("\n\n")
            
            f.write("SKILLS TO ADD\n")
            f.write("-------------\n")
            for skill in result["skills_to_add"]:
                f.write(f"- {skill}\n")
            f.write("\n")
            
            f.write("SKILLS TO REMOVE\n")
            f.write("---------------\n")
            for skill in result["skills_to_remove"]:
                f.write(f"- {skill}\n")
            f.write("\n")
            
            f.write("EXPERIENCE TWEAKS\n")
            f.write("----------------\n")
            for tweak in result["experience_tweaks"]:
                f.write("Original:\n")
                f.write(f"  {tweak['original']}\n\n")
                f.write("Optimized:\n")
                f.write(f"  {tweak['optimized']}\n\n")
            
            f.write("FORMATTING SUGGESTIONS\n")
            f.write("---------------------\n")
            for suggestion in result["formatting_suggestions"]:
                f.write(f"- {suggestion}\n")
            f.write("\n")
            
            f.write("COLLABORATION POINTS\n")
            f.write("-------------------\n")
            for point in result["collaboration_points"]:
                f.write(f"- {point}\n")
        
        # Also save the raw JSON for programmatic use
        json_output_path = output_path.with_suffix(".json")
        with open(json_output_path, "w") as f:
            json.dump(result, f, indent=2)
        
        print(f"Optimization complete! Results saved to:")
        print(f"  - Human-readable: {output_path}")
        print(f"  - JSON format: {json_output_path}")
        
    except Exception as e:
        print(f"Error optimizing resume: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
