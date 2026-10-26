from scripts.pipeline import run_pipeline
import pytest


def test_run_pipeline(monkeypatch, caplog):
    """Test fetching and transforming job postings."""
    import logging
    caplog.set_level(logging.INFO)

    fake_job = {
        "guid": "job-123",
        "title": "Junior Data Engineer",
        "companyName": "Test Company",
    }

    fake_response = {"jobs": [fake_job]}

    monkeypatch.setattr("scripts.pipeline.fetch_jobs", lambda: fake_response)

     
    monkeypatch.setattr(
        "scripts.pipeline.load_api_jobs",
        lambda jobs: len(jobs),
    )
    result = run_pipeline()

    
    assert len(result) == 1
    
    assert result[0]["posting_id"] == "job-123"

    assert result[0]["company_name"] == "Test Company"


    # Verify pipeline metrics in the logs.
    assert "Fetched jobs: 1" in caplog.text
    assert "Valid jobs: 1" in caplog.text
    assert "Invalid jobs: 0" in caplog.text
    assert "Data quality rate: 100.00%" in caplog.text
    assert "Inserted jobs: 1" in caplog.text
    assert "Pipeline status: SUCCESS" in caplog.text
    assert "Pipeline execution time:" in caplog.text


def test_pipeline_skips_invalid_jobs(monkeypatch, caplog):
    """Verify that invalid jobs are excluded from database loading."""
    import logging
    caplog.set_level(logging.INFO)

    # Step 1: Create one valid job and one invalid job.
    fake_jobs = [
        {
            "guid": "job-123",
            "title": "Data Engineer",
            "companyName": "Company A",
        },
        {
            "guid": None,
            "title": "Python Developer",
            "companyName": "Company B",
        },
    ]

    # Step 2: Mock the API response.
    fake_response = {"jobs": fake_jobs}

    monkeypatch.setattr(
        "scripts.pipeline.fetch_jobs",
        lambda: fake_response
    )

    # Step 3: Capture jobs sent to the database loader.
    loaded_jobs = []

    def fake_load_api_jobs(jobs):
        loaded_jobs.extend(jobs)
        return len(jobs)

    # Step 4: Replace the real database loader.
    monkeypatch.setattr(
        "scripts.pipeline.load_api_jobs",
        fake_load_api_jobs
    )

    # Step 5: Execute the pipeline.
    result = run_pipeline()

    # Step 6: Verify that only the valid job reaches the loader.
    assert len(loaded_jobs) == 1
    assert loaded_jobs[0]["posting_id"] == "job-123"

    # Verify that the pipeline logged the validation error.
    assert "Missing posting_id" in caplog.text

     
    assert "Fetched jobs: 2" in caplog.text
    assert "Valid jobs: 1" in caplog.text
    assert "Invalid jobs: 1" in caplog.text
    assert "Inserted jobs: 1" in caplog.text


def test_pipeline_rejects_invalid_api_response(monkeypatch, caplog):
    """Pipeline should reject an invalid API response."""

    monkeypatch.setattr(
        "scripts.pipeline.fetch_jobs",
        lambda: {"error": "Service unavailable"}
    )

    with pytest.raises(
        ValueError,
        match="API response is missing 'jobs' key"
    ):
        run_pipeline()

    assert "Pipeline failed during API fetching or validation" in caplog.text


def test_pipeline_logs_database_error(monkeypatch, caplog):
    """Test logging when database loading fails."""
    
    import logging
    caplog.set_level(logging.INFO)


    def fake_database_error(jobs):
        raise RuntimeError("Database connection failed")

    monkeypatch.setattr(
        "scripts.pipeline.load_api_jobs",
        fake_database_error
    )

    monkeypatch.setattr(
        "scripts.pipeline.fetch_jobs",
        lambda: {"jobs": []}
    )  

    with pytest.raises(
        RuntimeError,
        match="Database connection failed"
    ):
        run_pipeline() 

    
    assert "Pipeline failed during database loading" in caplog.text
    assert "Pipeline execution time:" in caplog.text
    assert "Pipeline status: FAILED" in caplog.text


def test_pipeline_empty_jobs(monkeypatch, caplog):
    """Test pipeline behavior when API returns zero jobs."""
    import logging
    caplog.set_level(logging.INFO)
    
    fake_response = {"jobs": []}
    monkeypatch.setattr("scripts.pipeline.fetch_jobs", lambda: fake_response)

    monkeypatch.setattr(
        "scripts.pipeline.load_api_jobs",
        lambda jobs: len(jobs),
    )

    result = run_pipeline()

    assert result == []
    assert "Data quality rate: 0.00%" in caplog.text