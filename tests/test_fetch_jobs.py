from urllib.error import HTTPError, URLError
from unittest.mock import MagicMock
from scripts.fetch_jobs import fetch_jobs
import json
import pytest
import logging


def test_fetch_jobs_retries_after_network_error(monkeypatch, caplog):
    """Verify that a network failure triggers a retry."""
    
    caplog.set_level(logging.WARNING)
    
    # Track how many times the API is called.
    attempts = 0

    fake_data = {
        "jobs": [
            {"guid": "job-123", "title": "Junior Data Engineer"}
        ]
    }

    def fake_urlopen(request, timeout):
        nonlocal attempts
        attempts += 1

        if attempts == 1:
            raise URLError("Temporary network failure")

        response = MagicMock()
        response.__enter__.return_value = response

        response.read.return_value = json.dumps(fake_data).encode("utf-8")
        return response

    
    monkeypatch.setattr("scripts.fetch_jobs.time.sleep", lambda seconds: None)
    monkeypatch.setattr("scripts.fetch_jobs.urlopen", fake_urlopen)


    result = fetch_jobs()

    assert attempts == 2
    assert result == fake_data
    assert "Network error:" in caplog.text


def test_fetch_jobs_does_not_retry_404(monkeypatch):
    """Verify that HTTP 404 errors are not retried."""

    attempts = 0

    def fake_urlopen(request, timeout):
        nonlocal attempts
        attempts += 1

        raise HTTPError(
            url="https://example.com",
            code=404,
            msg="Not Found",
            hdrs=None,
            fp=None
        )

    monkeypatch.setattr(
        "scripts.fetch_jobs.urlopen",
        fake_urlopen
    )

    # Verify that fetch_jobs raises HTTPError.
    with pytest.raises(HTTPError):
        fetch_jobs()

    # Verify that only one request was made.
    assert attempts == 1


def test_fetch_jobs_retries_503_until_exhausted(monkeypatch, caplog):
    """Verify that HTTP 503 is retried until attempts are exhausted."""

    caplog.set_level(logging.WARNING)
    
    attempts = 0

    def fake_urlopen(request, timeout):
        nonlocal attempts
        attempts += 1

        raise HTTPError(
            url="https://example.com",
            code=503,
            msg="Service Unavailable",
            hdrs=None,
            fp=None
        )

    # Avoid waiting between retries.
    monkeypatch.setattr(
        "scripts.fetch_jobs.time.sleep",
        lambda seconds: None
    )

    # Replace the real API call.
    monkeypatch.setattr(
        "scripts.fetch_jobs.urlopen",
        fake_urlopen
    )

    # Verify that HTTPError is raised after all retries.
    with pytest.raises(HTTPError) as error_info:
        fetch_jobs()

    # Verify that the final error is HTTP 503.
    assert error_info.value.code == 503

    # One initial request + three retries.
    assert attempts == 4
    assert "API request failed:" in caplog.text
    assert caplog.text.count("API request failed:") == 4
