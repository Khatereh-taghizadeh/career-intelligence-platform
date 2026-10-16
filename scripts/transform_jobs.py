def normalize_seniority(levels):
    return levels[0] if levels else None


def normalize_salary(salary):
    return salary if salary is not None else None


def hourly_to_annual(hourly_salary):
    if hourly_salary is None:
        return None

    return hourly_salary * 40 * 52


