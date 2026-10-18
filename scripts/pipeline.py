from scripts.fetch_jobs import fetch_jobs
from scripts.transform_jobs import transform_job
from scripts.load_api_jobs import load_api_jobs

def run_pipeline():
    """Fetch and transform job postings."""
    data = fetch_jobs()
    jobs = data.get("jobs", [])
    transformed_jobs = [transform_job(job) for job in jobs]
    inserted_count = load_api_jobs(transformed_jobs)
    
    return transformed_jobs

