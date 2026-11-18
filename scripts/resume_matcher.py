import re
from pypdf import PdfReader


def match_skills(resume_skills, job_skills):
    resume_set = {skill.lower().strip() for skill in resume_skills}
    job_set = {skill.lower().strip() for skill in job_skills}

    matched = sorted(resume_set & job_set)
    missing = sorted(job_set - resume_set)

    score = (
        round(len(matched) / len(job_set) * 100, 2)
        if job_set else 0.0
    )

    return {
        "match_score": score,
        "matched_skills": matched,
        "missing_skills": missing
    }


SKILL_KEYWORDS = [
    "python",
    "sql",
    "postgresql",
    "excel",
    "aws",
    "airflow",
    "pandas",
    "numpy",
    "docker",
    "git",
    "tableau",
    "power bi",
]


def extract_skills(text):
    text = text.lower()

    return sorted([
        skill
        for skill in SKILL_KEYWORDS
        if re.search(r"\b" + re.escape(skill) + r"\b", text)
    ])

def read_resume_pdf(file_path):
    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n".join(pages)


def rank_jobs(
    resume_skills,
    jobs,
    seniority="junior",
    country="US",
    work_mode=None,
):
    filtered_jobs = jobs.copy()

    if seniority:
        filtered_jobs = filtered_jobs[
            filtered_jobs["seniority"].str.lower() == seniority.lower()
        ]

    if country:
        filtered_jobs = filtered_jobs[
            filtered_jobs["country"].str.upper() == country.upper()
        ]

    if work_mode:
        filtered_jobs = filtered_jobs[
            filtered_jobs["remote"].str.lower() == work_mode.lower()
        ]

    filtered_jobs["match_score"] = filtered_jobs["skills"].apply(
        lambda skills: match_skills(
            resume_skills,
            str(skills).split("|")
        )["match_score"]
    )

    return filtered_jobs.sort_values(
        "match_score",
        ascending=False
    )
