import requests
from bs4 import BeautifulSoup
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import JobRepository
import re
import concurrent.futures


class VisaSponsorJobRepository(JobRepository):
    """
    Fetches jobs from visasponsor.jobs
    URL: https://visasponsor.jobs
    """
    def _fetch_description(self, job_url: str, headers: dict) -> str:
        try:
            res = requests.get(job_url, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                # Look for a specific content area. Usually it's in a main container
                main_div = soup.find("div", class_="container")
                if main_div:
                    # try to find the specific content div
                    content_divs = main_div.find_all("div")
                    for d in content_divs:
                        # find div that has the text of description
                        if len(d.get_text(strip=True)) > 200:
                            return str(d)
                    return str(main_div)
        except Exception:
            pass
        return ""

    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        tags = [t.strip().lower() for t in tag.replace(';', ',').replace('|', ',').split(',') if t.strip()]
        all_jobs = {}
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        print(f"Fetching jobs from visasponsor.jobs...")

        # They don't have a direct search API by keyword, so we'll just fetch recent jobs and filter locally
        # Fetching first 2 pages
        for page in range(2):
            url = f"https://visasponsor.jobs/api/jobs?page={page}"
            try:
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    job_links = soup.find_all("a", href=lambda h: h and h.startswith("/api/jobs/") and len(h.split("/")) > 3)

                    def process_link(a_tag):
                        link = a_tag["href"]
                        if link.startswith("/"):
                            link = f"https://visasponsor.jobs{link}"

                        job_id = link.split("/")[5] if len(link.split("/")) > 5 else link.split("/")[-1]

                        texts = [t.strip() for t in a_tag.get_text(separator="|", strip=True).split("|") if t.strip()]

                        title = "Unknown"
                        company = "Unknown"
                        location = "Unknown"
                        date = ""

                        if len(texts) >= 5:
                            title = texts[0]
                            company = texts[1]
                            location = f"{texts[2]} {texts[3]} {texts[4]}".replace(",", "").strip()
                            date = texts[-1]
                        elif len(texts) >= 2:
                            title = texts[0]
                            company = texts[1]

                        # Strict local filtering
                        text_to_search = (title + " " + company).lower()
                        matches_tag = False
                        if not tags:
                            matches_tag = True
                        else:
                            for t in tags:
                                pattern = r'(?<![a-zA-Z0-9_])' + re.escape(t) + r'(?![a-zA-Z0-9_])'
                                if re.search(pattern, text_to_search, re.IGNORECASE):
                                    matches_tag = True
                                    break

                        if not matches_tag:
                            return None

                        # Fetch full description
                        description = self._fetch_description(link, headers)

                        return Job(
                            id=f"visasponsor_{job_id}",
                            company=company,
                            position=title,
                            description=description,
                            url=link,
                            location=location,
                            apply_url=link,
                            date=date,
                            source="VisaSponsor.jobs"
                        )

                    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                        results = executor.map(process_link, job_links)
                        for job in results:
                            if job and job.id not in all_jobs:
                                all_jobs[job.id] = job

            except Exception as e:
                print(f"Error fetching from visasponsor.jobs page {page}: {e}")

        return list(all_jobs.values())
