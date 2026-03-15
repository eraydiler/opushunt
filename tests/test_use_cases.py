import pytest
from src.domain.entities import Job, Resume
from src.application.use_cases import SearchJobsUseCase, AIFilterJobsUseCase

# Mock Repositories and Services for testing
class MockJobRepository:
    def fetch_jobs(self, tag: str):
        if tag == "ios":
            return [Job(id="1", company="Apple", position="iOS Engineer", description="Swift", url="url")]
        return []

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
