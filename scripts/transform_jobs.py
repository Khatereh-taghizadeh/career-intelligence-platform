from datetime import datetime, timezone
from scripts.clean_job_description import clean_html
from scripts.job_relevance import is_relevant_job


def normalize_seniority(levels):
    return levels[0] if levels else None


def normalize_salary(salary):
    return salary if salary is not None else None


def hourly_to_annual(hourly_salary):
    if hourly_salary is None:
        return None

    return hourly_salary * 40 * 52


def normalize_job_id(job):
    return job.get("guid")


def normalize_posted_date(timestamp):
    if timestamp is None:
        return None

    return datetime.fromtimestamp(
        timestamp, tz=timezone.utc
    ).date()

def normalize_job_title(job):
    return job.get("title")


def normalize_company_name(job):
    return job.get("companyName")


def normalize_remote_status(job):
    title = job.get("title") or ""
    description = job.get("description") or ""

    if "remote" in title.lower():
        return True

    if "100% remote" in description.lower():
        return True

    return None


def transform_job(job):
    return {
        "posting_id": normalize_job_id(job),
        "title": normalize_job_title(job),
        "is_relevant": is_relevant_job(job.get("title")),
        "company_name": normalize_company_name(job),
        "posted_on": normalize_posted_date(job.get("pubDate")),
        "seniority": normalize_seniority(job.get("seniority")),
        "remote": normalize_remote_status(job),
        "salary_min": normalize_salary(job.get("minSalary")),
        "salary_max": normalize_salary(job.get("maxSalary")),
        "salary_currency": job.get("currency"),
        "salary_period": job.get("salaryPeriod"),
        "employment_type": job.get("employmentType"),
        "location_restrictions": job.get("locationRestrictions") or [],
        "description": clean_html(job.get("description")),
    }




