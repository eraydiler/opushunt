from typing import List
from src.domain.entities import Job, Resume
from src.domain.interfaces import JobRepository, LLMService, ApplicationRepository

class SearchJobsUseCase:
    def __init__(self, repositories: List[JobRepository]):
        self.repositories = repositories

    def execute(self, tag: str, location: str = "") -> List[Job]:
        all_jobs = []
        for repo in self.repositories:
            try:
                jobs = repo.fetch_jobs(tag)
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"Error fetching from repo: {e}")

        normalized_location = location.strip().casefold()
        if normalized_location:
            all_jobs = [
                job
                for job in all_jobs
                if normalized_location in (job.location or "").casefold()
                or "remote" in (job.location or "").casefold()
            ]

        return all_jobs

class AIFilterJobsUseCase:
    def __init__(self, llm_service: LLMService):
        self.service = llm_service

    def execute(self, jobs: List[Job], resume: Resume, tags: str) -> List[Job]:
        # If no LLM service or method doesn't exist, just return jobs
        if not hasattr(self.service, 'filter_relevant_jobs'):
            return jobs
        return self.service.filter_relevant_jobs(jobs, resume, tags)

class GenerateCoverLetterUseCase:
    def __init__(self, llm_service: LLMService):
        self.service = llm_service

    def execute(self, job: Job, resume: Resume) -> str:
        return self.service.generate_cover_letter(job, resume)

class ApplyJobUseCase:
    def __init__(self, repository: ApplicationRepository):
        self.repository = repository

    def execute(self, job: Job, status: str = "Applied"):
        self.repository.save_application(job, status)

    def get_history(self) -> List[dict]:
        return self.repository.get_applications()
