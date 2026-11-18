SKILL_RELEVANCE = {
    "airflow": 5,
    "aws": 5,
    "spark": 5,
    "dbt": 5,
    "snowflake": 5,
    "kafka": 5,
    "statistics": 4,
    "tableau": 3,
    "looker": 3,
    "pytorch": 2,
}


def calculate_priority(demand_percent, relevance_score):
    demand_score = min(max(demand_percent, 0), 100) / 100
    relevance_score = min(max(relevance_score, 1), 5) / 5

    priority = (
        demand_score * 0.6
        + relevance_score * 0.4
    )

    return round(priority * 100, 2)


def prioritize_skills(skill_gaps):
    priorities = []

    for gap in skill_gaps:
        skill = gap["skill"]
        demand = gap["demand_percent"]

        relevance = SKILL_RELEVANCE.get(skill, 3)

        priority_score = calculate_priority(
            demand,
            relevance
        )

        priorities.append({
            "skill": skill,
            "job_count": gap["job_count"],
            "demand_percent": demand,
            "relevance_score": relevance,
            "priority_score": priority_score,
        })

    return sorted(
        priorities,
        key=lambda item: item["priority_score"],
        reverse=True
    )
