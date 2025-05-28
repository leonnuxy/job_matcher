#!/usr/bin/env python3
"""
Test script for Gemini LLM integration
"""
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

def test_gemini_client():
    """Test the Gemini LLM client."""
    print("Testing Gemini LLM client...")
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment")
        print("Please set your Gemini API key:")
        print("export GEMINI_API_KEY='your-api-key-here'")
        return False
    
    print("✅ GEMINI_API_KEY found")
    
    try:
        from services.llm_client import LLMClient
        
        # Initialize client
        client = LLMClient()
        print("✅ LLM client initialized successfully")
        
        # Test with a simple prompt
        test_prompt = """
Please write a short professional summary for a software engineer with 3 years of experience in Python and web development.
Keep it to 2-3 sentences.
"""
        
        print("🔄 Sending test prompt to Gemini...")
        response = client.generate(test_prompt)
        
        if response and len(response.strip()) > 10:
            print("✅ Gemini responded successfully!")
            print(f"Response length: {len(response)} characters")
            print(f"Sample response: {response[:100]}...")
            return True
        else:
            print("❌ Gemini returned empty or very short response")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Gemini client: {str(e)}")
        return False

def test_optimizer():
    """Test the resume optimizer with Gemini."""
    print("\nTesting resume optimizer...")
    
    try:
        from optimizer.optimizer import optimize_resume_and_generate_cover_letter
        
        # Sample data
        resume = """
# John Doe
Software Engineer

## Skills
- Python, JavaScript
- Web development
- Database design

## Experience
### Software Engineer | ABC Company
2021-2024
- Developed web applications
- Worked with Python and Django
"""

        job_description = """
We are looking for a Senior Python Developer with experience in:
- Python web frameworks (Django, Flask)
- RESTful API development
- Database design and optimization
- Team collaboration
"""

        prompt_template = """
Optimize this resume for the given job description.
Make it more relevant and highlight matching skills.

Resume:
{resume}

Job Description:
{job_description}

Please provide an optimized resume in markdown format.
"""

        print("🔄 Testing resume optimization...")
        
        # Test the optimizer
        job_info = {
            'title': 'Senior Python Developer',
            'company': 'Test Company',
            'description': job_description
        }
        
        optimized_resume, cover_letter = optimize_resume_and_generate_cover_letter(
            resume, job_description, prompt_template, job_info
        )
        
        if optimized_resume and len(optimized_resume.strip()) > 50:
            print("✅ Resume optimization successful!")
            print(f"Optimized resume length: {len(optimized_resume)} characters")
            print(f"Sample optimized content: {optimized_resume[:150]}...")
            
            if cover_letter:
                print(f"✅ Cover letter generated! Length: {len(cover_letter)} characters")
            
            return True
        else:
            print("❌ Resume optimization failed or returned very short result")
            return False
            
    except Exception as e:
        print(f"❌ Error testing optimizer: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Job Matcher Gemini Integration Test")
    print("=" * 50)
    
    # Test LLM client
    llm_success = test_gemini_client()
    
    # Test optimizer if LLM works
    if llm_success:
        optimizer_success = test_optimizer()
        
        if optimizer_success:
            print("\n🎉 All tests passed! Gemini integration is working correctly.")
        else:
            print("\n⚠️  LLM client works but optimizer has issues.")
    else:
        print("\n❌ LLM client test failed. Please check your API key and setup.")
