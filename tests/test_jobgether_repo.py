import types

from src.infrastructure.repositories.jobgether_repo import JobgetherJobRepository


class DummyResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code


def test_jobgether_repo_parses_search_results(monkeypatch):
    html = """
    <html><body>
      <a href="/remote-jobs/ios-developer">iOS Developer 42</a>
      <a href="/remote-jobs/swift-developer">Swift Developer 15</a>
      <a href="/remote-jobs/company-apple">Apple</a>
      <a href="/remote-jobs/full-time">Full time</a>
    </body></html>
    """

    def fake_get(url, headers=None, timeout=None):
        assert "jobgether.com/search-offers" in url
        return DummyResponse(html)

    monkeypatch.setattr("src.infrastructure.repositories.jobgether_repo.requests.get", fake_get)

    repo = JobgetherJobRepository()
    jobs = repo.fetch_jobs("ios")

    assert len(jobs) == 2
    assert jobs[0].position == "iOS Developer"
    assert jobs[0].source == "Jobgether"
    assert jobs[0].url == "https://jobgether.com/remote-jobs/ios-developer"
