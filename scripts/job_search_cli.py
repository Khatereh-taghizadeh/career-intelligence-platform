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

    parser.add_argument(
        "--seniority",
        default="junior",
        help="Job seniority level (junior, mid, senior)"
    )

    parser.add_argument(
        "--country",
        default="US",
        help="Country code (US, CA, GB, DE)"
    )

    parser.add_argument(
        "--work-mode",
        default="remote",
        choices=["remote", "hybrid", "onsite"],
        help="Work arrangement (remote, hybrid, onsite)"
    )

    parser.add_argument(
        "--top",
        type=int,
        default=5,
        help="Number of top matching jobs to display"
    )

    parser.add_argument(
        "--target-role",
        default="data engineer",
        help="Target job role for ranking relevance"
    )

    args = parser.parse_args()
    if args.top < 1:
        parser.error("--top must be at least 1")

    resume_text = read_resume_pdf(args.resume)
    resume_skills = extract_skills(resume_text)

    print("Resume:", args.resume)
    print("Skills found:", ", ".join(resume_skills))

    jobs = pd.read_csv("data/cleaned_job_postings.csv")

    ranked_jobs = rank_jobs(
        resume_skills,
        jobs,
        seniority=args.seniority,
        country=args.country,
        work_mode=args.work_mode,
        target_role=args.target_role,
    )

    print("\nMatching jobs:", len(ranked_jobs))
    if ranked_jobs.empty:
        print("\nNo jobs found for the selected filters.")
        print("Try changing seniority, country, or work mode.")
        return

    print(f"\nTop {args.top} Job Matches:")

    def format_salary(row):
        minimum = row["salary_min_usd"]
        maximum = row["salary_max_usd"]

        if pd.isna(minimum) or pd.isna(maximum):
            return "Not listed"

        return f"${minimum:,.0f} - ${maximum:,.0f}"

    ranked_jobs["salary_range"] = ranked_jobs.apply(
        format_salary,
        axis=1
    )

    display_columns = [
        "title",
        "seniority",
        "city",
        "country",
        "remote",
        "salary_range",
        "match_score",
        "final_score",
    ]

    print(
        ranked_jobs[display_columns]
        .head(args.top)
        .to_string(index=False, col_space=14)
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