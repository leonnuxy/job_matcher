#!/usr/bin/env python
"""
Enhanced Resume Optimizer that leverages the lenient matching algorithm 
to better tailor resumes to job descriptions and provide feedback on match quality.
"""
import os
import sys
import json
import logging
from typing import Dict, Optional, Tuple, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add parent directory to sys.path if running as a module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import project modules
from optimizer.optimize import optimize_resume
from services.utils import save_optimized_resume
from job_search.matcher import calculate_match_score, create_matching_profile, extract_keywords


def analyze_job_resume_match(resume_text: str, job_description: Dict) -> Dict:
    """
    Analyze how well a resume matches a job description and identify improvement areas.
    
    Args:
        resume_text: The text of the resume
        job_description: Dictionary containing job details
    
    Returns:
        Dictionary with match analysis including score and recommendations
    """
    # Get job info
    job_title = job_description.get("title", "Unknown Title")
    company = job_description.get("company", "Unknown Company")
    job_desc = job_description.get("description", "")
    job_keywords = job_description.get("keywords", [])
    
    # If keywords aren't provided, extract them
    if not job_keywords and job_desc:
        job_keywords = extract_keywords(job_desc)
        # Add job title words as keywords if they're not already included
        if job_title:
            title_words = [word.lower() for word in job_title.split() if len(word) > 3]
            for word in title_words:
                if word not in job_keywords:
                    job_keywords.append(word)
    
    # Create a lenient matching profile
    matching_profile = create_matching_profile(matching_mode="lenient")
    
    # Calculate match score using our enhanced lenient algorithm
    match_score = calculate_match_score(resume_text, job_description, matching_profile)
    
    # Extract keywords from resume
    resume_keywords = extract_keywords(resume_text)
    
    # Find keywords in the job description that are missing from the resume
    missing_keywords = [kw for kw in job_keywords if kw.lower() not in [rk.lower() for rk in resume_keywords]]
    
    # Find keywords that appear in both the resume and job description
    matching_keywords = [kw for kw in job_keywords if kw.lower() in [rk.lower() for rk in resume_keywords]]
    
    # Return analysis dictionary
    analysis = {
        "job_title": job_title,
        "company": company,
        "match_score": match_score,
        "match_score_percentage": f"{match_score * 100:.1f}%",
        "matching_keywords": matching_keywords,
        "missing_keywords": missing_keywords,
        "matching_profile": matching_profile,
        "resume_analysis": {
            "keyword_count": len(resume_keywords),
            "extracted_keywords": resume_keywords
        }
    }
    
    return analysis


def generate_enhanced_prompt(
    resume_text: str, 
    job_description: Dict, 
    prompt_template: str,
    match_analysis: Optional[Dict] = None
) -> str:
    """
    Generate an enhanced prompt for resume optimization based on matching analysis.
    
    Args:
        resume_text: The text of the resume
        job_description: Dictionary containing job details
        prompt_template: The base prompt template
        match_analysis: Optional pre-computed match analysis
    
    Returns:
        Enhanced prompt with match analysis and keyword recommendations
    """
    # Get match analysis if not provided
    if not match_analysis:
        match_analysis = analyze_job_resume_match(resume_text, job_description)
    
    # Get job description text
    job_desc_text = job_description.get("description", "")
    
    # Create a section highlighting keywords to emphasize
    keyword_section = "KEYWORD RECOMMENDATIONS:\n"
    if match_analysis["missing_keywords"]:
        keyword_section += "Try to incorporate these missing keywords from the job description:\n"
        for kw in match_analysis["missing_keywords"][:10]:  # Limit to top 10 keywords
            keyword_section += f"- {kw}\n"
    else:
        keyword_section += "Your resume already contains many relevant keywords for this position.\n"
    
    keyword_section += "\nHighlight these matching keywords that already appear in your resume:\n"
    for kw in match_analysis["matching_keywords"][:10]:  # Limit to top 10 matching keywords
        keyword_section += f"- {kw}\n"
    
    # Add match score information
    match_info = f"""
MATCH ANALYSIS:
- Current match score: {match_analysis['match_score_percentage']}
- Job title: {match_analysis['job_title']}
- Company: {match_analysis['company']}
    """
    
    # Enhance the prompt by adding our analysis sections before the job description
    enhanced_prompt = prompt_template.replace("{resume_text}", resume_text.strip())
    enhanced_prompt = enhanced_prompt.replace("{job_description}", 
                                             f"{match_info}\n\n{keyword_section}\n\nJOB DESCRIPTION:\n{job_desc_text}")
    
    return enhanced_prompt


