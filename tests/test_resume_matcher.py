import pandas as pd
from scripts.resume_matcher import match_skills, rank_jobs, analyze_skill_gaps


def test_match_skills():
    result = match_skills(
        ["Python", "SQL", "Excel"],
        ["Python", "SQL", "AWS", "Airflow"]
    )

    assert result["match_score"] == 58.82
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

def test_analyze_skill_gaps():
    jobs = pd.DataFrame([
        {"skills": "python|sql|aws"},
        {"skills": "python|aws|airflow"},
        {"skills": "python|sql|airflow"},
    ])

    result = analyze_skill_gaps(["python", "sql"], jobs)

    assert result[0]["skill"] == "aws"
    assert result[0]["job_count"] == 2
    assert result[0]["demand_percent"] == 66.67

    assert result[1]["skill"] == "airflow"
    assert result[1]["job_count"] == 2

def test_weighted_skill_scoring():
    result = match_skills(
        ["sql", "python"],
        ["sql", "python", "excel"]
    )

    assert result["match_score"] == 83.33
    assert result["matched_skills"] == ["python", "sql"]
    assert result["missing_skills"] == ["excel"]
