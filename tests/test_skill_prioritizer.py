from scripts.skill_prioritizer import (
    calculate_priority,
    prioritize_skills,
)


def test_calculate_priority():
    assert calculate_priority(21.57, 5) == 52.94


def test_prioritize_skills():
    gaps = [
        {
            "skill": "tableau",
            "job_count": 24,
            "demand_percent": 23.53,
        },
        {
            "skill": "airflow",
            "job_count": 22,
            "demand_percent": 21.57,
        },
    ]

    result = prioritize_skills(gaps)

    assert result[0]["skill"] == "airflow"
    assert result[0]["priority_score"] == 52.94
    assert result[1]["skill"] == "tableau"