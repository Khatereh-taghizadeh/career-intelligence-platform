from scripts.pipeline import run_pipeline
import pytest
import json
import logging
import sys



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

    monkeypatch.setattr("scripts.pipeline.fetch_jobs", lambda query, country: fake_response)

     
    monkeypatch.setattr(
        "scripts.pipeline.load_api_jobs",
        lambda jobs: len(jobs),
    )
    result = run_pipeline()

    
    assert len(result) == 1
    
    assert result[0]["posting_id"] == "job-123"

    assert result[0]["company_name"] == "Test Company"


    # Verify pipeline metrics in the logs.
    assert '"event": "jobs_fetched", "count": 1' in caplog.text
    assert "Valid jobs: 1" in caplog.text
    assert "Invalid jobs: 0" in caplog.text
    assert "Data quality rate: 100.00%" in caplog.text
    assert "Inserted jobs: 1" in caplog.text
    assert "Pipeline status: SUCCESS" in caplog.text
    assert "Pipeline summary:" in caplog.text
    assert '"quality_rate": 100.0' in caplog.text
    summary_json = next(record.message.split("Pipeline summary: ", 1)[1] for record in caplog.records if record.message.startswith("Pipeline summary: "))
    summary_data = json.loads(summary_json)
    assert summary_data["status"] == "SUCCESS"
    assert summary_data["fetched"] == 1
    assert summary_data["valid"] == 1
    assert summary_data["invalid"] == 0
    assert summary_data["inserted"] == 1
    assert summary_data["quality_rate"] == 100.0
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
        lambda query, country: fake_response
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

     
    assert '"event": "jobs_fetched", "count": 2' in caplog.text
    assert "Valid jobs: 1" in caplog.text
    assert "Invalid jobs: 1" in caplog.text
    assert "Inserted jobs: 1" in caplog.text


