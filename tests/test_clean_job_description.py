from scripts.clean_job_description import clean_html


def test_clean_html_removes_tags():
    html = "<p>Python and <strong>SQL</strong></p>"
    result = clean_html(html)

    assert result == "Python and SQL"


def test_clean_html_handles_none():
    result = clean_html(None)

    assert result == ""


def test_clean_html_handles_empty_string():
    result = clean_html("")

    assert result == ""
    