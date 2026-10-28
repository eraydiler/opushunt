from src.domain.entities import Job, Resume
from src.application.use_cases import SearchJobsUseCase, AIFilterJobsUseCase


# Mock Repositories and Services for testing
class MockJobRepository:
    def fetch_jobs(self, tag: str):
        if tag == "ios":
            return [Job(id="1", company="Apple", position="iOS Engineer", description="Swift", url="url")]
        return []


class StaticJobRepository:
    def __init__(self, jobs):
        self.jobs = jobs

    def fetch_jobs(self, tag: str):
        return self.jobs


class MockLLMService:
    def filter_relevant_jobs(self, jobs, resume, tags):
        # Simply return the first job as "relevant"
        return [jobs[0]] if jobs else []


def test_search_jobs_use_case():
    repo1 = MockJobRepository()
    repo2 = MockJobRepository()

    use_case = SearchJobsUseCase(repositories=[repo1, repo2])
    results = use_case.execute("ios")

    # Should get results from both repos (2 total)
    assert len(results) == 2
    assert results[0].company == "Apple"


def test_search_jobs_filters_location_across_repositories_and_keeps_remote():
    london_job = Job(
        id="london", company="Company A", position="iOS Engineer", description="Swift",
        url="london-url",
        location="London, UK",
    )
    oslo_job = Job(
        id="oslo", company="Company B", position="iOS Engineer", description="Swift",
        url="oslo-url",
        location="Oslo, Norway",
    )
    remote_job = Job(
        id="remote", company="Company C", position="iOS Engineer", description="Swift",
        url="remote-url",
        location="Remote - United States",
    )
    use_case = SearchJobsUseCase(
        repositories=[
            StaticJobRepository([london_job]),
            StaticJobRepository([oslo_job, remote_job]),
        ]
    )

    results = use_case.execute("ios", location="lOnDoN")

    assert [job.id for job in results] == ["london", "remote"]


def test_search_jobs_without_location_keeps_all_results():
    jobs = [
        Job(
            id="london", company="Company A", position="iOS Engineer",
            description="Swift", url="london-url", location="London, UK",
        ),
        Job(
            id="oslo", company="Company B", position="iOS Engineer",
            description="Swift", url="oslo-url", location="Oslo, Norway",
        ),
    ]
    use_case = SearchJobsUseCase(repositories=[StaticJobRepository(jobs)])

    assert use_case.execute("ios") == jobs


def test_ai_filter_use_case():
    llm = MockLLMService()
    use_case = AIFilterJobsUseCase(llm_service=llm)

    jobs = [
        Job(id="1", company="Apple", position="iOS", description="Desc", url="url"),
        Job(id="2", company="Google", position="Android", description="Desc", url="url")
    ]
    resume = Resume(content="iOS dev")

    filtered = use_case.execute(jobs, resume, "ios")

    # Based on our mock, it should only return the first job
    assert len(filtered) == 1
    assert filtered[0].company == "Apple"
