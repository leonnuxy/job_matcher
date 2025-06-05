"""
Main entry point for the resume_optimizer package.
Allows the package to be run directly with `python -m resume_optimizer`.

This redirects to the CLI module for consistent interface.
"""

import sys
from .cli import cli_main

def main():
    """
    Run the resume optimizer CLI.
    
    Usage:
        python -m resume_optimizer <job_description_file> [--resume resume.txt] [--output-dir output_dir]
    """
    sys.exit(cli_main())
    parser = argparse.ArgumentParser(description="Optimize a resume based on a job description")
    parser.add_argument("resume", help="Path to the resume text file")
    parser.add_argument("job_description", help="Path to the job description text file")
    parser.add_argument("--output", "-o", help="Path to the output file (JSON format)")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text",
                        help="Output format (default: text)")
    
    args = parser.parse_args()
    
    # Check if input files exist
    if not os.path.isfile(args.resume):
        print(f"Error: Resume file not found: {args.resume}")
        sys.exit(1)
        
    if not os.path.isfile(args.job_description):
        print(f"Error: Job description file not found: {args.job_description}")
        sys.exit(1)
    
    # Read input files
    try:
        with open(args.resume, "r") as f:
            resume_text = f.read()
        
        with open(args.job_description, "r") as f:
            job_description = f.read()
    except Exception as e:
        print(f"Error reading input files: {e}")
        sys.exit(1)
    
    # Generate default output path if not provided
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if args.format == "json":
            args.output = f"resume_optimization_{timestamp}.json"
        else:
            args.output = f"resume_optimization_{timestamp}.txt"
    
    # Run optimization
    try:
        print("Optimizing resume...")
        result = optimize_resume(resume_text, job_description)
        
        # Save output
        if args.format == "json":
            with open(args.output, "w") as f:
                json.dump(result, f, indent=2)
        else:
            with open(args.output, "w") as f:
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
        
        print(f"Optimization complete! Results saved to: {args.output}")
        
    except OptimizerError as e:
        print(f"Optimization error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
