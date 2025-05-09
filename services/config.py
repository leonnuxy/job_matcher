# config.py

import os
from dotenv import load_dotenv

load_dotenv()

USER_AGENT       = os.getenv("USER_AGENT") or (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/91.0.4472.124 Safari/537.36"
)
REQUEST_TIMEOUT  = int(os.getenv("REQUEST_TIMEOUT", "10"))
SIMULATION_MODE  = os.getenv("SIMULATION_MODE", "false").lower() in ("true","1","yes")
GOOGLE_API_KEY   = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID    = os.getenv("GOOGLE_CSE_ID")
RETRY_TOTAL      = int(os.getenv("RETRY_TOTAL", "3"))
RETRY_BACKOFF    = float(os.getenv("RETRY_BACKOFF", "0.5"))
RETRY_STATUSES   = [429, 500, 502, 503, 504]
MIN_DESC_LENGTH  = int(os.getenv("MIN_DESCRIPTION_LENGTH", "50"))

