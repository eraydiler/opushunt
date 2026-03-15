import requests
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import JobRepository

class JobicyJobRepository(JobRepository):
    """
    Fetches jobs from Jobicy API.
    URL: https://jobicy.com/api/v2/remote-jobs
    Good for Remote jobs globally.
    """
    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        # Jobicy supports 'tag' parameter for search
        # We can also add 'geo' if needed, but let's keep it broad for now
        
        # Clean tags: Jobicy takes a single tag usually, or we can iterate
        tags = [t.strip().lower() for t in tag.replace(';', ',').replace('|', ',').split(',') if t.strip()]
        all_jobs = {}
        headers = {"User-Agent": "JobSearchAutomation/1.0"}
        
        # Jobicy might not support multiple tags in one go well, so let's iterate
        # Limit to first few tags to avoid too many requests
        for current_tag in tags[:3]: 
            print(f"Fetching '{current_tag}' jobs from Jobicy...")
            url = f"https://jobicy.com/api/v2/remote-jobs?tag={current_tag}&count=50"
            
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    # Check if success
                    if not data.get('success'):
                        continue
                        
                    raw_jobs = data.get('jobs', [])
                    
                    for item in raw_jobs:
                        job_id = str(item.get('id', ''))
                        if not job_id:
                            continue
                            
                        # Deduplicate
                        if job_id not in all_jobs:
                            # Jobicy returns HTML in description, we'll clean it later in UI or here
                            # But our UI now has clean_html_text helper
                            
                            # Location might be in jobGeo
                            loc = item.get('jobGeo', 'Remote')
                            
                            all_jobs[job_id] = Job(
                                id=f"jobicy_{job_id}",
                                company=item.get('companyName', 'Unknown'),
                                position=item.get('jobTitle', 'Unknown'),
                                description=item.get('jobDescription', ''),
                                url=item.get('url', ''),
                                location=loc if loc else "Remote",
                                apply_url=item.get('url'),
                                date=item.get('pubDate', ''),
                                source="Jobicy"
                            )
            except Exception as e:
                print(f"Error fetching from Jobicy for '{current_tag}': {e}")
        
        return list(all_jobs.values())
