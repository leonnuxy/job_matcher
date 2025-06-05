#!/usr/bin/env python
"""
Consolidated Resume and Cover Letter Optimizer

This module consolidates functionality from:
- optimize.py
- enhanced_optimizer.py
- enhanced_optimizer_with_cover_letter.py

It supports:
1. Basic resume optimization
2. Enhanced resume optimization with keyword matching
3. Cover letter generation
4. Placeholder sanitization in both resume and cover letter
"""
import os
import sys
import json
import re
import logging
from typing import Dict, Optional, Tuple, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Add parent directory to sys.path if running as a module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import project modules
from services.llm_client import LLMClient, LLM_PROVIDER
from services.utils import save_optimized_resume, extract_text_between_delimiters
from services.cover_letter import sanitize_cover_letter, save_cover_letter, extract_cover_letter

# Define our own versions of the functions to avoid circular imports
def create_matching_profile(matching_mode="strict", threshold=0.75):
    """
    Create a matching profile with appropriate settings for resume-job matching
    
    Args:
        matching_mode: The matching mode to use (strict, balanced, lenient)
        threshold: The threshold for considering a match
    
    Returns:
        Dictionary with matching profile settings
    """
    if matching_mode == "strict":
        return {
            "mode": "strict",
            "exact_match_weight": 1.0,  # Exact matches worth full value
            "substring_weight": 0.5,    # Substrings are half value
            "threshold": threshold,
            "require_all_keywords": True
        }
    elif matching_mode == "balanced":
        return {
            "mode": "balanced",
            "exact_match_weight": 1.0,
            "substring_weight": 0.75,  # Higher value for partial matches
            "threshold": threshold * 0.9,
            "require_all_keywords": False
        }
    else:  # lenient
        return {
            "mode": "lenient",
            "exact_match_weight": 1.0,
            "substring_weight": 0.9,  # Near-full value for partial matches
            "threshold": threshold * 0.8,
            "require_all_keywords": False
        }
        
def extract_keywords(text, min_length=4):
    """
    Extract probable keywords from text
    
    Args:
        text: The text to extract keywords from
        min_length: Minimum length for a keyword
    
    Returns:
        List of extracted keywords
    """
    # Basic keyword extraction
    words = re.findall(r'\b[A-Za-z][\w\+\#\-\.]*\b', text)
    keywords = [word.lower() for word in words if len(word) >= min_length]
    
    # Count frequencies
    from collections import Counter
    keyword_counter = Counter(keywords)
    
    # Get unique keywords sorted by frequency
    return [kw for kw, _ in keyword_counter.most_common(50)]
    
def calculate_match_score(resume_text, job_description, matching_profile):
    """
    Calculate how well a resume matches a job description
    
    Args:
        resume_text: The text of the resume
        job_description: Dictionary or string with job details
        matching_profile: Settings for how to calculate match
    
    Returns:
        Float between 0 and 1 indicating match quality
    """
    # Extract job description text if it's a dictionary
    job_text = job_description.get("description", "") if isinstance(job_description, dict) else job_description
    
    # Extract keywords
    job_keywords = extract_keywords(job_text)
    resume_keywords = extract_keywords(resume_text)
    
    # Count matches
    exact_matches = 0
    substring_matches = 0
    
    for job_kw in job_keywords:
        if job_kw in resume_keywords:
            exact_matches += 1
        else:
            # Check for substring matches
            for resume_kw in resume_keywords:
                if (job_kw in resume_kw) or (resume_kw in job_kw):
                    substring_matches += 1
                    break
    
    # Calculate score
    total_keywords = len(job_keywords)
    if total_keywords == 0:
        return 0.0
        
    exact_match_score = exact_matches * matching_profile["exact_match_weight"]
    substring_match_score = substring_matches * matching_profile["substring_weight"]
    
    total_score = (exact_match_score + substring_match_score) / total_keywords
    
    # Apply threshold for strict mode
    if matching_profile["require_all_keywords"] and exact_matches < total_keywords:
        return total_score * 0.8  # Penalize for missing keywords
        
    return min(1.0, total_score)  # Cap at 1.0

# Define model names for different providers
MODEL_MAP = {
    "gemini": "gemini-1.5-flash-latest",  # Updated to a generally available model
    "openai": "gpt-4o-mini"  # Updated to a newer, cost-effective model
}

# Initialize the LLM client
client = LLMClient(model_name=MODEL_MAP.get(LLM_PROVIDER, "gemini-1.5-flash-latest"))  # Fallback if provider not in map


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


