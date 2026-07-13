import re
from typing import List

import requests
from bs4 import BeautifulSoup

from src.domain.entities import Job
from src.domain.interfaces import JobRepository


class JobgetherJobRepository(JobRepository):
    """Fetches jobs from Jobgether search pages.

    Jobgether exposes search results on public pages such as
    https://jobgether.com/search-offers?keyword=ios. The page contains links
    to remote-job categories and similar-role pages, so we parse the visible
    text and hrefs conservatively and only return entries that look like real
    job/category links.
    """

    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        tags = [t.strip().lower() for t in tag.replace(";", ",").replace("|", ",").split(",") if t.strip()]
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://jobgether.com/",
        }

        try:
            url = "https://jobgether.com/search-offers"
            if tags:
                url = f"{url}?keyword={tags[0]}"
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code != 200:
                return []
        except Exception:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        jobs = []
        seen = set()

        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href", "")
            text = " ".join(anchor.get_text(" ", strip=True).split())
            if not href or not text:
                continue

            if not href.startswith("http"):
                href = f"https://jobgether.com{href}" if href.startswith("/") else href

            if not href.startswith("https://jobgether.com"):
                continue

            if "/remote-jobs/" not in href:
                continue

            if any(token in href.lower() for token in ["company-", "full-time", "part-time", "view-similar"]):
                continue

            title = self._clean_title(text)
            if not title:
                continue

            job_id = href
            if job_id in seen:
                continue
            seen.add(job_id)

            jobs.append(
                Job(
                    id=f"jobgether_{job_id}",
                    company="Jobgether",
                    position=title,
                    description=f"Remote job on Jobgether matching: {title}",
                    url=href,
                    location="Remote",
                    apply_url=href,
                    date=None,
                    source="Jobgether",
                )
            )

        return jobs[:15]

    def _clean_title(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text).strip()
        if not text:
            return ""
        text = re.sub(r"\s*\d+\s*$", "", text)
        if text.lower().startswith("view similar jobs"):
            return ""
        return text

    def _matches_tags(self, title: str, tags: List[str]) -> bool:
        if not tags:
            return True
        title_lower = title.lower()
        return any(re.search(rf"(?<![a-zA-Z0-9_]){re.escape(tag)}(?![a-zA-Z0-9_])", title_lower) for tag in tags)
