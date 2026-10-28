import re
from typing import List

from bs4 import BeautifulSoup
from langdetect import DetectorFactory, LangDetectException, detect_langs

from src.domain.entities import Job, Resume
from src.domain.interfaces import JobRepository, LLMService, ApplicationRepository

DetectorFactory.seed = 0

LANGUAGE_ALIASES = {
    "arabic": "ar",
    "chinese": "zh-cn",
    "danish": "da",
    "dutch": "nl",
    "english": "en",
    "finnish": "fi",
    "french": "fr",
    "german": "de",
    "greek": "el",
    "hindi": "hi",
    "italian": "it",
    "japanese": "ja",
    "korean": "ko",
    "norwegian": "no",
    "norsk": "no",
    "polish": "pl",
    "portuguese": "pt",
    "russian": "ru",
    "spanish": "es",
    "swedish": "sv",
    "turkish": "tr",
    "ukrainian": "uk",
}


def _normalize_language(language: str) -> str:
    value = language.strip().casefold().replace("_", "-")
    if not value:
        return ""

    alias = LANGUAGE_ALIASES.get(value)
    if alias:
        return alias

    code = value.split("-", 1)[0]
    if re.fullmatch(r"[a-z]{2}", code):
        return code

    raise ValueError(
        "Enter a language name (for example English) or a 2-letter code (en)."
    )


def _matches_language(job: Job, language_code: str) -> bool:
    description = BeautifulSoup(job.description or "", "html.parser").get_text(
        " ", strip=True
    )
    text = f"{job.position} {description}".strip()
    if len(text) < 80:
        return False

    try:
        detected_languages = detect_langs(text[:2000])
    except LangDetectException:
        return False

    return any(
        detected.lang.split("-", 1)[0] == language_code.split("-", 1)[0]
        and detected.prob >= 0.75
        for detected in detected_languages
    )


class SearchJobsUseCase:
    def __init__(self, repositories: List[JobRepository]):
        self.repositories = repositories

    def execute(self, tag: str, location: str = "", language: str = "") -> List[Job]:
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

        language_code = _normalize_language(language)
        if language_code:
            all_jobs = [job for job in all_jobs if _matches_language(job, language_code)]

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
