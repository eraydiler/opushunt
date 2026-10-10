import requests
import xml.etree.ElementTree as ET
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import JobRepository
import re


class SwissDevJobsRepository(JobRepository):
    """
    Fetches jobs from swissdevjobs.ch via their XML feed.
    URL: https://swissdevjobs.ch/job_feed.xml
    """
    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        tags = [t.strip().lower() for t in tag.replace(';', ',').replace('|', ',').split(',') if t.strip()]
        all_jobs = {}
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        print(f"Fetching jobs from swissdevjobs.ch (XML Feed)...")

        url = "https://swissdevjobs.ch/job_feed.xml"
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                # Use built-in xml.etree.ElementTree instead of lxml/bs4 xml to avoid dependency issues
                root = ET.fromstring(response.content)

                # SwissDevJobs custom XML structure: <jobs> -> <job>
                for job_node in root.findall('job'):
                    title_elem = job_node.find('title')
                    if title_elem is None:
                        title_elem = job_node.find('name')

                    link_elem = job_node.find('url')
                    if link_elem is None:
                        link_elem = job_node.find('link')

                    desc_elem = job_node.find('description')
                    company_elem = job_node.find('company')
                    if company_elem is None:
                        company_elem = job_node.find('company-name')

                    loc_elem = job_node.find('city')
                    if loc_elem is None:
                        loc_elem = job_node.find('location')

                    date_elem = job_node.find('pubdate')
                    id_elem = job_node.find('id')

                    if title_elem is None or link_elem is None:
                        continue

                    title = title_elem.text or ""
                    link = link_elem.text or ""
                    description = desc_elem.text if desc_elem is not None else ""
                    company = company_elem.text if company_elem is not None else "Unknown"
                    location = loc_elem.text if loc_elem is not None else "Switzerland"
                    date = date_elem.text if date_elem is not None else ""

                    # Ensure valid strings
                    title = title.strip()
                    company = company.strip()

                    # Local tag filtering
                    text_to_search = (title + " " + description).lower()
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
                        continue

                    job_id = ""
                    if id_elem is not None and id_elem.text:
                        job_id = id_elem.text
                    else:
                        job_id = link.split("/")[-1] if "/" in link else link

                    if job_id not in all_jobs:
                        all_jobs[job_id] = Job(
                            id=f"swissdevjobs_{job_id}",
                            company=company,
                            position=title,
                            description=description,
                            url=link,
                            location=location,
                            apply_url=link,
                            date=date,
                            source="SwissDevJobs"
                        )

        except Exception as e:
            print(f"Error fetching from swissdevjobs.ch: {e}")

        return list(all_jobs.values())