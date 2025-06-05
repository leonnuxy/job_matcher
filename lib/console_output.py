"""
Enhanced console output formatting for the Job Matcher application.
Provides clean, user-friendly console output with progress indicators and structured formatting.
"""

import sys
import time
from typing import List, Dict, Any, Optional
from datetime import datetime


class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Regular colors
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'


class ProgressBar:
    """Simple progress bar for console output."""
    
    def __init__(self, total: int, width: int = 40):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, current: int):
        """Update progress bar to current value."""
        self.current = current
        percent = min(100, int((current / self.total) * 100))
        filled = int((current / self.total) * self.width)
        bar = '●' * filled + '○' * (self.width - filled)
        
        sys.stdout.write(f'\r[{bar}] {percent}%')
        sys.stdout.flush()
    
    def finish(self):
        """Complete the progress bar."""
        self.update(self.total)
        print()  # New line after completion


class ConsoleOutput:
    """Main class for enhanced console output formatting."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.start_time = None
    
    def header(self, title: str, subtitle: str = ""):
        """Print application header."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}🔍 {title}{Colors.RESET}")
        print("=" * (len(title) + 3))
        if subtitle:
            print(f"{Colors.DIM}{subtitle}{Colors.RESET}")
        print()
    
    def section(self, title: str):
        """Print section header."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{title}{Colors.RESET}")
        print("=" * len(title))
    
    def subsection(self, title: str):
        """Print subsection header."""
        print(f"\n{Colors.BOLD}{title}{Colors.RESET}")
        print("-" * len(title))
    
    def info(self, message: str, icon: str = "ℹ️"):
        """Print info message."""
        print(f"{icon} {message}")
    
    def success(self, message: str, icon: str = "✅"):
        """Print success message."""
        print(f"{Colors.GREEN}{icon} {message}{Colors.RESET}")
    
    def warning(self, message: str, icon: str = "⚠️"):
        """Print warning message."""
        print(f"{Colors.YELLOW}{icon} {message}{Colors.RESET}")
    
    def error(self, message: str, icon: str = "❌"):
        """Print error message."""
        print(f"{Colors.RED}{icon} {message}{Colors.RESET}")
    
    def status(self, message: str, end: str = "\n"):
        """Print status message."""
        print(f"{Colors.CYAN}● {message}{Colors.RESET}", end=end)
        sys.stdout.flush()
    
    def progress_start(self, message: str):
        """Start a progress operation."""
        self.status(f"{message}...", end="")
        self.start_time = time.time()
    
    def progress_end(self, success: bool = True, message: str = ""):
        """End a progress operation."""
        if self.start_time:
            elapsed = time.time() - self.start_time
            time_str = f"({elapsed:.1f}s)"
        else:
            time_str = ""
        
        if success:
            icon = f"{Colors.GREEN}✓{Colors.RESET}"
        else:
            icon = f"{Colors.RED}✗{Colors.RESET}"
        
        result_msg = f" {message}" if message else ""
        print(f" {icon}{result_msg} {Colors.DIM}{time_str}{Colors.RESET}")
        self.start_time = None
    
    def job_search_header(self, resume_file: str, skill_count: int, search_terms: List[str]):
        """Print job search initialization info."""
        self.header("JOB MATCHER - Resume Optimization Tool")
        
        self.info(f"{Colors.BOLD}📋 Resume:{Colors.RESET} {resume_file} ({Colors.GREEN}✓ {skill_count} skills extracted{Colors.RESET})")
        self.info(f"{Colors.BOLD}📝 Search Terms:{Colors.RESET} {len(search_terms)} terms loaded")
        
        if self.verbose:
            for i, term in enumerate(search_terms, 1):
                print(f"   {i}. {term}")
    
    def search_progress(self, current_search: int, total_searches: int, search_term: str, progress_percent: int):
        """Display search progress."""
        # Create progress bar
        bar_width = 10
        filled = int((progress_percent / 100) * bar_width)
        bar = '●' * filled + '○' * (bar_width - filled)
        
        print(f"│ [{current_search}/{total_searches}] {search_term:<30} [{bar}] {progress_percent}%")
    
    def search_summary(self, total_jobs: int, high_potential: int, resumes_generated: int, cover_letters_generated: int):
        """Display search results summary."""
        self.section("📊 SEARCH RESULTS SUMMARY")
        self.success(f"Found {total_jobs} total jobs across all searches")
        
        if high_potential > 0:
            self.info(f"🎯 High-potential matches: {Colors.BOLD}{high_potential} jobs{Colors.RESET} (>70% similarity)")
        else:
            self.warning("🎯 No high-potential matches found (>70% similarity)")
        
        if resumes_generated > 0:
            self.info(f"📄 Generated optimized resumes: {Colors.BOLD}{resumes_generated}{Colors.RESET}")
        
        if cover_letters_generated > 0:
            self.info(f"📨 Generated cover letters: {Colors.BOLD}{cover_letters_generated}{Colors.RESET}")
    
    def display_top_jobs(self, jobs: List[Dict[str, Any]], max_display: int = 5):
        """Display top matching jobs in a formatted way."""
        if not jobs:
            self.warning("No jobs found to display")
            return
        
        self.section("🏆 TOP MATCHING JOBS")
        
        for i, job in enumerate(jobs[:max_display], 1):
            # Star rating based on similarity score
            similarity = job.get('similarity_score', 0)
            stars = self._get_star_rating(similarity)
            
            # Job title and company
            title = job.get('title', 'Unknown Title')
            company = job.get('company', 'Unknown Company')
            location = job.get('location', 'Unknown Location')
            ats_score = job.get('ats_score', 0)
            url = job.get('url', '')
            
            print(f"\n[{i}] {stars} {Colors.BOLD}{title}{Colors.RESET} @ {Colors.CYAN}{company}{Colors.RESET}")
            print(f"    📍 {location}  💰 Similarity: {Colors.BOLD}{similarity}%{Colors.RESET}  🤖 ATS: {Colors.BOLD}{ats_score}%{Colors.RESET}")
            
            if url:
                # Truncate long URLs
                display_url = url if len(url) <= 50 else url[:47] + "..."
                print(f"    🔗 {Colors.BLUE}{display_url}{Colors.RESET}")
            
            # Show if resume was generated
            if job.get('resume_file_path'):
                filename = job['resume_file_path'].split('/')[-1]
                print(f"    📄 Resume saved: {Colors.GREEN}{filename}{Colors.RESET}")
    
    def _get_star_rating(self, score: float) -> str:
        """Convert similarity score to star rating."""
        if score >= 90:
            return f"{Colors.YELLOW}⭐⭐⭐⭐⭐{Colors.RESET}"
        elif score >= 70:
            return f"{Colors.YELLOW}⭐⭐⭐⭐{Colors.RESET}○"
        elif score >= 50:
            return f"{Colors.YELLOW}⭐⭐⭐{Colors.RESET}○○"
        elif score >= 30:
            return f"{Colors.YELLOW}⭐⭐{Colors.RESET}○○○"
        elif score >= 10:
            return f"{Colors.YELLOW}⭐{Colors.RESET}○○○○"
        else:
            return "○○○○○"
    
    def files_saved_summary(self, results_file: str, optimization_dir: str):
        """Display summary of saved files."""
        self.section("💾 RESULTS SAVED")
        self.info(f"📊 Full results: {Colors.BOLD}{results_file}{Colors.RESET}")
        self.info(f"📁 Optimized resumes: {Colors.BOLD}{optimization_dir}{Colors.RESET}")
        self.success("🚀 Next step: Review optimized resumes and apply to top matches!")
    
    def processing_job(self, job_num: int, total_jobs: int, job_title: str):
        """Show current job being processed."""
        if self.verbose:
            print(f"   Processing job {job_num}/{total_jobs}: {job_title}")
    
    def optimization_status(self, job_title: str, company: str):
        """Show optimization status for high-potential job."""
        print(f"    🎯 {Colors.YELLOW}Optimizing for:{Colors.RESET} {job_title} @ {company}")


# Global console output instance
console = ConsoleOutput()


def set_verbose(verbose: bool):
    """Set global verbose mode."""
    global console
    console.verbose = verbose


def get_console() -> ConsoleOutput:
    """Get the global console output instance."""
    return console
