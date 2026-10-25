def validate_api_response(data):
    if not isinstance(data, dict):
        raise ValueError("API response must be a dictionary")

    if "jobs" not in data:
        raise ValueError("API response is missing 'jobs' key")

    if not isinstance(data["jobs"], list):
        raise ValueError("API response 'jobs' must be a list")

    for index, job in enumerate(data["jobs"]):
        if not isinstance(job, dict):
            raise ValueError(
                f"Job at index {index} must be a dictionary"
            )