import argparse
import pandas as pd
from scripts.resume_matcher import (
    read_resume_pdf,
    extract_skills,
    rank_jobs,
    analyze_skill_gaps,
)
from scripts.skill_prioritizer import prioritize_skills


def main():
    parser = argparse.ArgumentParser(
        description="Career Intelligence Job Search"
    )

    parser.add_argument(
        "--resume",
        required=True,
        help="Path to your resume PDF"
    )

    args = parser.parse_args()

    resume_text = read_resume_pdf(args.resume)
    resume_skills = extract_skills(resume_text)

    print("Resume:", args.resume)
    print("Skills found:", ", ".join(resume_skills))

    jobs = pd.read_csv("data/cleaned_job_postings.csv")

    ranked_jobs = rank_jobs(
        resume_skills,
        jobs,
        seniority="junior",
        country="US",
        work_mode="remote",
    )

    print("\nMatching jobs:", len(ranked_jobs))
    print("\nTop 5 Job Matches:")

    print(
        ranked_jobs[
            ["title", "match_score"]
        ].head(5).to_string(index=False)
    )

    skill_gaps = analyze_skill_gaps(
        resume_skills,
        ranked_jobs
    )

    print("\nTop 10 Missing Skills:")

    print(
        pd.DataFrame(skill_gaps)[
            ["skill", "job_count", "demand_percent"]
        ].head(10).to_string(index=False)
    )

    priorities = prioritize_skills(skill_gaps)

    print("\nTop 10 Learning Priorities:")

    print(
        pd.DataFrame(priorities)[
            [
                "skill",
                "demand_percent",
                "relevance_score",
                "priority_score",
            ]
        ].head(10).to_string(index=False)
    )

if __name__ == "__main__":
    main()