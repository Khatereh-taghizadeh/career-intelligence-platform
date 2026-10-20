from scripts.pipeline import run_pipeline

def test_run_pipeline(monkeypatch):
    """Test fetching and transforming job postings."""
    
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


def test_pipeline_skips_invalid_jobs(monkeypatch, caplog):
    """Verify that invalid jobs are excluded from database loading."""

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

