def is_relevant_job(title):
    """Check whether a job title is related to data engineering."""

    if not title:
        return False
    
    keywords = [
        "data engineer",
        "data engineering",
        "analytics engineer",
        "etl",
        "talend",
        "data pipeline",
        "business intelligence",
        "bi dev",
        "bi developer",
        "software engineer - data",
    ]

    return any(keyword in title.lower() for keyword in keywords)


