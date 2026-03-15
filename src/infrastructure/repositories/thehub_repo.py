import requests
import re
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import JobRepository

class TheHubJobRepository(JobRepository):
    """
    Fetches jobs from TheHub.io API.
    URL: https://thehub.io/api/jobs
    Good for Nordic/European startup jobs.
    """
    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        tags = [t.strip().lower() for t in tag.replace(';', ',').replace('|', ',').split(',') if t.strip()]
        all_jobs = {}
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # We can search via API query parameter
        for current_tag in tags[:3]:
            print(f"Fetching '{current_tag}' jobs from TheHub.io...")
            url = f"https://thehub.io/api/jobs?search={current_tag}"
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    raw_jobs = data.get('docs', [])
                    
                    for item in raw_jobs:
                        job_id = str(item.get('id', ''))
                        if not job_id:
                            continue
                            
                        title = item.get('title', '')
                        description = item.get('description', '')
                        company = item.get('company', {}).get('name', 'Unknown')
                        
                        text_to_search = (title + " " + description).lower()
                        
                        # Strict local filtering to ensure relevance
                        matches_tag = False
                        for t in tags:
                            pattern = r'(?<![a-zA-Z0-9_])' + re.escape(t) + r'(?![a-zA-Z0-9_])'
                            if re.search(pattern, text_to_search, re.IGNORECASE):
                                matches_tag = True
                                break
                                
                        if not matches_tag:
                            continue
                        
                        if job_id not in all_jobs:
                            location_data = item.get('location', {})
                            loc_str = f"{location_data.get('locality', '')}, {location_data.get('country', '')}".strip(', ')
                            if not loc_str and item.get('isRemote'):
                                loc_str = "Remote"
                                
                            job_url = item.get('absoluteJobUrl', '') or item.get('link', '')
                            
                            all_jobs[job_id] = Job(
                                id=f"thehub_{job_id}",
                                company=company,
                                position=title,
                                description=description,
                                url=job_url,
                                location=loc_str,
                                apply_url=job_url,
                                date=item.get('createdAt', ''),
                                source="TheHub"
                            )
            except Exception as e:
                print(f"Error fetching from TheHub for '{current_tag}': {e}")
                
        return list(all_jobs.values())