def optimize_resume_with_enhanced_matching(
    resume_text: str,
    job: Dict,
    prompt_template: str,
    output_dir: str
) -> Tuple[str, str, Dict]:
    """
    Optimize a resume using the enhanced matching algorithm and feedback.
    
    Args:
        resume_text: The text of the resume
        job: Dictionary containing job details
        prompt_template: The prompt template for resume optimization
        output_dir: Directory to save the optimized resume
    
    Returns:
        Tuple of (optimized_resume_markdown, output_path, match_analysis)
    """
    try:
        # First, analyze the match
        match_analysis = analyze_job_resume_match(resume_text, job)
        
        # Generate enhanced prompt
        enhanced_prompt = generate_enhanced_prompt(resume_text, job, prompt_template, match_analysis)
        
        # Generate optimized resume using the enhanced prompt
        logging.info(f"Optimizing resume for: {job.get('title')} at {job.get('company')}")
        optimized_md = optimize_resume(resume_text, job.get("description", ""), enhanced_prompt)
        
        # Create safe filename components
        job_title_safe = "".join(c if c.isalnum() else "_" for c in job.get('title', 'Unknown'))
        company_safe = "".join(c if c.isalnum() else "_" for c in job.get('company', 'Unknown'))
        custom_suffix = f"{job_title_safe}_{company_safe}"
        
        # Save optimized resume
        output_path = save_optimized_resume(
            optimized_md,
            output_dir,
            include_timestamp=True,
            custom_suffix=custom_suffix
        )
        
        # Return the optimized resume and match analysis
        return optimized_md, output_path, match_analysis
    
    except Exception as e:
        logging.error(f"Error optimizing resume: {e}")
        return "", "", {"error": str(e)}


def main():
    """
    Main entry point for the enhanced resume optimizer.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Optimize resume with enhanced job matching")
    parser.add_argument("--resume", "-r", default=os.path.join(parent_dir, "data", "resume.txt"), 
                       help="Path to resume file (default: data/resume.txt)")
    parser.add_argument("--job", "-j", default=os.path.join(parent_dir, "data", "job_descriptions", "job_description.txt"),
                       help="Path to job description file (default: data/job_descriptions/job_description.txt)")
    parser.add_argument("--prompt", "-p", default=os.path.join(parent_dir, "prompt.txt"),
                       help="Path to prompt template file (default: prompt.txt)")
    parser.add_argument("--output-dir", "-o", default=os.path.join(parent_dir, "data", "optimization_results"),
                       help="Output directory (default: data/optimization_results)")
    parser.add_argument("--analyze-only", action="store_true", 
                       help="Only analyze match without generating resume")
    args = parser.parse_args()
    
    # Check if files exist
    for filepath in [args.prompt, args.resume, args.job]:
        if not os.path.exists(filepath):
            logging.error(f"File not found: {filepath}")
            sys.exit(1)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Load files
    with open(args.prompt, "r") as f:
        prompt_template = f.read()
    with open(args.resume, "r") as f:
        resume_text = f.read()
    with open(args.job, "r") as f:
        job_text = f.read()
    
    # Try to parse job text as JSON first
    try:
        job = json.loads(job_text)
    except:
        # If not JSON, treat as plain text
        job = {
            "description": job_text,
            "title": os.path.basename(args.job).replace(".txt", "").replace("_", " ").title(),
            "company": "Unknown"
        }
    
    if args.analyze_only:
        # Only analyze match
        match_analysis = analyze_job_resume_match(resume_text, job)
        print(json.dumps(match_analysis, indent=2))
    else:
        # Optimize resume
        optimized_md, output_path, match_analysis = optimize_resume_with_enhanced_matching(
            resume_text, job, prompt_template, args.output_dir
        )
        
        if output_path:
            print(f"Optimized resume saved to: {output_path}")
            print(f"Match score: {match_analysis['match_score_percentage']}")
            
            if match_analysis["missing_keywords"]:
                print("\nMissing keywords addressed in the optimized resume:")
                for kw in match_analysis["missing_keywords"][:5]:
                    print(f"- {kw}")
            
            # Print first few lines to confirm it worked
            preview_lines = optimized_md.split('\n')[:10]
            print("\nPreview:")
            print('\n'.join(preview_lines))
            print("...")
        else:
            print("Failed to optimize resume.")


if __name__ == "__main__":
    main()
