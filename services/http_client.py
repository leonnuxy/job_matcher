# http_client.py

"""
HTTP client with retry logic for the job_matcher service.
"""
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config import USER_AGENT, REQUEST_TIMEOUT, RETRY_TOTAL, RETRY_BACKOFF, RETRY_STATUSES

# Shared, retried session
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
    headers = headers or {"User-Agent": USER_AGENT}
    timeout = timeout or REQUEST_TIMEOUT
    try:
        resp = SESSION.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp
    except Exception as e:
        logging.debug(f"fetch_url error for {url}: {e}")
        return None
