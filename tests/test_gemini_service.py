from types import SimpleNamespace

from src.domain.entities import Job, Resume
from src.infrastructure.services import gemini_service
from src.infrastructure.services.gemini_service import GeminiLLMService


class FakeModels:
    def __init__(self, *, error=None, response_text='["job-1"]'):
        self.error = error
        self.response_text = response_text

    def generate_content(self, model, contents):
        if self.error:
            raise self.error
        return SimpleNamespace(text=self.response_text)


class FakeClient:
    def __init__(self, models):
        self.models = models


def make_service(monkeypatch, models):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(
        gemini_service.genai,
        "Client",
        lambda api_key: FakeClient(models),
    )
    return GeminiLLMService()


def test_ai_filter_returns_original_jobs_when_all_models_fail(monkeypatch):
    service = make_service(monkeypatch, FakeModels(error=RuntimeError("API error")))
    jobs = [
        Job(
            id="job-1",
            company="Example",
            position="iOS Engineer",
            description="Swift",
            url="https://example.com/job",
        )
    ]

    result = service.filter_relevant_jobs(jobs, Resume(content="iOS developer"), "ios")

    assert result is jobs


def test_ai_filter_returns_new_list_when_filtering_succeeds(monkeypatch):
    service = make_service(monkeypatch, FakeModels())
    jobs = [
        Job(
            id="job-1",
            company="Example",
            position="iOS Engineer",
            description="Swift",
            url="https://example.com/job",
        )
    ]

    result = service.filter_relevant_jobs(jobs, Resume(content="iOS developer"), "ios")

    assert result == jobs
    assert result is not jobs
