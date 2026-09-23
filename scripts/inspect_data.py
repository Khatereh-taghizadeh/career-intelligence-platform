import pandas as pd

df = pd.read_csv("data/data-job-postings.csv")

print(df.head())
print(df.shape)
print(df.columns)
print(df.dtypes)
print(df.isnull().sum())
print(df.duplicated().sum())
