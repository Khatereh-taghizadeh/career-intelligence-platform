from scripts.job_relevance import is_relevant_job


def test_relevant_data_engineer():
    assert is_relevant_job("Junior Data Engineer") is True



def test_irrelevant_job():
    assert is_relevant_job("Junior iOS Developer") is False


def test_relevant_talend_job():
    assert is_relevant_job("Junior Talend Developer") is True


def test_relevant_software_engineer_data():
    assert is_relevant_job("SOFTWARE ENGINEER - DATA | JUNIOR / MID") is True


def test_missing_job_title():
    assert is_relevant_job(None) is False
    

def test_analytics_engineer_is_relevant():
    assert is_relevant_job("Junior Analytics Engineer") is True


def test_bi_dev_focus_is_relevant():
    assert is_relevant_job(
        "Jr Developer – DevOps & BI Dev Focus (REMOTE)"
    ) is True