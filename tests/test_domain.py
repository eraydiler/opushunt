from src.domain.entities import Job, Resume


def test_job_creation():
    job = Job(
        id="1",
        company="Apple",
        position="iOS Developer",
        description="Swift and SwiftUI experience needed.",
        url="http://apple.com/jobs",
        location="Cupertino",
        apply_url="http://apple.com/apply",
        date="2024-01-01",
        source="Direct"
    )
    assert job.id == "1"
    assert job.company == "Apple"
    assert job.location == "Cupertino"
    assert job.source == "Direct"


def test_resume_creation():
    resume = Resume(content="I am a great iOS Developer.")
    assert resume.content == "I am a great iOS Developer."
