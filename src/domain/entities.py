from dataclasses import dataclass
from typing import Optional

@dataclass
class Job:
    id: str
    company: str
    position: str
    description: str
    url: str
    location: str = "Remote"
    apply_url: Optional[str] = None
    date: Optional[str] = None

@dataclass
class Resume:
    content: str
