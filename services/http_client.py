
"""
HTTP client with simple fetch functionality for the job_matcher service.
"""
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config import USER_AGENT, REQUEST_TIMEOUT, RETRY_TOTAL, RETRY_BACKOFF, RETRY_STATUSES

# For backwards compatibility with existing code
# Create a session with retry logic but don't use it in fetch_url
def create_session() -> requests.Session:
    retry = Retry(
        total=RETRY_TOTAL,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=RETRY_STATUSES
    )
    sess = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)
    sess.mount("http://", adapter)
    sess.mount("https://", adapter)
    return sess

SESSION = create_session()

def fetch_url(url: str, headers: dict = None, timeout: int = None):
    """
    Fetch a URL and return the response object, or None if the request fails.
    
    Args:
        url: The URL to fetch
        headers: Optional headers dictionary (defaults to using USER_AGENT)
        timeout: Optional request timeout in seconds
        
    Returns:
        Response object if successful, None otherwise
    """
    headers = headers or {"User-Agent": USER_AGENT}
    timeout = timeout or REQUEST_TIMEOUT
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp
    except Exception as e:
        logging.debug(f"fetch_url error for {url}: {e}")
        return None
