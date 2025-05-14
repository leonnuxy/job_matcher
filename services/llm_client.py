# llm_client.py
import os
import sys
import time
import google.generativeai as genai
import openai
from typing import Any

# Add parent directory to sys.path if running as a module
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from config import GEMINI_API_KEY, OPENAI_API_KEY, get_llm_provider

# Determine which LLM provider to use
LLM_PROVIDER = get_llm_provider().lower()

# One-time testing flag
TESTING = os.getenv("TESTING", "").lower() in ("true", "1", "yes")

# Warn if credentials are missing
if not TESTING:
    if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
        print("Warning: OpenAI selected but OPENAI_API_KEY not found")
    elif LLM_PROVIDER == "gemini" and not GEMINI_API_KEY:
        print("Warning: Gemini selected but GEMINI_API_KEY not found")

# Configure providers (skip in testing)
if not TESTING:
    if LLM_PROVIDER == "gemini":
        if not GEMINI_API_KEY:
            raise RuntimeError("Please set GEMINI_API_KEY for Gemini provider")
        genai.configure(api_key=GEMINI_API_KEY)
    elif LLM_PROVIDER == "openai":
        if not OPENAI_API_KEY:
            raise RuntimeError("Please set OPENAI_API_KEY for OpenAI provider")
        openai.api_key = OPENAI_API_KEY
    else:
        raise RuntimeError(f"Unknown LLM_PROVIDER: {LLM_PROVIDER}")

# Retry settings
_MAX_RETRIES = 3
_TIMEOUT = 5  # seconds

class LLMClient:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        """Call the chosen provider, with retries and fallback."""
        # Use mock response in testing mode or when API keys are missing
        if TESTING or (LLM_PROVIDER == "gemini" and not GEMINI_API_KEY) or (LLM_PROVIDER == "openai" and not OPENAI_API_KEY):
            # Return a mock response with both resume and cover letter in the expected format
            mock_path = os.path.join(parent_dir, "tests", "mock_llm_response.txt")
            if os.path.exists(mock_path):
                try:
                    with open(mock_path, "r") as f:
                        return f.read()
                except Exception as e:
                    print(f"Error reading mock response: {e}")
            
            # Create a simplified mock response to use as fallback
            return """---BEGIN_RESUME---
# NOEL UGWOKE
Calgary, Alberta | 306-490-2929 | 1leonnoel1@gmail.com | [LinkedIn](https://www.linkedin.com/in/noelugwoke/) | [Portfolio](https://noelugwoke.com/)

## TECHNICAL SKILLS
- **Languages & Frameworks:** Python, TypeScript/Node.js, SQL, Java, JavaScript, C++, C#
- **Machine Learning:** TensorFlow, PyTorch, Scikit-learn, MLOps, Feature Engineering

## PROFESSIONAL EXPERIENCE

**Software Engineer (Cloud & Data)**
APEGA | Calgary, AB | Dec 2022 – Dec 2024
* Developed and deployed scalable, containerized AI/ML applications on AWS using Kubernetes, leveraging Python, TensorFlow, and PyTorch.
---END_RESUME---

---BEGIN_COVER_LETTER---
Noel Ugwoke
[Your Address]
[City, State, Zip]
[Your Email]
[Your Phone Number]
[Date]

Hiring Manager
[Company Name]
[Company Location, if provided]

Dear Hiring Manager,

I am writing to express my interest in the [Job Title] position at [Company Name] as advertised on [Platform where you saw the ad]. My experience in AI/ML development aligns perfectly with your needs.

I am particularly drawn to [Company Name]'s work in [Mention a specific area of the company's work if known, otherwise, mention something positive like "cutting-edge technology" or "impactful projects"].

Sincerely,
Noel Ugwoke
---END_COVER_LETTER---"""

        backoff = 1
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                if LLM_PROVIDER == "gemini":
                    model = genai.GenerativeModel(self.model_name)
                    resp  = model.generate_content(prompt)  # no timeout param
                    return resp.text
                else:
                    # Try new OpenAI client
                    try:
                        from openai import OpenAI
                        client = OpenAI(api_key=OPENAI_API_KEY)
                        resp = client.chat.completions.create(
                            model=self.model_name,
                            messages=[{"role": "user", "content": prompt}],
                            timeout=_TIMEOUT
                        )
                        return resp.choices[0].message.content
                    except (ImportError, AttributeError):
                        # Fallback to classic client
                        resp = openai.ChatCompletion.create(
                            model=self.model_name,
                            messages=[{"role": "user", "content": prompt}],
                            timeout=_TIMEOUT
                        )
                        return resp.choices[0].message.content

            except Exception as e:
                if attempt == _MAX_RETRIES:
                    raise
                time.sleep(backoff)
                backoff *= 2