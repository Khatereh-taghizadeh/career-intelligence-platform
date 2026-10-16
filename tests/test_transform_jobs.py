from scripts.transform_jobs import (
    normalize_seniority,
    normalize_salary,
    hourly_to_annual,
    normalize_job_id,
    normalize_posted_date,
    normalize_job_title,
    normalize_company_name,
)


def test_normalize_seniority():
    result = normalize_seniority(["Entry-level"])

    assert result == "Entry-level"


def test_normalize_seniority_empty_list():
    result = normalize_seniority([])

    assert result is None


def test_normalize_salary():
    result = normalize_salary(75400)

    assert result == 75400


def test_normalize_salary_none():
    result = normalize_salary(None)

    assert result is None


def test_hourly_to_annual():
    result = hourly_to_annual(150)

    assert result == 312000


def test_hourly_to_annual_none():
    result = hourly_to_annual(None)

    assert result is None   


def test_normalize_job_id():
    job = {"guid": "https://himalayas.app/jobs/example"}
    result = normalize_job_id(job)
    assert result == "https://himalayas.app/jobs/example"



def test_normalize_job_id_missing():
    job = {"title": "Junior Data Engineer"}
    result = normalize_job_id(job)
    assert result is None


def test_normalize_posted_date():
    result = normalize_posted_date(1791982155)
    assert str(result) == "2026-10-14"


def test_normalize_posted_date_none():
    result = normalize_posted_date(None)
    assert result is None


def test_normalize_job_title():
    job = {"title": "Jr. Data Engineer / Analyst"}
    result = normalize_job_title(job)
    assert result == "Jr. Data Engineer / Analyst"


def test_normalize_company_name():
    job = {"companyName": "Woolpert"}
    result = normalize_company_name(job)
    assert result == "Woolpert"


def test_normalize_remote_status():
    from scripts.transform_jobs import normalize_remote_status

    job = {"title": "Junior Data Engineer - Remote"}

    assert normalize_remote_status(job) is True


def test_normalize_remote_status_unknown():
    from scripts.transform_jobs import normalize_remote_status

    job = {"title": "Junior Data Engineer"}

    assert normalize_remote_status(job) is None   



