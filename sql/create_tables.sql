CREATE TABLE job_postings (
    posting_id VARCHAR(20) PRIMARY KEY,
    posted_on DATE NOT NULL,
    title TEXT NOT NULL,
    seniority VARCHAR(20) NOT NULL,
    city TEXT NOT NULL,
    country CHAR(2) NOT NULL,
    remote VARCHAR(20) NOT NULL,
    salary_min_usd NUMERIC(10,2),
    salary_max_usd NUMERIC(10,2),
    company_size VARCHAR(20) NOT NULL,
    skills TEXT NOT NULL,
    CONSTRAINT check_salary_range CHECK (
        salary_min_usd IS NULL
        OR salary_max_usd IS NULL
        OR salary_min_usd <= salary_max_usd
    )
);