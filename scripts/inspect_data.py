import pandas as pd

df = pd.read_csv("data/data-job-postings.csv")

print(df.head())
print(df.shape)
print(df.columns)
print(df.dtypes)
print(df.isnull().sum())
print(df.duplicated().sum())

missing_min_salary = df[
    df["salary_min_usd"].isna() & df["salary_max_usd"].notna()
]
print(len(missing_min_salary))


missing_max_salary = df[
    df["salary_max_usd"].isna() & df["salary_min_usd"].notna()
]
print(len(missing_max_salary))


print(df["posting_id"].duplicated().sum())


print(df["seniority"].value_counts())


print(df["remote"].value_counts())


print(df["company_size"].value_counts())


print(df["country"].value_counts())


print(df["skills"].str.split("|").head())


all_skills = df["skills"].str.split("|").explode()
print(all_skills.value_counts())


print(all_skills.value_counts().head(10))

top_10_skills = all_skills.value_counts().head(10)
print(top_10_skills)


top_10_skills.to_csv("reports/top_10_skills.csv")
