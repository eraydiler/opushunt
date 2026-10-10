import requests
from bs4 import BeautifulSoup
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import JobRepository
import re
import concurrent.futures


class RelocateMeJobRepository(JobRepository):
    """
    Fetches jobs from Relocate.me
    URL: https://relocate.me
    Great source for jobs explicitly offering relocation packages and visa sponsorship.
    """
    def _fetch_description(self, job_url: str, headers: dict) -> str:
        try:
            res = requests.get(job_url, headers=headers, timeout=10)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                # Relocate.me description usually in a specific div
                desc_div = soup.find("div", class_="job__details")
                if desc_div:
                    return str(desc_div)

                # fallback
                desc_div = soup.find("div", class_="job-description")
                if desc_div:
                    return str(desc_div)
        except Exception:
            pass
        return ""

    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        tags = [t.strip().lower() for t in tag.replace(';', ',').replace('|', ',').split(',') if t.strip()]
        all_jobs = {}
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        for current_tag in tags[:3]:
            print(f"Fetching '{current_tag}' jobs from Relocate.me...")
            url = f"https://relocate.me/search?q={current_tag}"

            try:
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    job_cards = soup.find_all("div", class_="jobs-list__job")

                    def process_card(card):
                        title_div = card.find("div", class_="job__title")
                        if not title_div:
                            return None

                        a_tag = title_div.find("a")
                        if not a_tag:
                            return None

                        link = a_tag["href"]
                        if link.startswith("/"):
                            link = f"https://relocate.me{link}"

                        job_id = link.split("/")[-1]

                        title_b = a_tag.find("b")
                        title = title_b.get_text(strip=True) if title_b else "Unknown"

                        # Location (city) is often after 'in' inside the a_tag
                        a_text = a_tag.get_text(separator=" ", strip=True)
                        city = a_text.split("in ")[-1].strip() if "in " in a_text else ""

                        # Company and Country
                        company_divs = card.find_all("div", class_="job__company")
                        country = "Unknown"
                        company = "Unknown"

                        if len(company_divs) >= 2:
                            country = company_divs[0].get_text(strip=True)
                            company = company_divs[1].get_text(strip=True)
                        elif len(company_divs) == 1:
                            company = company_divs[0].get_text(strip=True)

                        location = f"{city}, {country}".strip(", ")

                        desc_p = card.find("p", class_="job__preview")
                        description = desc_p.get_text(strip=True) if desc_p else ""

                        # Local tag filtering check just to be sure
                        text_to_search = (title + " " + description).lower()
                        matches_tag = False
                        for t in tags:
                            pattern = r'(?<![a-zA-Z0-9_])' + re.escape(t) + r'(?![a-zA-Z0-9_])'
                            if re.search(pattern, text_to_search, re.IGNORECASE):
                                matches_tag = True
                                break

                        if not matches_tag:
                            return None

                        # Fetch full description
                        full_desc = self._fetch_description(link, headers)
                        if full_desc:
                            description = full_desc

                        return Job(
                            id=f"relocateme_{job_id}",
                            company=company,
                            position=title,
                            description=description,
                            url=link,
                            location=location,
                            apply_url=link,
                            date="", # Relocate.me doesn't clearly show date on listing page
                            source="Relocate.me"
                        )

                    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                        results = executor.map(process_card, job_cards)
                        for job in results:
                            if job and job.id not in all_jobs:
                                all_jobs[job.id] = job

            except Exception as e:
                print(f"Error fetching from Relocate.me for '{current_tag}': {e}")

        return list(all_jobs.values())
