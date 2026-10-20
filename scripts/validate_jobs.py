def validate_job(job):
    errors = []

    if not job.get("posting_id"):
        errors.append("Missing posting_id")

    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")

    if (
        salary_min is not None
        and salary_max is not None
        and salary_min > salary_max
    ):
        errors.append("Invalid salary range")

    return errors
