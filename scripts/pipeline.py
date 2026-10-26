from scripts.fetch_jobs import fetch_jobs
from scripts.transform_jobs import transform_job
from scripts.validate_jobs import validate_job
from scripts.load_api_jobs import load_api_jobs
from scripts.validate_api_response import validate_api_response
import logging
import time
import json

logger = logging.getLogger(__name__)

DATA_QUALITY_THRESHOLD = 80.0

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
        Only validated jobs are loaded into PostgreSQL.
    """

    start_time = time.perf_counter()

    try:

        # Step 1: Fetch raw job data from the external API.
        try:
            data = fetch_jobs()
            validate_api_response(data)
        except Exception:
            logger.exception("Pipeline failed during API fetching or validation")
            raise

        # Step 2: Extract the job list.
        # Return an empty list if the "jobs" key is missing.
        jobs = data.get("jobs", [])
        fetched_count = len(jobs)

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

        # Step 5:Count valid and invalid job postings.
        valid_count = len(valid_jobs)
        invalid_count = fetched_count - valid_count
        quality_rate = (valid_count / fetched_count * 100) if fetched_count > 0 else 0.0


        # Log pipeline metrics.
        logger.info("Fetched jobs: %s", fetched_count)
        logger.info("Valid jobs: %s", valid_count)
        logger.info("Invalid jobs: %s", invalid_count)
        logger.info("Data quality rate: %.2f%%", quality_rate)

        if fetched_count > 0 and quality_rate < DATA_QUALITY_THRESHOLD:
            logger.warning("Data quality below threshold: %.2f%% < %.2f%%", quality_rate, DATA_QUALITY_THRESHOLD)



        # Step 6: Load valid jobs into PostgreSQL.
        try:
            inserted_count = load_api_jobs(valid_jobs)
        except Exception:
            logger.exception("Pipeline failed during database loading")
            raise


        # Log the number of successfully inserted jobs.
        logger.info("Inserted jobs: %s", inserted_count)
        
        logger.info("Pipeline status: SUCCESS")
        
        summary = {
            "status": "SUCCESS",
            "fetched": fetched_count,
            "valid": valid_count,
            "invalid": invalid_count,
            "inserted": inserted_count,
            "quality_rate": quality_rate,
        }

        logger.info("Pipeline summary: %s", json.dumps(summary))

        # Return all transformed jobs for further processing or testing.
        return transformed_jobs

    except Exception:
        logger.error("Pipeline status: FAILED")
        raise

    finally:
        elapsed_time = time.perf_counter() - start_time
        logger.info("Pipeline execution time: %.2f seconds", elapsed_time)