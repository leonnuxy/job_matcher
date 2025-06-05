# lib/matcher.py
import logging
from lib import api_calls

def calculate_similarity(resume_skills, job_skills):
    """
    Calculate similarity score between resume skills and job skills.
    
    Args:
        resume_skills (list): List of skills extracted from the resume
        job_skills (list): List of skills extracted from the job description
        
    Returns:
        float: Percentage score representing the match
    """
    print("Calculating similarity")

    if not job_skills:
        print("Warning: No job skills provided. Returning 0 similarity.")  # Log this for debugging
        return 0.0

    # Normalize and convert to sets for efficient comparison
    resume_set = {s.lower().strip() for s in resume_skills if s and isinstance(s, str)} # Robust check
    job_set = {s.lower().strip() for s in job_skills if s and isinstance(s, str)} # Robust check

    matched_skills = resume_set.intersection(job_set)
    similarity_percentage = (len(matched_skills) / len(job_set)) * 100

    return round(similarity_percentage, 2)


def adjust_resume(resume_skills, job_skills):
    """
    Provide suggestions for adjusting the resume based on job skills.
    
    Args:
        resume_skills (list): List of skills extracted from the resume
        job_skills (list): List of skills extracted from the job description
        
    Returns:
        str: Suggestions for resume improvement
    """
    print("Adjusting resume")

    # Normalize and convert to sets for efficient comparison
    resume_set = {s.lower().strip() for s in resume_skills if s and isinstance(s, str)}
    job_set = {s.lower().strip() for s in job_skills if s and isinstance(s, str)}

    missing_skills = job_set - resume_set

    if not missing_skills:
        return "Your resume already covers all key job requirements!"

    suggestions = "The following job requirements are missing from your resume:\n"
    suggestions += ", ".join(missing_skills) + "\n\n"
    suggestions += "Consider adding the following lines to your resume (tailor them to your specific experience):\n"

    for skill in missing_skills:
        suggestions += f"- Demonstrated proficiency in {skill} through [relevant project/experience].\n"
        suggestions += f"- Utilized {skill} to achieve [specific outcome] in [relevant role].\n"

    return suggestions


def optimize_resume(resume_text, job_description):
    """
    Comprehensive resume optimization using both simple matching and AI-based suggestions.
    
    Args:
        resume_text (str): Full text of the resume
        job_description (str): Full text of the job description
        
    Returns:
        dict: Optimization results including both keyword-based and AI-based suggestions
    """
    from lib import resume_parser, job_parser
    
    # Extract skills from both documents
    resume_skills = resume_parser.extract_resume_skills(resume_text)
    job_skills = job_parser.extract_job_requirements(job_description)
    
    # Calculate match score
    match_score = calculate_similarity(resume_skills, job_skills)
    
    # Get basic keyword suggestions
    keyword_suggestions = adjust_resume(resume_skills, job_skills)
    
    # Get AI-powered optimization if available
    try:
        # Use the optimization utility instead of deprecated function
        from lib.optimization_utils import generate_optimized_documents
        _, _, raw_response = generate_optimized_documents(resume_text, job_description)
        ai_suggestions = raw_response if raw_response else "No optimization result available."
    except Exception as e:
        logging.error(f"AI optimization failed: {e}")
        ai_suggestions = "AI optimization unavailable at this time."
    
    return {
        'match_score': match_score,
        'keyword_suggestions': keyword_suggestions,
        'ai_suggestions': ai_suggestions,
        'missing_skills': list(set(job_skills) - set(resume_skills)),
        'matched_skills': list(set(job_skills) & set(resume_skills)),
    }