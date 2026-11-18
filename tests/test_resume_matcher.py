import pandas as pd
from scripts.resume_matcher import match_skills, rank_jobs


def test_match_skills():
    result = match_skills(
        ["Python", "SQL", "Excel"],
        ["Python", "SQL", "AWS", "Airflow"]
    )

    assert result["match_score"] == 50.0
    assert result["matched_skills"] == ["python", "sql"]
    assert result["missing_skills"] == ["airflow", "aws"]


def test_rank_jobs_filters():
    jobs = pd.DataFrame([
        {
            "title": "Junior Data Analyst",
            "seniority": "junior",
            "country": "US",
            "remote": "remote",
            "skills": "python|sql",
        },
        {
            "title": "Senior Data Engineer",
            "seniority": "senior",
            "country": "US",
            "remote": "remote",
            "skills": "python|sql",
        },
        {
            "title": "Junior Data Engineer",
            "seniority": "junior",
            "country": "GB",
            "remote": "remote",
            "skills": "python|sql",
        },
    ])

    result = rank_jobs(
        ["python", "sql"],
        jobs,
        seniority="junior",
        country="US",
        work_mode="remote",
    )

    assert len(result) == 1
    assert result.iloc[0]["title"] == "Junior Data Analyst"
    assert result.iloc[0]["match_score"] == 100.0

