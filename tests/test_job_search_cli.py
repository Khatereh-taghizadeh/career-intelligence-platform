import subprocess
import sys

from reportlab.pdfgen import canvas


def test_job_search_cli(tmp_path):
    resume_path = tmp_path / "test_resume.pdf"

    pdf = canvas.Canvas(str(resume_path))
    pdf.drawString(
        100, 750,
        "Skills: Python, SQL, Docker, AWS"
    )
    pdf.save()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.job_search_cli",
            "--resume",
            str(resume_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    output = result.stdout

    assert "Skills found:" in output
    assert "Matching jobs:" in output
    assert "Top 5 Job Matches:" in output
    assert "Top 10 Missing Skills:" in output
    assert "Top 10 Learning Priorities:" in output


def test_job_search_cli_with_filters(tmp_path):
    resume_path = tmp_path / "test_resume.pdf"

    pdf = canvas.Canvas(str(resume_path))
    pdf.drawString(100, 750, "Skills: Python, SQL, Docker, AWS")
    pdf.save()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.job_search_cli",
            "--resume",
            str(resume_path),
            "--seniority",
            "junior",
            "--country",
            "CA",
            "--work-mode",
            "remote",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Matching jobs: 17" in result.stdout


def test_job_search_cli_no_matches(tmp_path):
    resume_path = tmp_path / "test_resume.pdf"

    pdf = canvas.Canvas(str(resume_path))
    pdf.drawString(100, 750, "Skills: Python, SQL")
    pdf.save()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.job_search_cli",
            "--resume",
            str(resume_path),
            "--country",
            "ZZ",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Matching jobs: 0" in result.stdout
    assert "No jobs found for the selected filters." in result.stdout


def test_job_search_cli_salary_display(tmp_path):
    resume_path = tmp_path / "test_resume.pdf"

    pdf = canvas.Canvas(str(resume_path))
    pdf.drawString(100, 750, "Skills: Python, SQL")
    pdf.save()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.job_search_cli",
            "--resume",
            str(resume_path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    output = result.stdout

    assert "salary_range" in output
    assert "seniority" in output
    assert "match_score" in output
    assert "$" in output


def test_job_search_cli_custom_top(tmp_path):
    resume_path = tmp_path / "test_resume.pdf"

    pdf = canvas.Canvas(str(resume_path))
    pdf.drawString(100, 750, "Skills: Python, SQL, Docker")
    pdf.save()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.job_search_cli",
            "--resume",
            str(resume_path),
            "--top",
            "10",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Top 10 Job Matches:" in result.stdout
    assert "Matching jobs:" in result.stdout

def test_job_search_cli_target_role(tmp_path):
    resume_path = tmp_path / "test_resume.pdf"

    pdf = canvas.Canvas(str(resume_path))
    pdf.drawString(100, 750, "Skills: Python, SQL, Docker")
    pdf.save()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.job_search_cli",
            "--resume",
            str(resume_path),
            "--target-role",
            "data engineer",
            "--top",
            "5",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Top 5 Job Matches:" in result.stdout
    assert "final_score" in result.stdout
    assert "Junior Data Engineer" in result.stdout

def test_job_search_cli_invalid_weights(tmp_path):
    resume_path = tmp_path / "test_resume.pdf"

    pdf = canvas.Canvas(str(resume_path))
    pdf.drawString(100, 750, "Skills: Python, SQL")
    pdf.save()

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.job_search_cli",
            "--resume",
            str(resume_path),
            "--skill-weight",
            "0.8",
            "--title-weight",
            "0.5",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "Ranking weights must sum to 1.0" in result.stderr
