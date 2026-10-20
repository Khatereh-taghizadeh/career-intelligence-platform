from scripts.validate_jobs import validate_job


def test_missing_posting_id():
    job = {
        "posting_id": None,
        "title": "Data Engineer"
    }

    result = validate_job(job)

    assert result == ["Missing posting_id"]


def test_valid_posting_id():
    job = {
        "posting_id": "job_123",
        "title": "Data Engineer"
    }

    result = validate_job(job)

    assert result == []

def test_invalid_salary_range():
    job = {
        "posting_id": "job_456",
        "salary_min": 150000,
        "salary_max": 100000
    }

    result = validate_job(job)

    assert result == ["Invalid salary range"]


def test_missing_salary():
    job = {
        "posting_id": "job_789",
        "salary_min": None,
        "salary_max": None
    }

    result = validate_job(job)

    assert result == []




