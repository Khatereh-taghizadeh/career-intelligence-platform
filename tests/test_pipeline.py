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

