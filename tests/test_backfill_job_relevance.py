from unittest.mock import MagicMock, patch
from scripts.backfill_job_relevance import backfill_job_relevance


def test_backfill_with_no_jobs():
    """Return zero when there are no jobs to update."""
    cursor = MagicMock()
    cursor.fetchall.return_value = []
    connection = MagicMock()
    connection.__enter__.return_value.cursor.return_value.__enter__.return_value = cursor

    with patch("scripts.backfill_job_relevance.psycopg.connect", return_value=connection):
        result = backfill_job_relevance()

    assert result == 0


def test_backfill_updates_changed_job():
    """Count a job when its relevance status changes."""
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        ("job-001", "Junior Data Engineer")
    ]
    cursor.rowcount = 1
    connection = MagicMock()
    connection.__enter__.return_value.cursor.return_value.__enter__.return_value = cursor

    with patch("scripts.backfill_job_relevance.psycopg.connect", return_value=connection):
        result = backfill_job_relevance()

    assert result == 1
    assert cursor.execute.call_args_list[-1].args[1] == (True, "job-001", True)