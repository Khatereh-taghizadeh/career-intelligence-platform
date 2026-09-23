import pandas as pd

# Load raw dataset
df = pd.read_csv("data/data-job-postings.csv")

# Convert posting date to datetime
df["posted_on"] = pd.to_datetime(df["posted_on"])

# Validate salary ranges
invalid_salary = df[
    df["salary_min_usd"] > df["salary_max_usd"]
]

if len(invalid_salary) > 0:
    print(f"Warning: {len(invalid_salary)} invalid salary ranges found.")

# Save cleaned dataset
df.to_csv("data/cleaned_job_postings.csv", index=False)

print(f"Cleaning complete: {len(df)} rows saved.")