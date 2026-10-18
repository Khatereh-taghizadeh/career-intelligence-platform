import psycopg

from scripts.job_relevance import is_relevant_job

def backfill_job_relevance():
    """Update relevance status for existing job postings."""

    with psycopg.connect("dbname=career_intelligence") as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT posting_id, title
                FROM api_job_postings
                WHERE is_relevant IS NULL
            """)
            jobs = cur.fetchall()

            for posting_id, title in jobs:
                is_relevant = is_relevant_job(title)
                cur.execute(
                    """
                    UPDATE api_job_postings
                    SET is_relevant = %s
                    WHERE posting_id = %s
                      AND is_relevant IS NULL
                    """,
                    (is_relevant, posting_id),
                )
            return len(jobs)

