import requests
from bs4 import BeautifulSoup
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import JobRepository
import re

class FindAJobDWPJobRepository(JobRepository):
    """
    Fetches jobs from findajob.dwp.gov.uk (UK Government job search).
    URL: https://findajob.dwp.gov.uk
    """
    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        tags = [t.strip().lower() for t in tag.replace(';', ',').replace('|', ',').split(',') if t.strip()]
        all_jobs = {}
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        for current_tag in tags[:3]:
            print(f"Fetching '{current_tag}' jobs from findajob.dwp.gov.uk...")
            url = f"https://findajob.dwp.gov.uk/search?q={current_tag}"
            
            try:
                response = requests.get(url, headers=headers, timeout=15)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    job_cards = soup.find_all("div", class_="search-result")
                    
                    for card in job_cards:
                        a_tag = card.find("a")
                        if not a_tag:
                            continue
                            
                        title = a_tag.get_text(strip=True)
                        link = a_tag["href"]
                        if link.startswith("/"):
                            link = f"https://findajob.dwp.gov.uk{link}"
                            
                        job_id = link.split("/")[-1] if "/" in link else link
                        
                        lis = card.find_all("li")
                        date = ""
                        company = "Unknown"
                        location = "Unknown"
                        
                        if len(lis) >= 2:
                            date = lis[0].get_text(strip=True)
                            company_loc_text = lis[1].get_text(separator="|", strip=True)
                            parts = [p.strip() for p in company_loc_text.split("|") if p.strip() and p.strip() != "-"]
                            if len(parts) >= 2:
                                company = parts[0]
                                location = parts[-1]
                            elif len(parts) == 1:
                                company = parts[0]
                                
                        desc_p = card.find("p", class_="search-result-description")
                        description = desc_p.get_text(strip=True) if desc_p else ""
                        
                        if job_id not in all_jobs:
                            all_jobs[job_id] = Job(
                                id=f"findajob_{job_id}",
                                company=company,
                                position=title,
                                description=description,
                                url=link,
                                location=location,
                                apply_url=link,
                                date=date,
                                source="FindAJob DWP"
                            )
            except Exception as e:
                print(f"Error fetching from findajob.dwp.gov.uk for '{current_tag}': {e}")
                
        return list(all_jobs.values())
