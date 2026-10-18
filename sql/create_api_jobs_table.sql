CREATE TABLE IF NOT EXISTS api_job_postings (
    posting_id TEXT PRIMARY KEY
        ,title TEXT NOT NULL
        ,is_relevant BOOLEAN
        ,company_name TEXT
        ,posted_on DATE
        ,seniority TEXT
        ,remote BOOLEAN
        ,salary_min NUMERIC(12, 2)
        ,salary_max NUMERIC(12, 2)
        ,salary_currency VARCHAR(3)
        ,salary_period TEXT
        ,employment_type TEXT
        ,location_restrictions TEXT[]
        ,description TEXT
        );


