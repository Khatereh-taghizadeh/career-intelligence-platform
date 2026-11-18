import re
from pypdf import PdfReader
from collections import Counter

SKILL_WEIGHTS = {
    "sql": 5,
    "python": 5,
    "statistics": 4,
    "postgresql": 4,
    "aws": 4,
    "docker": 3,
    "airflow": 3,
    "excel": 2,
}


def match_skills(resume_skills, job_skills):
    resume_set = {skill.lower().strip() for skill in resume_skills}
    job_set = {skill.lower().strip() for skill in job_skills}

    matched = sorted(resume_set & job_set)
    missing = sorted(job_set - resume_set)

    total_weight = sum(
        SKILL_WEIGHTS.get(skill, 1)
        for skill in job_set
    )

    matched_weight = sum(
        SKILL_WEIGHTS.get(skill, 1)
        for skill in matched
    )

    score = (
        round(matched_weight / total_weight * 100, 2)
        if total_weight else 0.0
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


def analyze_skill_gaps(resume_skills, ranked_jobs):
    counter = Counter()

    for skills in ranked_jobs["skills"].dropna():
        job_skills = skills.split("|")

        result = match_skills(
            resume_skills,
            job_skills
        )

        counter.update(result["missing_skills"])

    return [
        {
            "skill": skill,
            "job_count": count,
            "demand_percent": round(
                count / len(ranked_jobs) * 100, 2
            )
        }
        for skill, count in counter.most_common()
    ]