def optimize_resume(
    resume_text: str, 
    job_description: str, 
    prompt_template: str
) -> str:
    """
    Generate an optimized resume using an LLM based on the provided template.
    
    Args:
        resume_text: The text of the resume
        job_description: The job description text
        prompt_template: The prompt template to use
        
    Returns:
        Optimized resume in Markdown format
    """
    try:
        # Replace placeholders directly
        prompt = prompt_template.replace("{resume_text}", resume_text.strip())
        prompt = prompt.replace("{job_description}", job_description.strip())
        
        full_llm_response = client.generate(prompt)

        if not full_llm_response:
            logging.error("LLM returned an empty response.")
            return ""

        optimized_resume_md = extract_text_between_delimiters(full_llm_response, "---BEGIN_RESUME---", "---END_RESUME---")

        if not optimized_resume_md:
            logging.warning("Could not extract optimized resume from LLM response.")
            # Return the full response if we couldn't extract the resume part
            return full_llm_response
            
        return optimized_resume_md

    except Exception as e:
        logging.error(f"Error during LLM call or parsing: {e}")
        # Fallback to default resume template if API call fails
        default_resume_template_path = os.path.join(parent_dir, "data", "resume_template", "Noel Ugwoke Resume.md")
        if os.path.exists(default_resume_template_path):
            with open(default_resume_template_path, "r") as f:
                return f.read()
        else:
            # Basic fallback if template is missing
            return """# NOEL UGWOKE
Calgary, Alberta | 306-490-2929 | 1leonnoel1@gmail.com | [LinkedIn](https://www.linkedin.com/in/noelugwoke/) | [Portfolio](https://noelugwoke.com/)
## TECHNICAL SKILLS
- Default skills...
"""


