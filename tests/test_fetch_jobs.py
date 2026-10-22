import json
import logging
import pytest

from urllib.error import HTTPError, URLError
from unittest.mock import MagicMock

from scripts.fetch_jobs import fetch_jobs


def test_fetch_jobs_retries_after_network_error(monkeypatch, caplog):
    """Verify that a network failure triggers a retry."""

    caplog.set_level(logging.WARNING)
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

    monkeypatch.setattr(
        "scripts.fetch_jobs.time.sleep",
        lambda seconds: None
    )

    monkeypatch.setattr(
        "scripts.fetch_jobs.urlopen",
        fake_urlopen
    )

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

    with pytest.raises(HTTPError):
        fetch_jobs()

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

    monkeypatch.setattr(
        "scripts.fetch_jobs.time.sleep",
        lambda seconds: None
    )

    monkeypatch.setattr(
        "scripts.fetch_jobs.urlopen",
        fake_urlopen
    )

    with pytest.raises(HTTPError) as error_info:
        fetch_jobs()

    assert error_info.value.code == 503
    assert attempts == 4
    assert "API request failed:" in caplog.text
    assert caplog.text.count("API request failed:") == 4


def test_fetch_jobs_uses_exponential_backoff(monkeypatch):
    """Verify that retry delays increase exponentially."""

    sleep_calls = []
    attempts = 0
    monkeypatch.setattr(
        "scripts.fetch_jobs.random.uniform",
        lambda a, b: 0.5
    )

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    def fake_urlopen(request, timeout):
        nonlocal attempts
        attempts += 1

        raise URLError("Temporary network failure")

    # Replace real sleep with fake sleep.
    monkeypatch.setattr(
        "scripts.fetch_jobs.time.sleep",
        fake_sleep
    )

    # Replace real API requests with fake failures.
    monkeypatch.setattr(
        "scripts.fetch_jobs.urlopen",
        fake_urlopen
    )

    # Expect an error after all retries.
    with pytest.raises(URLError):
        fetch_jobs()

    # One initial request + three retries.
    assert attempts == 4

    # Verify exponential retry delays.
    assert sleep_calls == [2.5, 4.5, 8.5]


def test_fetch_jobs_respects_retry_after(monkeypatch):
    sleep_calls = []
    attempts = 0

    def fake_urlopen(request, timeout):
        nonlocal attempts
        attempts += 1

        raise HTTPError(
            url="https://example.com",
            code=429,
            msg="Too Many Requests",
            hdrs={"Retry-After": "30"},
            fp=None,
        )

    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr("scripts.fetch_jobs.urlopen", fake_urlopen)
    monkeypatch.setattr("scripts.fetch_jobs.time.sleep", fake_sleep)
    with pytest.raises(HTTPError) as error_info:
        fetch_jobs()

    assert error_info.value.code == 429
    assert attempts == 4
    assert sleep_calls == [30, 30, 30]

def test_fetch_jobs_invalid_retry_after(monkeypatch):
    sleep_calls = []
    attempts = 0

    def fake_urlopen(request, timeout):
        nonlocal attempts
        attempts += 1

        raise HTTPError(
            url="https://example.com",
            code=429,
            msg="Too Many Requests",
            hdrs={"Retry-After": "invalid"},
            fp=None,
        )
    
    def fake_sleep(seconds):
        sleep_calls.append(seconds)

    monkeypatch.setattr(
        "scripts.fetch_jobs.urlopen",
        fake_urlopen
    )

    monkeypatch.setattr(
        "scripts.fetch_jobs.time.sleep",
        fake_sleep
    )

    monkeypatch.setattr(
        "scripts.fetch_jobs.random.uniform",
        lambda a, b: 0.5
    )

    with pytest.raises(HTTPError) as error_info:
        fetch_jobs()

    assert error_info.value.code == 429
    assert attempts == 4
    assert sleep_calls == [2.5, 4.5, 8.5]
