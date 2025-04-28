import logging
import requests
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import API_KEY, CSE_ID, GEMINI_API_KEY


def search_jobs(query, api_key=None, cse_id=None, max_age_hours=None):
    """
    Search for jobs using Google Custom Search Engine (CSE).
    Optionally filter results to those published within max_age_hours.
    Returns a list of dicts with 'title', 'link', and 'snippet'.
    Logs errors and returns an empty list on failure.
    """
    api_key = api_key or API_KEY
    cse_id = cse_id or CSE_ID
    try:
        service = build("customsearch", "v1", developerKey=api_key)
        # Add dateRestrict if max_age_hours is set
        params = {'q': query, 'cx': cse_id, 'num': 10}
        if max_age_hours:
            # Google CSE supports dateRestrict in days only
            days = max(1, int(max_age_hours // 24))
            params['dateRestrict'] = f'd{days}'
        res = service.cse().list(**params).execute()
        items = res.get('items', [])
        results = []
        for item in items:
            results.append({
                'title': item.get('title', ''),
                'link': item.get('link', ''),
                'snippet': item.get('snippet', '')
            })
        return results
    except HttpError as e:
        logging.error(f"Google CSE API error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in search_jobs: {e}")
    return []


def optimize_resume_with_gemini(resume_text, job_description):
    """
    Calls Google Gemini API to optimize the resume based on the job description.
    Returns the optimized resume or suggestions as a string.
    """
    try:
        endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        headers = {"Content-Type": "application/json"}
        prompt = (
            "You are an expert career coach and resume writer. "
            "Given the following resume and job description, suggest improvements to the resume to better match the job. "
            "Return the improved resume or a list of specific suggestions.\n"
            f"Resume:\n{resume_text}\nJob Description:\n{job_description}"
        )
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1024}
        }
        params = {"key": GEMINI_API_KEY}
        response = requests.post(endpoint, headers=headers, params=params, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        # Extract the generated text from Gemini's response
        return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        logging.error(f"Gemini API error: {e}")
        return "[Error: Could not optimize resume with Gemini AI.]"
