import psycopg


def load_api_jobs(jobs):
    """Load transformed job postings into PostgreSQL."""

    if not jobs:
        return 0

    insert_sql = """
        INSERT INTO api_job_postings (
            posting_id,
            title,
            is_relevant,
            company_name,
            posted_on,
            seniority,
            remote,
            salary_min,
            salary_max,
            salary_currency,
            salary_period,
            employment_type,
            location_restrictions,
            description
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (posting_id) DO NOTHING
    """

    inserted_count = 0

    with psycopg.connect("dbname=career_intelligence") as conn:
        with conn.cursor() as cur:
            for job in jobs:
                values = (
                    job["posting_id"],
                    job["title"],
                    job.get("is_relevant"),
                    job.get("company_name"),
                    job.get("posted_on"),
                    job.get("seniority"),
                    job.get("remote"),
                    job.get("salary_min"),
                    job.get("salary_max"),
                    job.get("salary_currency"),
                    job.get("salary_period"),
                    job.get("employment_type"),
                    job.get("location_restrictions"),
                    job.get("description"),
                )

                cur.execute(insert_sql, values)
                inserted_count += cur.rowcount

    return inserted_count