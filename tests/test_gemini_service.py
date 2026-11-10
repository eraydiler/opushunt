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
    client_options = {}

    def create_client(*, api_key, http_options):
        client_options["api_key"] = api_key
        client_options["http_options"] = http_options
        return FakeClient(models)

    monkeypatch.setattr(
        gemini_service.genai,
        "Client",
        create_client,
    )
    return GeminiLLMService(), client_options


def test_ai_filter_returns_original_jobs_when_all_models_fail(monkeypatch):
    service, _ = make_service(monkeypatch, FakeModels(error=RuntimeError("API error")))
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
    service, _ = make_service(monkeypatch, FakeModels())
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


def test_gemini_client_uses_bounded_timeout_without_retries(monkeypatch):
    _, client_options = make_service(monkeypatch, FakeModels())

    http_options = client_options["http_options"]
    assert http_options.timeout == 30_000
    assert http_options.retry_options.attempts == 1
