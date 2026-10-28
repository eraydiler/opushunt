import re
from typing import List, Optional
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup, Tag

from src.domain.entities import Job
from src.domain.interfaces import JobRepository


class CognizantJobRepository(JobRepository):
    """Fetches jobs from Cognizant's UK&I careers search pages."""

    base_url = "https://careers.cognizant.com"
    search_url = f"{base_url}/uki-en/jobs/"
    job_path = re.compile(r"^/uki-en/jobs/(\d+)/", re.IGNORECASE)
    max_pages_per_tag = 3

    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        tags = [
            item.strip() for item in re.split(r"[,;|]", tag) if item.strip()
        ][:3] or [""]
        headers = {"User-Agent": "Mozilla/5.0 (compatible; OpusHunt/1.0)"}
        jobs = {}

        for current_tag in tags:
            for page in range(1, self.max_pages_per_tag + 1):
                params = {"pagesize": 10}
                if current_tag:
                    params["keyword"] = current_tag
                if page > 1:
                    params["page"] = page

                try:
                    response = requests.get(
                        self.search_url, params=params, headers=headers, timeout=20
                    )
                    if response.status_code != 200:
                        break
                except requests.RequestException:
                    break

                soup = BeautifulSoup(response.text, "html.parser")
                page_jobs = 0
                for anchor in soup.find_all("a", href=True):
                    source_id = self._job_id(anchor["href"])
                    title = " ".join(anchor.get_text(" ", strip=True).split())
                    if not source_id or not title:
                        continue

                    job_id = f"cognizant_{source_id}"
                    if job_id in jobs:
                        continue

                    job_url = urljoin(self.base_url, anchor["href"])
                    card = self._find_card(anchor)
                    card_text = card.get_text("\n", strip=True) if card else title
                    jobs[job_id] = Job(
                        id=job_id,
                        company="Cognizant",
                        position=title,
                        description=card.get_text(" ", strip=True) if card else title,
                        url=job_url,
                        location=self._extract_location(card, card_text),
                        apply_url=job_url,
                        source="Cognizant",
                    )
                    page_jobs += 1

                if page_jobs == 0:
                    break

        return list(jobs.values())

    def _find_card(self, anchor: Tag) -> Optional[Tag]:
        for parent in anchor.parents:
            if not isinstance(parent, Tag):
                continue
            matching_links = [
                link for link in parent.find_all("a", href=True)
                if self._job_id(link.get("href", ""))
            ]
            if len(matching_links) == 1:
                return parent
        return None

    def _job_id(self, href: str) -> Optional[str]:
        match = self.job_path.match(urlsplit(href).path)
        return match.group(1) if match else None

    def _extract_location(self, card: Optional[Tag], card_text: str) -> str:
        if card:
            location_element = card.find(
                class_=re.compile(r"location|city", re.IGNORECASE)
            )
            if location_element:
                location = " ".join(location_element.get_text(" ", strip=True).split())
                if location:
                    return location

        ignored = {
            "save",
            "digital",
            "technology & engineering",
            "business processes",
            "consulting",
        }
        lines = [line.strip() for line in card_text.splitlines() if line.strip()]
        for line in lines[1:]:
            if line.casefold() not in ignored and line.casefold() != "work from home":
                return line
        return "Unknown"
