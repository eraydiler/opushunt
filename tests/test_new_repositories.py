from src.infrastructure.repositories.cognizant_repo import CognizantJobRepository
from src.infrastructure.repositories.nav_arbeidsplassen_repo import (
    NavArbeidsplassenJobRepository,
)


class DummyResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code


def test_nav_arbeidsplassen_repo_parses_search_results(monkeypatch):
    page = """
    <html><body>
      <article>
                <a
                    href="https://arbeidsplassen.nav.no/stillinger/stilling/9894d10d-94fe-4883-9b64-81286ec0008c"
                >Senior iOS-utvikler</a>
        <span>Arbeidsgiver</span><span>Example AS</span>
        <span>Sted</span><span>Oslo, Norge</span>
      </article>
    </body></html>
    """

    def fake_get(url, params=None, headers=None, timeout=None):
        assert url == "https://arbeidsplassen.nav.no/stillinger"
        assert params == {"q": "ios"}
        return DummyResponse(page)

    monkeypatch.setattr(
        "src.infrastructure.repositories.nav_arbeidsplassen_repo.requests.get",
        fake_get,
    )

    jobs = NavArbeidsplassenJobRepository().fetch_jobs("ios")

    assert len(jobs) == 1
    assert jobs[0].id == "nav_9894d10d-94fe-4883-9b64-81286ec0008c"
    assert jobs[0].company == "Example AS"
    assert jobs[0].position == "Senior iOS-utvikler"
    assert jobs[0].location == "Oslo, Norge"
    assert jobs[0].source == "NAV Arbeidsplassen"


def test_nav_arbeidsplassen_repo_skips_failed_response(monkeypatch):
    monkeypatch.setattr(
        "src.infrastructure.repositories.nav_arbeidsplassen_repo.requests.get",
        lambda *args, **kwargs: DummyResponse("", status_code=503),
    )

    assert NavArbeidsplassenJobRepository().fetch_jobs("ios") == []


def test_cognizant_repo_parses_and_deduplicates_search_results(monkeypatch):
    page = """
    <html><body>
      <article>
                <a
                    href="https://careers.cognizant.com/uki-en/jobs/00070799231/ios-engineer/"
                >iOS Engineer</a>
        <span class="job-location">Burgess Hill, West Sussex, United Kingdom</span>
        <span>Technology &amp; Engineering</span>
      </article>
    </body></html>
    """
    requested_pages = []

    def fake_get(url, params=None, headers=None, timeout=None):
        requested_pages.append(params.get("page", 1))
        assert params["keyword"] == "ios"
        assert params["pagesize"] == 10
        return DummyResponse(page)

    monkeypatch.setattr(
        "src.infrastructure.repositories.cognizant_repo.requests.get", fake_get
    )

    jobs = CognizantJobRepository().fetch_jobs("ios")

    assert len(jobs) == 1
    assert jobs[0].id == "cognizant_00070799231"
    assert jobs[0].company == "Cognizant"
    assert jobs[0].position == "iOS Engineer"
    assert jobs[0].location == "Burgess Hill, West Sussex, United Kingdom"
    assert jobs[0].source == "Cognizant"
    assert requested_pages == [1, 2]


def test_cognizant_repo_skips_failed_response(monkeypatch):
    monkeypatch.setattr(
        "src.infrastructure.repositories.cognizant_repo.requests.get",
        lambda *args, **kwargs: DummyResponse("", status_code=503),
    )

    assert CognizantJobRepository().fetch_jobs("ios") == []
