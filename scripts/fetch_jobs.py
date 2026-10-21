import json
import logging
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import time

API_URL = "https://himalayas.app/jobs/api/search"
MAX_RETRIES = 3
RETRY_DELAY = 2
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
logger = logging.getLogger(__name__)


def fetch_jobs():
    """Fetch job postings from the Himalayas API."""

    params = {"q": "junior data engineer", "country": "US"}
    url = f"{API_URL}?{urlencode(params)}"

    request = Request(
            url,
            headers={"User-Agent": "CareerIntelligencePlatform/0.1"}
    )

    for attempt in range(MAX_RETRIES + 1):
        try:
            with urlopen(request, timeout=15) as response:
                data = json.load(response)

            return data
        
        except HTTPError as error:
            if error.code not in RETRYABLE_STATUS_CODES:
                raise
            
            logger.warning("API request failed: %s", error)

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

            else:
                raise

        except URLError as error:
            logger.warning("Network error: %s", error)
            
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                raise


