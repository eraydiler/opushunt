import requests
import re
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import JobRepository

class RemotiveJobRepository(JobRepository):
    """
    Fetches jobs from Remotive API.
    URL: https://remotive.com/api/remote-jobs
    No API Key required.
    """
    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        # Remotive allows filtering by category or search term
        # We will use the 'search' parameter for tags
        tags = [t.strip() for t in tag.replace(';', ',').replace('|', ',').split(',') if t.strip()]
        
        all_jobs = {}
        headers = {"User-Agent": "JobSearchAutomation/1.0"}

        for current_tag in tags:
            print(f"Fetching '{current_tag}' jobs from Remotive...")
            url = f"https://remotive.com/api/remote-jobs?search={current_tag}"
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    continue
                    
                data = response.json()
                raw_jobs = data.get('jobs', [])
                
                for item in raw_jobs:
                    job_id = str(item.get('id', ''))
                    if not job_id:
                        continue
                        
                    # Strict local filtering to ensure relevance
                    title = item.get('title', '')
                    description = item.get('description', '')
                    text_to_search = (title + " " + description).lower()
                    
                    matches_tag = False
                    for t in tags:
                        pattern = r'(?<![a-zA-Z0-9_])' + re.escape(t) + r'(?![a-zA-Z0-9_])'
                        if re.search(pattern, text_to_search, re.IGNORECASE):
                            matches_tag = True
                            break
                            
                    if not matches_tag:
                        continue
                        
                    if job_id not in all_jobs:
                        all_jobs[job_id] = Job(
                            id=f"remotive_{job_id}",
                            company=item.get('company_name', 'Unknown'),
                            position=item.get('title', 'Unknown'),
                            description=item.get('description', ''),
                            url=item.get('url', ''),
                            location=item.get('candidate_required_location', 'Remote'),
                            apply_url=item.get('url'), # Remotive URL usually redirects to apply
                            date=item.get('publication_date', ''),
                            source="Remotive"
                        )
            except Exception as e:
                print(f"Error fetching from Remotive for '{current_tag}': {e}")
                
        return list(all_jobs.values())
