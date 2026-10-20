from scripts.fetch_jobs import fetch_jobs
from scripts.transform_jobs import transform_job
from scripts.validate_jobs import validate_job
from scripts.load_api_jobs import load_api_jobs
import logging

logger = logging.getLogger(__name__)

def run_pipeline():
    """
    Run the job ingestion pipeline.

    Steps:
    1. Fetch raw job postings from the API.
    2. Extract the list of jobs from the API response.
    3. Transform each job into a standardized format.
    4. Validate each transformed job for data quality issues.
    5. Load job postings into PostgreSQL.

    Note:
        Validation is not yet connected to the loading step.
    """

    # Step 1: Fetch raw job data from the external API.
    data = fetch_jobs()

    # Step 2: Extract the job list.
    # Return an empty list if the "jobs" key is missing.
    jobs = data.get("jobs", [])

    # Step 3: Transform each job into a consistent data structure.
    transformed_jobs = [transform_job(job) for job in jobs]

    # Step 4: Validate each transformed job.
    valid_jobs = []

    # Check each job for data quality errors.
    for job in transformed_jobs:
        errors = validate_job(job)

        # Keep the job only if it passes validation.
        if not errors:
            valid_jobs.append(job)

        # Log validation errors and skip invalid jobs.
        else:
            logger.warning(
                "Skipping invalid job %s: %s",
                job.get("posting_id"),
                errors
            )   

    # Step 5: Load only validated jobs into PostgreSQL.
    inserted_count = load_api_jobs(valid_jobs)

    # Return all transformed jobs for further processing or testing.
    return transformed_jobs