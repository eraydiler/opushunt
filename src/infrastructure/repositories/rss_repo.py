from bs4 import BeautifulSoup
import requests
import re
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import JobRepository


class RSSJobRepository(JobRepository):
    """
    A generic RSS/XML feed parser for job boards.
    We use RSS feeds because they are much more stable than HTML scraping
    and many job boards (like WeWorkRemotely, StackOverflow, etc.) provide them.
    """
    def __init__(self, feed_url: str, platform_name: str):
        self.feed_url = feed_url
        self.platform_name = platform_name

    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        print(f"Fetching '{tag}' jobs from {self.platform_name} (RSS)...")

        # Split tags and get the first one for the RSS feed query if it supports it
        # Or we just fetch the feed and filter locally
        tags = [t.strip().lower() for t in tag.replace(';', ',').replace('|', ',').split(',') if t.strip()]

        headers = {"User-Agent": "JobSearchAutomation/1.0"}
        jobs = []

        try:
            response = requests.get(self.feed_url, headers=headers)
            if response.status_code != 200:
                print(f"  -> Failed to fetch RSS from {self.platform_name}")
                return []

            soup = BeautifulSoup(response.content, features="xml")
            items = soup.findAll('item')

            for item in items:
                title = item.title.text if item.title else "Unknown Position"
                description = item.description.text if item.description else ""
                link = item.link.text if item.link else ""

                # WeWorkRemotely specific extraction (Company name is usually before a colon in title)
                company = "Unknown"
                position = title
                if ":" in title:
                    parts = title.split(":", 1)
                    company = parts[0].strip()
                    position = parts[1].strip()

                # Local Filtering based on tags
                text_to_search = (title + " " + description).lower()

                # Check if ANY of the requested tags are in the job description/title strictly
                matches_tag = False
                if not tags:
                    matches_tag = True # No tags provided, match all
                else:
                    for t in tags:
                        pattern = r'(?<![a-zA-Z0-9_])' + re.escape(t) + r'(?![a-zA-Z0-9_])'
                        if re.search(pattern, text_to_search, re.IGNORECASE):
                            matches_tag = True
                            break

                if matches_tag:
                    jobs.append(Job(
                        id=link, # Use link as unique ID
                        company=company,
                        position=position,
                        description=description,
                        url=link,
                        location="Remote",
                        apply_url=link,
                        source=self.platform_name
                    ))

            return jobs

        except Exception as e:
            print(f"Error parsing RSS for {self.platform_name}: {e}")
            return []
