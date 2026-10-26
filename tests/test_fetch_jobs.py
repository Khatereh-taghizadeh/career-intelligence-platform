import json
import logging
import pytest

from urllib.error import HTTPError, URLError
from unittest.mock import MagicMock
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

from scripts.fetch_jobs import fetch_jobs, calculate_backoff_delay, calculate_retry_delay


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


def test_fetch_jobs_caps_retry_after(monkeypatch):
    sleep_calls = []
    attempts = 0

    def fake_urlopen(request, timeout):
        nonlocal attempts
        attempts += 1

        raise HTTPError(
            url="https://example.com",
            code=429,
            msg="Too Many Requests",
            hdrs={"Retry-After": "999999"},
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

    with pytest.raises(HTTPError) as error_info:
        fetch_jobs()

    assert error_info.value.code == 429
    assert attempts == 4
    assert sleep_calls == [60, 60, 60]


def test_fetch_jobs_respects_retry_after_http_date(monkeypatch):
    sleep_calls = []
    attempts = 0

    retry_date = datetime.now(timezone.utc) + timedelta(minutes=5)
    retry_after = format_datetime(retry_date, usegmt=True)

    def fake_urlopen(request, timeout):
        nonlocal attempts
        attempts += 1

        raise HTTPError(
            url="https://example.com",
            code=429,
            msg="Too Many Requests",
            hdrs={"Retry-After": retry_after},
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

    with pytest.raises(HTTPError) as error_info:
        fetch_jobs()

    assert error_info.value.code == 429
    assert attempts == 4
    assert len(sleep_calls) == 3
    assert sleep_calls == [60, 60, 60]


def test_calculate_backoff_delay(monkeypatch):
    monkeypatch.setattr(
        "scripts.fetch_jobs.random.uniform",
        lambda a, b: 0.5
    )

    assert calculate_backoff_delay(0) == 2.5
    assert calculate_backoff_delay(1) == 4.5
    assert calculate_backoff_delay(2) == 8.5


def test_calculate_backoff_delay_cap(monkeypatch):
    monkeypatch.setattr(
        "scripts.fetch_jobs.random.uniform",
        lambda a, b: 0.5
    )

    assert calculate_backoff_delay(10) == 60


def test_calculate_backoff_delay_invalid_type():
    with pytest.raises(TypeError, match="attempt must be an integer"):
        calculate_backoff_delay("three")


def test_calculate_backoff_delay_negative_attempt():
    with pytest.raises(ValueError, match="attempt must be non-negative"):
        calculate_backoff_delay(-2)


def test_calculate_backoff_delay_rejects_boolean():
    with pytest.raises(TypeError, match="attempt must be an integer"):
        calculate_backoff_delay(True)


def test_calculate_retry_delay_numeric():
    error = HTTPError(
        url="https://example.com",
        code=429,
        msg="Too Many Requests",
        hdrs={"Retry-After": "10"},
        fp=None,
    )

    delay = calculate_retry_delay(error, 0)

    assert delay == 10


def test_calculate_retry_delay_numeric_cap():
    error = HTTPError(
        url="https://example.com",
        code=429,
        msg="Too Many Requests",
        hdrs={"Retry-After": "120"},
        fp=None,
    )

    delay = calculate_retry_delay(error, 0)

    assert delay == 60


def test_calculate_retry_delay_past_date():
    error = HTTPError(
        url="https://example.com",
        code=429,
        msg="Too Many Requests",
        hdrs={"Retry-After": "Wed, 21 Oct 2020 07:28:00 GMT"},
        fp=None,
    )

    delay = calculate_retry_delay(error, 0)

    assert delay == 0


def test_calculate_retry_delay_future_date(monkeypatch):
    from datetime import datetime, timezone

    fixed_now = datetime(2026, 10, 24, 12, 0, 0, tzinfo=timezone.utc)
    retry_date = fixed_now + timedelta(seconds=30)

    class FakeDateTime:
        @staticmethod
        def now(tz):
            return fixed_now

    monkeypatch.setattr("scripts.fetch_jobs.datetime", FakeDateTime)

    error = HTTPError(
        url="https://example.com",
        code=429,
        msg="Too Many Requests",
        hdrs={"Retry-After": retry_date.strftime("%a, %d %b %Y %H:%M:%S GMT")},
        fp=None,
    )

    delay = calculate_retry_delay(error, 0)

    assert delay == 30


def test_calculate_retry_delay_invalid_header(monkeypatch):
    monkeypatch.setattr(
        "scripts.fetch_jobs.calculate_backoff_delay",
        lambda attempt: 2.5
    )

    error = HTTPError(
        url="https://example.com",
        code=429,
        msg="Too Many Requests",
        hdrs={"Retry-After": "invalid-date"},
        fp=None,
    )

    delay = calculate_retry_delay(error, 0)

    assert delay == 2.5


def test_calculate_retry_delay_missing_header(monkeypatch):
    monkeypatch.setattr(
        "scripts.fetch_jobs.calculate_backoff_delay",
        lambda attempt: 2.5
    )

    error = HTTPError(
        url="https://example.com",
        code=429,
        msg="Too Many Requests",
        hdrs={},
        fp=None,
    )

    delay = calculate_retry_delay(error, 0)

    assert delay == 2.5


def test_calculate_retry_delay_http_503(monkeypatch):
    monkeypatch.setattr(
        "scripts.fetch_jobs.calculate_backoff_delay",
        lambda attempt: 4.5
    )

    error = HTTPError(
        url="https://example.com",
        code=503,
        msg="Service Unavailable",
        hdrs={"Retry-After": "10"},
        fp=None,
    )

    delay = calculate_retry_delay(error, 1)

    assert delay == 4.5


def test_fetch_jobs_invalid_json(monkeypatch, caplog):
    """Test API response with invalid JSON."""

    fake_response = MagicMock()
    fake_response.read.return_value = b"Service temporarily unavailable"

    fake_response.__enter__.return_value = fake_response

    monkeypatch.setattr(
        "scripts.fetch_jobs.urlopen",
        lambda *args, **kwargs: fake_response
    )
    with pytest.raises(json.JSONDecodeError):
        fetch_jobs()

    assert "Invalid JSON response from API" in caplog.text


def test_fetch_jobs_uses_custom_search_parameters(monkeypatch):
    from urllib.parse import parse_qs, urlparse

    captured_urls = []

    def fake_urlopen(request, timeout):
        captured_urls.append(request.full_url)

        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b'{"jobs": []}'

        return response

    monkeypatch.setattr(
        "scripts.fetch_jobs.urlopen",
        fake_urlopen
    )

    fetch_jobs(query="data analyst", country="US")

    assert len(captured_urls) == 1

    params = parse_qs(urlparse(captured_urls[0]).query)

    assert params["q"] == ["data analyst"]
    assert params["country"] == ["US"]
