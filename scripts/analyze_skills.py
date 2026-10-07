import pandas as pd

# Load cleaned dataset
df = pd.read_csv("data/cleaned_job_postings.csv")

# Split skills and put each skill on its own row
all_skills = df["skills"].str.split("|").explode()

# Find the 10 most common skills
top_10_skills = all_skills.value_counts().head(10)

# Save results
top_10_skills.to_csv("reports/top_10_skills.csv")

##print(df["title"].value_counts())


data_engineer_jobs = df[
    df["title"].str.contains("Data Engineer")
]
##print(len(data_engineer_jobs))


data_engineer_skills = data_engineer_jobs["skills"].str.split("|").explode()

top_10_de_skills = data_engineer_skills.value_counts().head(10)
print("Top Data Engineer Skills:")
print(top_10_de_skills)

top_10_de_skills.to_csv("reports/top_10_data_engineer_skills.csv")


junior_de_jobs = df[df["title"] == "Junior Data Engineer"]

junior_de_skills = junior_de_jobs["skills"].str.split("|").explode()

top_10_junior_de_skills = junior_de_skills.value_counts().head(10)
print("Top Junior Data Engineer Skills:")
print(top_10_junior_de_skills)

top_10_junior_de_skills.to_csv("reports/top_10_junior_de_skills.csv")


#sql_percentage = round(
#   (top_10_junior_de_skills["sql"] * 100) / len(junior_de_jobs),
#   2)
#print(f"SQL appears in {sql_percentage}% of Junior Data Engineer postings")


# .index gets the skill names from the Series
for skill in top_10_junior_de_skills.index:
    count = top_10_junior_de_skills[skill]
    percentage = round((count * 100) / len(junior_de_jobs), 2)
    print(f"{skill} appears in {percentage}% of Junior Data Engineer postings")


junior_de_report = pd.DataFrame({
    "skill": top_10_junior_de_skills.index,
    "count": top_10_junior_de_skills.values
})
junior_de_report["percentage"] = (
    (junior_de_report["count"] * 100) / len(junior_de_jobs)
).round(2)
print(junior_de_report)


junior_de_report.to_csv("reports/junior_de_report.csv", index=False)



de_report = pd.DataFrame({
    "skill": top_10_de_skills.index,
    "count": top_10_de_skills.values
})

de_report["percentage"] = (
    (de_report["count"] * 100) / len(data_engineer_jobs)
).round(2)
print(de_report)


de_report.to_csv("reports/de_report.csv", index=False)



comparison_report = pd.merge(
    junior_de_report,
    de_report,
    on="skill",
    suffixes=("_junior", "_all")
)
print(comparison_report)



comparison_report["percentage_difference"] = (
    comparison_report["percentage_junior"] - comparison_report["percentage_all"]
)
print(comparison_report)


comparison_report.to_csv(
    "reports/junior_vs_all_de_skills.csv",
    index=False
)



