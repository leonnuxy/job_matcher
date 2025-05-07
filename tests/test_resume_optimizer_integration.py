"""
Integration test for the resume_optimizer package.

This test demonstrates how to use the resume_optimizer package
to optimize a resume for a specific job description.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add the parent directory to the path so we can import resume_optimizer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resume_optimizer import optimize_resume
from resume_optimizer.optimizer import OptimizerError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_resume_optimization():
    """Test the resume optimization functionality with sample data."""
    try:
        # Load sample resume and job description
        data_dir = Path(__file__).parent / "data"
        
        with open(data_dir / "resume.txt", "r") as f:
            resume_text = f.read()
        
        with open(data_dir / "job_descriptions" / "job_description.txt", "r") as f:
            job_description = f.read()
        
        # Run optimization
        logger.info("Starting resume optimization...")
        result = optimize_resume(resume_text, job_description)
        
        # Log the results
        logger.info(f"Optimization complete. Summary: {result['summary'][:100]}...")
        logger.info(f"Skills to add: {', '.join(result['skills_to_add'])}")
        logger.info(f"Skills to remove: {', '.join(result['skills_to_remove'])}")
        logger.info(f"Number of experience tweaks: {len(result['experience_tweaks'])}")
        
        # Save the results to a file
        output_dir = Path(__file__).parent.parent / "data" / "optimization_results"
        output_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = Path(__file__).stem.split("_")[-1]
        output_file = output_dir / f"resume_optimization_test_{timestamp}.json"
        
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Results saved to {output_file}")
        
        # Test passed if we got here
        return True
    
    except OptimizerError as e:
        logger.error(f"Optimization error: {e}")
        return False
    
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_resume_optimization()
    sys.exit(0 if success else 1)
