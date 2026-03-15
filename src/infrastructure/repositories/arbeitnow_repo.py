import requests
import re
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import JobRepository

class ArbeitnowJobRepository(JobRepository):
    """
    Fetches jobs from Arbeitnow API.
    URL: https://www.arbeitnow.com/api/job-board-api
    Good for Europe & Remote. No API Key required.
    """
    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        # Arbeitnow API doesn't have a direct search query parameter in the free version
        # So we fetch the latest page and filter locally.
        
        tags = [t.strip().lower() for t in tag.replace(';', ',').replace('|', ',').split(',') if t.strip()]
        all_jobs = {}
        headers = {"User-Agent": "JobSearchAutomation/1.0"}
        
        print(f"Fetching jobs from Arbeitnow...")
        url = "https://www.arbeitnow.com/api/job-board-api"
        
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                raw_jobs = data.get('data', [])
                
                for item in raw_jobs:
                    title = item.get('title', '')
                    description = item.get('description', '')
                    text_to_search = (title + " " + description).lower()
                    
                    # Check if it matches tags strictly (whole word matching)
                    matches_tag = False
                    if not tags:
                        matches_tag = True
                    else:
                        for t in tags:
                            pattern = r'(?<![a-zA-Z0-9_])' + re.escape(t) + r'(?![a-zA-Z0-9_])'
                            if re.search(pattern, text_to_search, re.IGNORECASE):
                                matches_tag = True
                                break
                                
                    if matches_tag:
                        job_id = str(item.get('slug', ''))
                        if job_id not in all_jobs:
                            all_jobs[job_id] = Job(
                                id=f"arbeitnow_{job_id}",
                                company=item.get('company_name', 'Unknown'),
                                position=title,
                                description=description,
                                url=item.get('url', ''),
                                location=item.get('location', 'Remote'),
                                apply_url=item.get('url'),
                                date=str(item.get('created_at', '')),
                                source="Arbeitnow"
                            )
        except Exception as e:
            print(f"Error fetching from Arbeitnow: {e}")
            
        return list(all_jobs.values())
