-- Count job postings by seniority level
SELECT
    seniority,
    COUNT(*) AS job_count
FROM job_postings
GROUP BY seniority
ORDER BY job_count DESC;


-- Count job postings by work arrangement
SELECT
    remote,
    COUNT(*) AS job_count
FROM job_postings
GROUP BY remote
ORDER BY job_count DESC;


-- Count job postings by seniority and work arrangement
SELECT
    seniority,
    remote,
    COUNT(*) AS job_count
FROM job_postings
GROUP BY seniority, remote
ORDER BY seniority, job_count DESC;



--What are the 10 most common job titles in the dataset?
SELECT
    title,
    COUNT(*) AS job_count             --Why title? Because that's the column we're trying to analyze.
FROM job_postings           --COUNT(*) will count the rows, and AS job_count gives that result a readable column name
GROUP BY title         --GROUP BY title → put identical titles together → COUNT(*) → count the rows in each group
ORDER BY job_count DESC
LIMIT 10;


-- Average salary range
SELECT
    ROUND(AVG(salary_min_usd), 2) AS avg_min_salary,
    ROUND(AVG(salary_max_usd), 2) AS avg_max_salary     --ROUND(value, 2) means round the number to 2 decimal places.
FROM job_postings;


-- Average salary range by seniority level
SELECT
    seniority,
    ROUND(AVG(salary_min_usd), 2) AS avg_min_salary,
    ROUND(AVG(salary_max_usd), 2) AS avg_max_salary
FROM job_postings
GROUP BY seniority
ORDER BY avg_min_salary DESC;

