import re
from typing import List, Optional
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup, Tag

from src.domain.entities import Job
from src.domain.interfaces import JobRepository


class NavArbeidsplassenJobRepository(JobRepository):
    """Fetches publicly listed jobs from NAV's Arbeidsplassen search pages."""

    base_url = "https://arbeidsplassen.nav.no"
    search_url = f"{base_url}/stillinger"
    job_path = re.compile(r"^/stillinger/stilling/([a-f0-9-]+)", re.IGNORECASE)

    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        tags = [
            item.strip() for item in re.split(r"[,;|]", tag) if item.strip()
        ][:3] or [""]
        headers = {"User-Agent": "Mozilla/5.0 (compatible; OpusHunt/1.0)"}
        jobs = {}

        for current_tag in tags:
            try:
                response = requests.get(
                    self.search_url,
                    params={"q": current_tag} if current_tag else None,
                    headers=headers,
                    timeout=15,
                )
                if response.status_code != 200:
                    continue
            except requests.RequestException:
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            for anchor in soup.find_all("a", href=True):
                job_id = self._job_id(anchor["href"])
                title = " ".join(anchor.get_text(" ", strip=True).split())
                if not job_id or not title:
                    continue

                job_url = urljoin(self.base_url, anchor["href"])
                card = self._find_card(anchor)
                card_text = card.get_text("\n", strip=True) if card else title
                job = Job(
                    id=f"nav_{job_id}",
                    company=self._labeled_value(
                        card_text, ("Arbeidsgiver", "Employer")
                    ) or "Unknown",
                    position=title,
                    description=card.get_text(" ", strip=True) if card else title,
                    url=job_url,
                    location=self._labeled_value(
                        card_text, ("Sted", "Location")
                    ) or "Norway",
                    apply_url=job_url,
                    source="NAV Arbeidsplassen",
                )
                jobs[job.id] = job

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

    def _labeled_value(self, text: str, labels: tuple) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for index, line in enumerate(lines[:-1]):
            if line.casefold().rstrip(":") in {label.casefold() for label in labels}:
                return lines[index + 1]
        return ""
