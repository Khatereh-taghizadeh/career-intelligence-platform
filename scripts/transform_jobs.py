from datetime import datetime, timezone


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

    if "remote" in title.lower():
        return True

    return None



