"""
Web application for resume optimization.
"""
import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash
import markdown

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from optimizer.optimize import optimize_resume
from services.utils import save_optimized_resume

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_change_in_production')

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/optimize', methods=['POST'])
def optimize():
    """Handle resume optimization form submission."""
    try:
        # Get form data
        resume_text = request.form.get('resume')
        job_description = request.form.get('job_description')
        
        # Load the prompt template
        with open(os.path.join(parent_dir, 'prompt.txt'), 'r') as f:
            prompt_template = f.read()
            
        # Optimize the resume
        optimized_md = optimize_resume(resume_text, job_description, prompt_template)
        
        # Save the optimized resume
        out_dir = os.path.join(parent_dir, 'data/optimization_results')
        output_path = save_optimized_resume(optimized_md, out_dir)
        
        # Convert markdown to HTML for display
        optimized_html = markdown.markdown(optimized_md)
        
        return render_template('result.html', 
                            optimized_html=optimized_html, 
                            optimized_markdown=optimized_md,
                            file_path=output_path)
    except Exception as e:
        flash(f"Error: {str(e)}", 'danger')
        return redirect(url_for('index'))

def main():
    """Run the Flask server."""
    app.run(host='127.0.0.1', port=5000, debug=True)
    
if __name__ == '__main__':
    main()