def test_pipeline_rejects_invalid_api_response(monkeypatch, caplog):
    """Pipeline should reject an invalid API response."""

    monkeypatch.setattr(
        "scripts.pipeline.fetch_jobs",
        lambda query, country: {"error": "Service unavailable"}
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
        lambda query, country: {"jobs": []}
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
    monkeypatch.setattr("scripts.pipeline.fetch_jobs", lambda query, country: fake_response)

    monkeypatch.setattr(
        "scripts.pipeline.load_api_jobs",
        lambda jobs: len(jobs),
    )

    result = run_pipeline()

    assert result == []
    assert "Data quality rate: 0.00%" in caplog.text
    assert "Data quality below threshold" not in caplog.text


def test_pipeline_warns_on_low_data_quality(monkeypatch, caplog):
    caplog.set_level(logging.WARNING)
    valid_job = {"guid": "job-001", "title": "Data Engineer", "company": "Test Company"}
    invalid_job = {"guid": "", "title": "", "company": ""}
    api_response = {"jobs": [valid_job, invalid_job]}
    monkeypatch.setattr("scripts.pipeline.fetch_jobs", lambda query, country: api_response)
    monkeypatch.setattr("scripts.pipeline.load_api_jobs", lambda jobs: len(jobs))
    
    run_pipeline()

    assert "Data quality below threshold: 50.00% < 80.00%" in caplog.text


def test_pipeline_does_not_warn_on_high_data_quality(monkeypatch, caplog):
    caplog.set_level(logging.WARNING)
    job_1 = {"guid": "job-001", "title": "Data Engineer", "company": "Test Company"}
    job_2 = {"guid": "job-002", "title": "Python Developer", "company": "Example Company"}
    
    api_response = {"jobs": [job_1, job_2]}
    
    monkeypatch.setattr("scripts.pipeline.fetch_jobs", lambda query, country: api_response)
    monkeypatch.setattr("scripts.pipeline.load_api_jobs", lambda jobs: len(jobs))

    run_pipeline()

    assert "Data quality below threshold" not in caplog.text


def test_pipeline_does_not_warn_at_quality_threshold(monkeypatch, caplog):
    
    caplog.set_level(logging.INFO)

    valid_jobs = [{"guid": f"job-{i}", "title": "Data Engineer", "company": "Test Company"} for i in range(1, 5)]
    invalid_job = {"guid": "", "title": "", "company": ""}

    api_response = {"jobs": valid_jobs + [invalid_job]}

    monkeypatch.setattr("scripts.pipeline.fetch_jobs", lambda query, country: api_response)
    monkeypatch.setattr("scripts.pipeline.load_api_jobs", lambda jobs: len(jobs))

    run_pipeline()

    assert "Data quality rate: 80.00%" in caplog.text
    assert "Data quality below threshold" not in caplog.text
    

def test_pipeline_passes_custom_search_parameters(monkeypatch):
    """Verify that pipeline forwards search parameters to fetch_jobs."""

    captured_params = {}

    def fake_fetch_jobs(query, country):
        captured_params["query"] = query
        captured_params["country"] = country
        return {"jobs": []}

    monkeypatch.setattr(
        "scripts.pipeline.fetch_jobs",
        fake_fetch_jobs
    )

    monkeypatch.setattr(
        "scripts.pipeline.load_api_jobs",
        lambda jobs: len(jobs)
    )

    run_pipeline(query="data analyst", country="US")

    assert captured_params == {
        "query": "data analyst",
        "country": "US"
    }


def test_pipeline_cli_passes_custom_arguments(monkeypatch):
    """Verify CLI arguments are forwarded to the pipeline."""

    captured_args = {}

    def fake_run_pipeline(query, country):
        captured_args["query"] = query
        captured_args["country"] = country

    monkeypatch.setattr(
        "scripts.pipeline.run_pipeline",
        fake_run_pipeline
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["pipeline.py", "--query", "data analyst", "--country", "US"]
    )

    from scripts.pipeline import main

    main()

    assert captured_args == {
        "query": "data analyst",
        "country": "US"
    }


def test_pipeline_cli_rejects_empty_query(monkeypatch):
    """Verify CLI rejects an empty job search query."""

    monkeypatch.setattr(
        sys,
        "argv",
        ["pipeline.py", "--query", "", "--country", "US"]
    )

    from scripts.pipeline import main

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2


def test_pipeline_cli_rejects_whitespace_query(monkeypatch):
    """Verify CLI rejects a query containing only spaces."""

    monkeypatch.setattr(
        sys,
        "argv",
        ["pipeline.py", "--query", "   ", "--country", "US"]
    )

    from scripts.pipeline import main

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2


def test_pipeline_cli_rejects_invalid_country(monkeypatch):
    """Verify CLI rejects a country code with three letters."""

    monkeypatch.setattr(
        sys,
        "argv",
        ["pipeline.py", "--query", "data analyst", "--country", "USA"]
    )

    from scripts.pipeline import main

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2


def test_pipeline_cli_rejects_non_ascii_country(monkeypatch):
    """Verify CLI rejects non-ASCII country codes."""

    monkeypatch.setattr(
        sys,
        "argv",
        ["pipeline.py", "--query", "data analyst", "--country", "ای"]
    )

    from scripts.pipeline import main

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 2


def test_pipeline_cli_normalizes_country(monkeypatch):
    """Verify CLI converts country code to uppercase."""

    captured_args = {}

    def fake_run_pipeline(query, country):
        captured_args["query"] = query
        captured_args["country"] = country

    monkeypatch.setattr(
        "scripts.pipeline.run_pipeline",
        fake_run_pipeline
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["pipeline.py", "--query", "data analyst", "--country", "us"]
    )

    from scripts.pipeline import main

    main()

    assert captured_args == {
        "query": "data analyst",
        "country": "US"
    }


def test_pipeline_cli_normalizes_query(monkeypatch):
    """Verify CLI removes surrounding whitespace from query."""

    captured_args = {}

    def fake_run_pipeline(query, country):
        captured_args["query"] = query
        captured_args["country"] = country

    monkeypatch.setattr(
        "scripts.pipeline.run_pipeline",
        fake_run_pipeline
    )

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "pipeline.py",
            "--query",
            "  data engineer  ",
            "--country",
            "US"
        ]
    )

    from scripts.pipeline import main

    main()

    assert captured_args == {
        "query": "data engineer",
        "country": "US"
    }


def test_pipeline_cli_configures_logging(monkeypatch):
    """Verify CLI configures logging at INFO level."""

    import logging
    import scripts.pipeline as pipeline

    captured_config = {}

    def fake_basic_config(**kwargs):
        captured_config.update(kwargs)

    monkeypatch.setattr(
        pipeline.logging,
        "basicConfig",
        fake_basic_config
    )

    monkeypatch.setattr(
        pipeline,
        "run_pipeline",
        lambda query, country: None
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["pipeline.py"]
    )

    pipeline.main()

    assert captured_config["level"] == logging.INFO
    assert "%(asctime)s" in captured_config["format"]
    assert "%(levelname)s" in captured_config["format"]
    assert "%(message)s" in captured_config["format"]


def test_pipeline_logs_jobs_fetched_event(monkeypatch, caplog):
    """Verify pipeline logs the fetched jobs event as JSON."""
    import json
    import logging
    import scripts.pipeline as pipeline

    monkeypatch.setattr(
        pipeline,
        "fetch_jobs",
        lambda query, country: {"jobs": []}
    )
    monkeypatch.setattr(
        pipeline,
        "validate_api_response",
        lambda data: None
    )
    monkeypatch.setattr(
        pipeline,
        "load_api_jobs",
        lambda jobs: 0
    )

    with caplog.at_level(logging.INFO):
        pipeline.run_pipeline()

    messages = [
        record.getMessage()
        for record in caplog.records
        if record.message.startswith("Pipeline event:")
    ]

    assert messages

    event = json.loads(messages[0].split("Pipeline event: ", 1)[1])

    assert event == {
        "event": "jobs_fetched",
        "count": 0
    }
