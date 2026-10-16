import pandas as pd
import pytest
from scripts.load_data import (
    prepare_skill_values,
    validate_required_fields,
    validate_salary_range,
    prepare_job_values,
    prepare_salary,
)


def test_prepare_skill_values():
        result = prepare_skill_values("TEST001", " SQL | Python | AWS ")
        assert result == [
            ("TEST001", "sql"),
            ("TEST001", "python"),
            ("TEST001", "aws"),
        ]

def test_duplicate_and_empty_skills():
    result = prepare_skill_values("TEST002", "SQL | Python || sql | PYTHON | AWS")
    assert result == [
        ("TEST002", "sql"),
        ("TEST002", "python"),
        ("TEST002", "aws"),
    ]

def test_missing_city():
    df = pd.DataFrame([{
        "posting_id": "TEST003",
        "posted_on": "2026-10-15",
        "title": "Data Engineer",
        "seniority": "Junior",
        "city": None,
        "country": "US",
        "remote": "Remote",
        "company_size": "Small",
        "skills": "sql|python",
    }])

    with pytest.raises(ValueError, match="Missing values in city"):
        validate_required_fields(df)


def test_valid_required_fields():
    df = pd.DataFrame([{
        "posting_id": "TEST004",
        "posted_on": "2026-10-15",
        "title": "Data Engineer",
        "seniority": "Junior",
        "city": "San Jose",
        "country": "US",
        "remote": "Remote",
        "company_size": "Small",
        "skills": "sql|python",
    }])
    validate_required_fields(df)


def test_prepare_salary_valid():
    result = prepare_salary(85000)
    assert result == 85000


def test_prepare_salary_none():
    result = prepare_salary(None)
    assert result is None


def test_prepare_salary_nan():
    result = prepare_salary(float("nan"))
    assert result is None


def test_database_name_environment_variable(monkeypatch):
    import importlib
    import scripts.load_data as load_data

    with monkeypatch.context() as patch:
        patch.setenv("DB_NAME", "test_database")
        importlib.reload(load_data)
        assert load_data.DB_NAME == "test_database"

    importlib.reload(load_data)

         
def test_valid_salary_range():
    result = validate_salary_range(80000, 120000)

    assert result is None



def test_invalid_salary_range():
    with pytest.raises(ValueError, match="Minimum salary cannot exceed maximum salary"):
        validate_salary_range(150000, 90000)



def test_prepare_job_values_invalid_salary():
    row = {
        "posting_id": "TEST005",
        "salary_min_usd": 150000,
        "salary_max_usd": 90000,
    }

    with pytest.raises(
        ValueError,
        match="Minimum salary cannot exceed maximum salary"
    ):
        prepare_job_values(row)



        





