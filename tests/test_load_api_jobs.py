
from unittest.mock import MagicMock

from scripts.load_api_jobs import load_api_jobs


def test_load_api_jobs_empty_list():
    """An empty list should not connect to the database."""
    assert load_api_jobs([]) == 0


def test_load_api_jobs_inserts_job(monkeypatch):
    """A new job should be inserted successfully."""

    fake_job = {
        "posting_id": "job-123",
        "title": "Junior Data Engineer",
        "is_relevant": True,
        "company_name": "Test Company",
        "posted_on": None,
        "seniority": "Entry-level",
        "remote": True,
        "salary_min": 75400,
        "salary_max": 94300,
        "salary_currency": "USD",
        "salary_period": "annual",
        "employment_type": "Full Time",
        "location_restrictions": ["United States"],
        "description": "Experience with Python and SQL",
    }

    fake_cursor = MagicMock()
    fake_cursor.rowcount = 1

    fake_connection = MagicMock()
    fake_connection.__enter__.return_value = fake_connection

    fake_connection.cursor.return_value.__enter__.return_value = (
        fake_cursor
    )

    monkeypatch.setattr(
        "scripts.load_api_jobs.psycopg.connect",
        lambda *args, **kwargs: fake_connection,
    )

    result = load_api_jobs([fake_job])

    assert result == 1
    fake_cursor.execute.assert_called_once()

    sql, values = fake_cursor.execute.call_args.args
    assert sql.count("%s") == 14
    assert len(values) == 14



    assert "INSERT INTO api_job_postings" in sql
    assert "ON CONFLICT (posting_id) DO NOTHING" in sql
    assert values[0] == "job-123"
    assert values[1] == "Junior Data Engineer"
    assert values[2] is True
    assert values[3] == "Test Company"
    assert values[12] == ["United States"]


def test_load_api_jobs_skips_duplicate(monkeypatch):
    """An existing job should not be inserted again."""

    fake_job = {
        "posting_id": "job-123",
        "title": "Junior Data Engineer",
    }

    fake_cursor = MagicMock()
    fake_cursor.rowcount = 0

    fake_connection = MagicMock()
    fake_connection.__enter__.return_value = fake_connection

    fake_connection.cursor.return_value.__enter__.return_value = (
        fake_cursor
    )

    monkeypatch.setattr(
        "scripts.load_api_jobs.psycopg.connect",
        lambda *args, **kwargs: fake_connection,
    )

    result = load_api_jobs([fake_job])

    assert result == 0
    fake_cursor.execute.assert_called_once()
