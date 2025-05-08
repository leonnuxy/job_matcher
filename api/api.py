"""
API module for the job_matcher application.
Provides HTTP endpoints for resume optimization.
"""
from fastapi import FastAPI, HTTPException
import sys
import os

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from optimizer.optimize import optimize_resume
from pydantic import BaseModel

app = FastAPI(title="Job Matcher API", 
             description="API for optimizing resumes based on job descriptions",
             version="1.0.0")

class OptimizationRequest(BaseModel):
    resume_text: str
    job_description: str
    prompt_template: str = None

class OptimizationResponse(BaseModel):
    optimized_resume: str

@app.post("/optimize", response_model=OptimizationResponse)
async def optimize(request: OptimizationRequest):
    """
    Optimize a resume based on a job description.
    """
    try:
        # Use default prompt if not provided
        prompt = request.prompt_template
        if not prompt:
            try:
                with open("prompt.txt") as f:
                    prompt = f.read()
            except FileNotFoundError:
                raise HTTPException(status_code=500, detail="Default prompt template not found")
        
        # Generate optimized resume
        optimized_resume = optimize_resume(
            request.resume_text, 
            request.job_description, 
            prompt
        )
        
        return OptimizationResponse(optimized_resume=optimized_resume)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during optimization: {str(e)}")

@app.get("/health")
async def health():
    """
    Health check endpoint.
    """
    return {"status": "healthy"}
