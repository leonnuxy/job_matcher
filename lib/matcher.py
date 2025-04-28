# lib/matcher.py
def calculate_similarity(resume_skills, job_skills):
    """
    Calculates the similarity percentage between resume skills and job requirements.

    Normalizes skills to lowercase and strips whitespace before comparison.

    Args:
        resume_skills (list): List of skills extracted from the resume.
        job_skills (list): List of skills extracted from the job description.

    Returns:
        float: Similarity percentage (0-100), rounded to two decimal places.  Returns 0 if
               job_skills is empty to avoid division by zero.
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


def adjust_resume(resume_text, job_keywords, ai_api_key=None):
    """
    Suggests improvements to the resume based on missing job requirements.

    If ai_api_key is provided, uses Gemini AI for optimization. Otherwise, provides
    basic text-based suggestions.

    Args:
        resume_text (str): The text content of the resume.
        job_keywords (list): List of keywords/skills from the job description.
        ai_api_key (str, optional): API key for Gemini AI. Defaults to None.

    Returns:
        str: Suggestions for improving the resume, or the optimized resume text
             if Gemini AI is used.
    """
    print("Adjusting resume")

    if ai_api_key:
        try:
            from lib.api_calls import optimize_resume_with_gemini  # Import locally
            job_desc = '\n'.join(job_keywords) if isinstance(job_keywords, list) else str(job_keywords)
            return optimize_resume_with_gemini(resume_text, job_desc, ai_api_key)
        except ImportError as e:
            return f"Error: Could not import optimize_resume_with_gemini.  Ensure lib/api_calls.py exists and is accessible. {e}"
        except Exception as e:
            return f"Error using Gemini AI: {e}"

    from lib import resume_parser
    resume_skills = resume_parser.extract_resume_skills(resume_text)

    # Normalize and convert to sets for efficient comparison
    resume_set = {s.lower().strip() for s in resume_skills if s and isinstance(s, str)}
    job_set = {s.lower().strip() for s in job_keywords if s and isinstance(s, str)}

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