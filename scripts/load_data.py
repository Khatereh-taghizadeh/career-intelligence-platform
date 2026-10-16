
"""Load cleaned job postings from CSV into PostgreSQL."""

import os
from pathlib import Path

import pandas as pd
import psycopg

# Database and input file configuration
DB_NAME = os.getenv("DB_NAME", "career_intelligence")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_ROOT / "data" / "cleaned_job_postings.csv"


# SQL query to insert a job without creating duplicate posting IDs
INSERT_JOB_SQL = """
    INSERT INTO job_postings (
        posting_id,
        posted_on,
        title,
        seniority,
        city,
        country,
        remote,
        salary_min_usd,
        salary_max_usd,
        company_size,
        skills
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (posting_id) DO NOTHING
"""


# Insert job skills without creating duplicate job-skill pairs
INSERT_SKILL_SQL = """
    INSERT INTO job_skills (
        posting_id,
        skill
    )
    VALUES (%s, %s)
    ON CONFLICT (posting_id, skill) DO NOTHING
"""

def connect_db():
    """Create and return a PostgreSQL database connection."""
    return psycopg.connect(f"dbname={DB_NAME}")


def prepare_salary(value):
    """Convert a salary to float, or None if the value is missing."""
    return float(value) if pd.notna(value) else None


def validate_salary_range(salary_min, salary_max):
    """Validate that minimum salary is not greater than maximum salary."""
    if salary_min is not None and salary_max is not None:
        if salary_min > salary_max:
            raise ValueError("Minimum salary cannot exceed maximum salary")

        

def validate_required_fields(df):
    """Check that required fields have no missing values."""
    required_columns = [
        "posting_id",
        "posted_on",
        "title",
        "seniority",
        "city",
        "country",
        "remote",
        "company_size",
        "skills",
    ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column: {column}")

        missing_rows = df[df[column].isna()]

        if not missing_rows.empty:
            if column == "posting_id":
                locations = missing_rows.index.tolist()
                location_label = "row indices"
            else:
                locations = missing_rows["posting_id"].tolist()
                location_label = "posting IDs"

            raise ValueError(
                f"Missing values in {column} for {location_label}: "
                f"{locations}"
            )



def prepare_job_values(row):
    """Prepare one CSV row for a parameterized SQL INSERT."""

    salary_min = prepare_salary(row["salary_min_usd"])
    salary_max = prepare_salary(row["salary_max_usd"])

    validate_salary_range(salary_min, salary_max)

    return (
        row["posting_id"],
        row["posted_on"],
        row["title"],
        row["seniority"],
        row["city"],
        row["country"],
        row["remote"],
        salary_min,
        salary_max,
        row["company_size"],
        "|".join(
            skill
            for posting_id, skill in prepare_skill_values(
                row["posting_id"], row["skills"]
            )
        ),
    )




def prepare_skill_values(posting_id, skills_text):
    """Convert a pipe-separated skill string into job-skill pairs."""

    # Split the skill string and prepare one tuple per skill
    skill_values = []
    seen_skills = set()

    for skill in skills_text.split("|"):
        skill = skill.strip().lower()

        if skill and skill not in seen_skills:
            seen_skills.add(skill)
            skill_values.append((posting_id, skill))

    return skill_values


def load_jobs():
    """Load all CSV jobs into PostgreSQL without inserting duplicates."""

    # Read the cleaned CSV file
    df = pd.read_csv(CSV_PATH)

    # Convert missing values to Python None
    df = df.astype(object).where(pd.notna(df), None)

    # Validate required fields before loading data
    validate_required_fields(df)

    # Stop if posting IDs are missing or duplicated in the source file
    if df["posting_id"].isna().any():
        raise ValueError("CSV contains missing posting IDs.")

    if df["posting_id"].duplicated().any():
        raise ValueError("CSV contains duplicate posting IDs.")

    print("Total CSV rows:", len(df))

    inserted_count = 0

    # Use one connection and one transaction for the entire load
    with connect_db() as db:
        with db.cursor() as cur:

            # Process each job posting
            for row in df.itertuples(index=False, name=None):
                # Convert tuple values back to named columns
                job = dict(zip(df.columns, row))

                # Prepare values, including missing salaries
                job_values = prepare_job_values(job)

                # Insert the job only if its posting ID is new
                cur.execute(INSERT_JOB_SQL, job_values)

                # Count successfully inserted rows
                inserted_count += cur.rowcount

                # Prepare the skills associated with this job
                skill_values = prepare_skill_values(
                    job["posting_id"],
                    job["skills"]
                )

                # Insert each skill without creating duplicate pairs
                for skill_value in skill_values:
                    cur.execute(INSERT_SKILL_SQL, skill_value)


       

        # The connection context commits if no exception occurs

    print("New jobs inserted:", inserted_count)
    print("Existing jobs skipped:", len(df) - inserted_count)
    print("Job loading completed successfully.")


if __name__ == "__main__":
    # Run the loader only when this file is executed directly
    load_jobs()
