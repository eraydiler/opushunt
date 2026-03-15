from abc import ABC, abstractmethod
from typing import List
from .entities import Job, Resume

class JobRepository(ABC):
    @abstractmethod
    def fetch_jobs(self, tag: str) -> List[Job]:
        pass

class LLMService(ABC):
    @abstractmethod
    def generate_cover_letter(self, job: Job, resume: Resume) -> str:
        pass

class ApplicationRepository(ABC):
    @abstractmethod
    def save_application(self, job: Job, status: str):
        pass
    
    @abstractmethod
    def get_applications(self) -> List[dict]:
        pass
