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