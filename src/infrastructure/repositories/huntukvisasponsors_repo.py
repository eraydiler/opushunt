import requests
from bs4 import BeautifulSoup
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import JobRepository
import re

class HuntUKVisaSponsorsJobRepository(JobRepository):
    """
    Fetches jobs from Hunt UK Visa Sponsors.
    URL: https://huntukvisasponsors.com
    """
    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        tags = [t.strip().lower() for t in tag.replace(';', ',').replace('|', ',').split(',') if t.strip()]
        all_jobs = {}
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        for current_tag in tags[:3]:
            print(f"Fetching '{current_tag}' jobs from huntukvisasponsors.com...")
            # fetch from /jobs directly
            url = f"https://huntukvisasponsors.com/jobs?q={current_tag}"
            
            try:
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    job_links = soup.find_all("a", href=lambda h: h and "/job/" in h)
                    
                    for a_tag in job_links:
                        link = a_tag["href"]
                        if link.startswith("/"):
                            link = f"https://huntukvisasponsors.com{link}"
                            
                        job_id = link.split("/")[-1]
                        
                        parent = a_tag.parent
                        texts = [t.strip() for t in parent.get_text(separator="|", strip=True).split("|") if t.strip()]
                        
                        title = "Unknown"
                        company = "Unknown"
                        description = ""
                        location = "Unknown"
                        date = ""
                        
                        if len(texts) >= 6:
                            title = texts[0]
                            company = texts[1]
                            description = texts[3]
                            location = texts[4]
                            date = texts[5]
                        elif len(texts) >= 5:
                            title = texts[0]
                            company = texts[1]
                            description = texts[2]
                            location = texts[3]
                            date = texts[-1]
                        elif len(texts) >= 3:
                            title = texts[0]
                            company = texts[1]
                            
                        # Strict local filtering
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
                                id=f"huntuk_{job_id}",
                                company=company,
                                position=title,
                                description=description,
                                url=link,
                                location=location,
                                apply_url=link,
                                date=date,
                                source="HuntUKVisaSponsors"
                            )
            except Exception as e:
                print(f"Error fetching from huntukvisasponsors.com for '{current_tag}': {e}")
                
        return list(all_jobs.values())