def optimize_resume_and_generate_cover_letter(
    resume_text: str, 
    job_description: str, 
    prompt_template: str,
    job_info: Dict = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns the AI-generated, Markdown-formatted optimized resume and cover letter.
    Returns (None, None) if generation fails or parsing fails.
    
    Args:
        resume_text: The text of the resume
        job_description: The job description text
        prompt_template: The prompt template to use
        job_info: Optional dictionary with job details like title and company
        
    Returns:
        Tuple of (optimized_resume_md, cover_letter_md)
    """
    try:
        # Replace placeholders directly
        prompt = prompt_template.replace("{resume_text}", resume_text.strip())
        prompt = prompt.replace("{job_description}", job_description.strip())
        
        full_llm_response = client.generate(prompt)

        if not full_llm_response:
            logging.error("LLM returned an empty response.")
            return None, None

        optimized_resume_md = extract_text_between_delimiters(full_llm_response, "---BEGIN_RESUME---", "---END_RESUME---")
        cover_letter_md = extract_text_between_delimiters(full_llm_response, "---BEGIN_COVER_LETTER---", "---END_COVER_LETTER---")

        if not optimized_resume_md:
            logging.warning("Could not extract optimized resume from LLM response.")
        if not cover_letter_md:
            logging.warning("Could not extract cover letter from LLM response.")
            
        # Process the cover letter to replace placeholders
        if cover_letter_md and job_info:
            cover_letter_md = sanitize_cover_letter(cover_letter_md, job_info)
        
        return optimized_resume_md, cover_letter_md

    except Exception as e:
        logging.error(f"Error during LLM call or parsing: {e}")
        # Fallback to default resume template if API call fails, no cover letter in this case
        default_resume_template_path = os.path.join(parent_dir, "data", "resume_template", "Noel Ugwoke Resume.md")
        if os.path.exists(default_resume_template_path):
            with open(default_resume_template_path, "r") as f:
                return f.read(), None
        else:
            # Basic fallback if template is missing
            return """# NOEL UGWOKE
Calgary, Alberta | 306-490-2929 | 1leonnoel1@gmail.com | [LinkedIn](https://www.linkedin.com/in/noelugwoke/) | [Portfolio](https://noelugwoke.com/)
## TECHNICAL SKILLS
- Default skills...
""", None


def extract_cover_letter(optimization_response: str, job: Dict = None) -> Optional[str]:
    """
    Extract the cover letter content from the LLM response and replace placeholders.
    
    Args:
        optimization_response: The full response from the LLM
        job: Dictionary containing job details to replace placeholders
        
    Returns:
        str: Extracted cover letter text or None if not found
    """
    cover_letter_pattern = r"---BEGIN_COVER_LETTER---(.*?)---END_COVER_LETTER---"
    match = re.search(cover_letter_pattern, optimization_response, re.DOTALL)
    
    if match:
        cover_letter_text = match.group(1).strip()
        
        # Replace placeholders if job details are provided
        if job:
            cover_letter_text = sanitize_cover_letter(cover_letter_text, job)
        
        return f"---BEGIN_COVER_LETTER---\n{cover_letter_text}\n---END_COVER_LETTER---"
    
    return None


# Using sanitize_cover_letter from services.cover_letter instead


def extract_resume(optimization_response: str) -> str:
    """
    Extract just the resume portion from the LLM response.
    
    Args:
        optimization_response: The full response from the LLM
        
    Returns:
        str: Extracted resume text
    """
    # Check if there's a delimited resume section
    resume_md = extract_text_between_delimiters(optimization_response, "---BEGIN_RESUME---", "---END_RESUME---")
    if resume_md:
        return resume_md
        
    # If no resume section with delimiters, remove any cover letter section and return the rest
    cover_letter_pattern = r"---BEGIN_COVER_LETTER---.*?---END_COVER_LETTER---"
    resume_text = re.sub(cover_letter_pattern, "", optimization_response, flags=re.DOTALL).strip()
    
    return resume_text


def optimize_resume_with_enhanced_matching(
    resume_text: str,
    job: Dict,
    prompt_template: str,
    output_dir: str,
    include_cover_letter: bool = True
) -> Tuple[str, str, Dict, Optional[str], Optional[str]]:
    """
    Optimize a resume using the enhanced matching algorithm and feedback.
    
    Args:
        resume_text: The text of the resume
        job: Dictionary containing job details
        prompt_template: The prompt template for resume optimization
        output_dir: Directory to save the optimized resume
        include_cover_letter: Whether to generate cover letter
    
    Returns:
        Tuple of (optimized_resume_markdown, output_path, match_analysis, cover_letter, cover_letter_path)
    """
    try:
        # First, analyze the match
        match_analysis = analyze_job_resume_match(resume_text, job)
        
        # Generate enhanced prompt
        enhanced_prompt = generate_enhanced_prompt(resume_text, job, prompt_template, match_analysis)
        
        # Generate optimized resume using the enhanced prompt
        logging.info(f"Optimizing resume for: {job.get('title')} at {job.get('company')}")
        optimized_content = optimize_resume(resume_text, job.get("description", ""), enhanced_prompt)
        
        # Extract resume and cover letter portions if needed
        cover_letter = None
        cover_letter_path = None
        
        if include_cover_letter:
            cover_letter = extract_cover_letter(optimized_content, job)
            optimized_resume = extract_resume(optimized_content)
        else:
            optimized_resume = optimized_content
        
        # Create safe filename components
        job_title_safe = "".join(c if c.isalnum() else "_" for c in job.get('title', 'Unknown'))
        company_safe = "".join(c if c.isalnum() else "_" for c in job.get('company', 'Unknown'))
        custom_suffix = f"{job_title_safe}_{company_safe}"
        
        # Save optimized resume
        resume_path = save_optimized_resume(
            optimized_resume,
            output_dir,
            include_timestamp=True,
            custom_suffix=custom_suffix
        )
        
        # Save cover letter if it exists
        if cover_letter:
            cover_letter_path = save_cover_letter(
                cover_letter,
                output_dir,
                include_timestamp=True,
                custom_suffix=custom_suffix
            )
        
        # Return the optimized content and analysis
        return optimized_resume, resume_path, match_analysis, cover_letter, cover_letter_path
    
    except Exception as e:
        logging.error(f"Error optimizing resume: {e}")
        return "", "", {"error": str(e)}, None, None


def main():
    """
    Main entry point for the consolidated optimizer.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Optimize resume with enhanced job matching")
    parser.add_argument("--resume", "-r", default=os.path.join(parent_dir, "data", "resume.txt"), 
                       help="Path to resume file (default: data/resume.txt)")
    parser.add_argument("--job", "-j", default=os.path.join(parent_dir, "data", "job_descriptions", "job_description.txt"),
                       help="Path to job description file (default: data/job_descriptions/job_description.txt)")
    parser.add_argument("--prompt", "-p", default=os.path.join(parent_dir, "prompt_with_cover_letter.txt"),
                       help="Path to prompt template file (default: prompt_with_cover_letter.txt)")
    parser.add_argument("--output-dir", "-o", default=os.path.join(parent_dir, "data", "optimization_results"),
                       help="Output directory (default: data/optimization_results)")
    parser.add_argument("--analyze-only", action="store_true", 
                       help="Only analyze match without generating resume")
    parser.add_argument("--no-cover-letter", action="store_true",
                       help="Skip cover letter generation")
    parser.add_argument("--output-suffix", "-s", help="Custom suffix for output filenames (e.g., job_title_company)")
    parser.add_argument("--no-timestamp", action="store_true", help="Don't include timestamp in filenames")
    parser.add_argument("--basic", action="store_true", 
                       help="Use basic optimization without enhanced matching")
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
    
    # Determine output suffix if not provided
    output_suffix = args.output_suffix
    if not output_suffix:
        job_title_str = "".join(c if c.isalnum() else "_" for c in job.get('title', 'Unknown'))
        company_str = "".join(c if c.isalnum() else "_" for c in job.get('company', 'Unknown'))
        output_suffix = f"{job_title_str}_{company_str}"
    
    if args.analyze_only:
        # Only analyze match
        match_analysis = analyze_job_resume_match(resume_text, job)
        print(json.dumps(match_analysis, indent=2))
    elif args.basic:
        # Use basic optimization without enhanced matching
        logging.info(f"Using basic optimization for job: {job.get('title')} at {job.get('company')}")
        
        if args.no_cover_letter:
            # Generate only resume
            optimized_resume = optimize_resume(resume_text, job.get("description", ""), prompt_template)
            
            # Save optimized resume
            resume_path = save_optimized_resume(
                optimized_resume,
                args.output_dir,
                include_timestamp=not args.no_timestamp,
                custom_suffix=output_suffix
            )
            
            if resume_path:
                print(f"Optimized resume saved to: {resume_path}")
                # Print first few lines of resume to confirm it worked
                preview_lines = optimized_resume.split('\n')[:10]
                print("\nResume Preview:")
                print('\n'.join(preview_lines))
                print("...")
            else:
                print("Failed to optimize resume.")
        else:
            # Generate both resume and cover letter
            optimized_resume, cover_letter = optimize_resume_and_generate_cover_letter(
                resume_text, job.get("description", ""), prompt_template, job
            )
            
            # Save optimized resume
            if optimized_resume:
                resume_path = save_optimized_resume(
                    optimized_resume,
                    args.output_dir,
                    include_timestamp=not args.no_timestamp,
                    custom_suffix=output_suffix
                )
                print(f"Optimized resume saved to: {resume_path}")
                # Print first few lines of resume to confirm it worked
                preview_lines = optimized_resume.split('\n')[:10]
                print("\nResume Preview:")
                print('\n'.join(preview_lines))
                print("...")
            else:
                print("Failed to optimize resume.")
            
            # Save cover letter if it exists
            if cover_letter:
                cover_letter_path = save_cover_letter(
                    cover_letter,
                    args.output_dir,
                    include_timestamp=not args.no_timestamp,
                    custom_suffix=output_suffix
                )
                print(f"\nCover letter saved to: {cover_letter_path}")
                # Print beginning of cover letter
                cover_letter_lines = cover_letter.split('\n')[:5]
                print("\nCover Letter Preview:")
                print('\n'.join(cover_letter_lines))
                print("...")
            else:
                print("Failed to generate cover letter.")
    else:
        # Use enhanced optimization with matching
        optimized_resume, resume_path, match_analysis, cover_letter, cover_letter_path = optimize_resume_with_enhanced_matching(
            resume_text, job, prompt_template, args.output_dir, 
            include_cover_letter=not args.no_cover_letter
        )
        
        if resume_path:
            print(f"Optimized resume saved to: {resume_path}")
            print(f"Match score: {match_analysis['match_score_percentage']}")
            
            if match_analysis["missing_keywords"]:
                print("\nMissing keywords addressed in the optimized resume:")
                for kw in match_analysis["missing_keywords"][:5]:
                    print(f"- {kw}")
            
            # Print first few lines of resume to confirm it worked
            preview_lines = optimized_resume.split('\n')[:10]
            print("\nResume Preview:")
            print('\n'.join(preview_lines))
            print("...")
            
            # Print cover letter info if generated
            if cover_letter and cover_letter_path:
                print(f"\nCover letter saved to: {cover_letter_path}")
                
                # Print beginning of cover letter
                cover_letter_lines = cover_letter.split('\n')[:5]
                print("\nCover Letter Preview:")
                print('\n'.join(cover_letter_lines))
                print("...")
        else:
            print("Failed to optimize resume.")


# For backward compatibility with existing imports
def optimize_resume_for_backward_compat(
    resume_text: str, 
    job_description: str, 
    prompt_template: str
) -> str:
    """For backward compatibility with existing imports from optimize.py"""
    return optimize_resume(resume_text, job_description, prompt_template)


if __name__ == "__main__":
    main()
