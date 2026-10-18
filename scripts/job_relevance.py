def is_relevant_job(title):
    """Check whether a job title is related to data engineering."""

    if not title:
        return False
    
    keywords = [
        "data engineer",
        "data engineering",
        "etl",
        "talend",
        "data pipeline",
        "business intelligence",
        "bi developer",
        "software engineer - data",
    ]

    return any(keyword in title.lower() for keyword in keywords)


