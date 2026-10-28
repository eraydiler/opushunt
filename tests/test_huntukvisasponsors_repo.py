from src.infrastructure.repositories.huntukvisasponsors_repo import (
    HuntUKVisaSponsorsJobRepository,
)


class DummyResponse:
    def __init__(self, text: str, status_code: int = 200):
        self.text = text
        self.status_code = status_code


def test_huntuk_repo_extracts_location_and_full_description(monkeypatch):
    search_page = """
    <div class="grid grid-cols-[minmax(0,1fr)_72px]">
      <div>
        <a href="/job/developer-ios-at-next-test">Developer - iOS</a>
        <a href="/company/next-retail">NEXT RETAIL LIMITED</a>
        <span title="Sponsorship likely">Likely</span>
      </div>
      <span class="hidden truncate sm:block">Leicester, England, United Kingdom</span>
      <a href="/job/developer-ios-at-next-test"><span>Likely</span></a>
      <span class="hidden truncate lg:block">Full-time</span>
    </div>
    """
    detail_page = """
    <main>
      <section>
        <h2>About the role</h2>
        <div class="prose prose-sm max-w-none">
          <p>We are looking for an experienced iOS developer to build mobile
          applications with Swift and collaborate with our product team.</p>
        </div>
      </section>
    </main>
    """

    def fake_get(url, headers=None, timeout=None):
        if url.endswith("/jobs?q=ios"):
            return DummyResponse(search_page)
        return DummyResponse(detail_page)

    monkeypatch.setattr(
        "src.infrastructure.repositories.huntukvisasponsors_repo.requests.get",
        fake_get,
    )

    jobs = HuntUKVisaSponsorsJobRepository().fetch_jobs("ios")

    assert len(jobs) == 1
    assert jobs[0].position == "Developer - iOS"
    assert jobs[0].company == "NEXT RETAIL LIMITED"
    assert jobs[0].location == "Leicester, England, United Kingdom"
    assert "experienced iOS developer" in jobs[0].description
    assert "Leicester" not in jobs[0].description
