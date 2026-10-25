import pytest
from scripts.validate_api_response import validate_api_response


def test_valid_api_response():
    data = {
        "jobs": [
            {"title": "Junior Data Engineer"}
        ]
    }

    validate_api_response(data)


def test_api_response_must_be_dictionary():
    data = ["job1", "job2"]

    with pytest.raises(ValueError, match="API response must be a dictionary"):
        validate_api_response(data)


def test_api_response_missing_jobs_key():
    data = {"error": "Service unavailable"}

    with pytest.raises(
        ValueError,
        match="API response is missing 'jobs' key"
    ):
        validate_api_response(data)


def test_api_response_jobs_must_be_list():
    data = {"jobs": "invalid data"}

    with pytest.raises(
        ValueError,
        match="API response 'jobs' must be a list"
    ):
        validate_api_response(data)


def test_api_response_job_must_be_dictionary():
    data = {
        "jobs": [
            {"title": "Data Engineer"},
            "invalid job"
        ]
    }

    with pytest.raises(
        ValueError,
        match="Job at index 1 must be a dictionary"
    ):
        validate_api_response(data)
        