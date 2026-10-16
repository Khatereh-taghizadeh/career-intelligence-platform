from scripts.transform_jobs import normalize_seniority, normalize_salary, hourly_to_annual


def test_normalize_seniority():
    result = normalize_seniority(["Entry-level"])

    assert result == "Entry-level"


def test_normalize_seniority_empty_list():
    result = normalize_seniority([])

    assert result is None


def test_normalize_salary():
    result = normalize_salary(75400)

    assert result == 75400


def test_normalize_salary_none():
    result = normalize_salary(None)

    assert result is None


def test_hourly_to_annual():
    result = hourly_to_annual(150)

    assert result == 312000


def test_hourly_to_annual_none():
    result = hourly_to_annual(None)

    assert result is None   




