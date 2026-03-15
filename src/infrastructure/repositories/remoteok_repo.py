import requests
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import JobRepository

class RemoteOKJobRepository(JobRepository):
    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        # Split tags by comma and clean whitespace
        # Robust splitting: replace common separators with comma
        cleaned_tag_input = tag.replace(';', ',').replace('|', ',')
        tags = [t.strip() for t in cleaned_tag_input.split(',') if t.strip()]
        
        print(f"DEBUG: Input tag string: '{tag}'")
        print(f"DEBUG: Parsed tags: {tags}")
        
        all_jobs = {} # Use dict for deduplication by ID
        headers = {"User-Agent": "JobSearchAutomation/1.0"}

        for current_tag in tags:
            print(f"Fetching '{current_tag}' jobs from RemoteOK...")
            url = f"https://remoteok.com/api?tag={current_tag}"
            
            try:
                response = requests.get(url, headers=headers)
                print(f"  -> Status Code: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"  -> Failed to fetch for {current_tag}")
                    continue
                    
                data = response.json()
                # The first item is usually legal info
                raw_jobs = data[1:] if len(data) > 1 else []
                print(f"  -> Found {len(raw_jobs)} raw items")
                
                for item in raw_jobs:
                    job_id = item.get('id', '')
                    if not job_id:
                        continue
                        
                    # Deduplicate
                    if job_id not in all_jobs:
                        all_jobs[job_id] = Job(
                            id=str(job_id),
                            company=item.get('company', 'Unknown'),
                            position=item.get('position', 'Unknown'),
                            description=item.get('description', ''),
                            url=item.get('url', ''),
                            location=item.get('location', 'Remote'),
                            apply_url=item.get('apply_url'),
                            date=item.get('date', '')
                        )
            except Exception as e:
                print(f"Error fetching jobs for tag '{current_tag}': {e}")
        
        return list(all_jobs.values())
