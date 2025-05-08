"""
Main entry point for the job_matcher application.
"""
import os
import argparse
from services.llm_client import LLM_PROVIDER
from optimizer.optimize import optimize_resume
from services.utils import save_optimized_resume, generate_filename


def main():
    parser = argparse.ArgumentParser(description="Optimize resume for a job description")
    parser.add_argument("--job", "-j", default="data/job_descriptions/job_description.txt")
    parser.add_argument("--suffix", "-s")
    parser.add_argument("--no-timestamp", action="store_true")
    args = parser.parse_args()

    # Load files
    with open("prompt.txt") as f:
        prompt_template = f.read()
    with open("data/resume.txt") as f:
        resume_text = f.read()
    with open(args.job) as f:
        job_description = f.read()

    # Optimize
    optimized_md = optimize_resume(resume_text, job_description, prompt_template)

    # Save output using the utility function
    out_dir = "data/optimization_results"
    output_path = save_optimized_resume(
        optimized_md, 
        out_dir, 
        include_timestamp=not args.no_timestamp, 
        custom_suffix=args.suffix
    )
    
    print("Resume optimization complete!")
    print(f"Results saved to: {output_path}")
    print(f"Latest resume link created at: {os.path.join(out_dir, 'latest_resume.md')}")

if __name__ == "__main__":
    main()
