import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://himalayas.app/jobs/api/search"


def fetch_jobs():
    """Fetch job postings from the Himalayas API."""

    params = {"q": "junior data engineer", "country": "US"}
    url = f"{API_URL}?{urlencode(params)}"

    request = Request(
            url,
            headers={"User-Agent": "CareerIntelligencePlatform/0.1"}
    )

    with urlopen(request, timeout=15) as response:
        data = json.load(response)

    return data

