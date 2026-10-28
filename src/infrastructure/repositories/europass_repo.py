import requests
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import JobRepository


class EuropassJobRepository(JobRepository):
    """
    Fetches jobs from EURES Job Search API (used by Europass).
    URL: https://europa.eu/eures/api/jv-searchengine/public/jv-search/search
    """
    def fetch_jobs(self, tag: str = "python") -> List[Job]:
        tags = [t.strip().lower() for t in tag.replace(';', ',').replace('|', ',').split(',') if t.strip()]
        all_jobs = {}
        headers = {"Content-Type": "application/json", "User-Agent": "JobSearchAutomation/1.0"}
        url = "https://europa.eu/eures/api/jv-searchengine/public/jv-search/search"

        print(f"Fetching jobs from Europass/EURES...")
        
        keywords = []
        if tags:
            for t in tags:
                keywords.append({"keyword": t, "specificSearchCode": "EVERYWHERE"})
        else:
            keywords.append({"keyword": "", "specificSearchCode": "EVERYWHERE"})

        payload = {
            "resultsPerPage": 50,
            "page": 1,
            "sortSearch": "BEST_MATCH",
            "keywords": keywords,
            "publicationPeriod": None,
            "occupationUris": [],
            "skillUris": [],
            "requiredExperienceCodes": [],
            "positionScheduleCodes": [],
            "sectorCodes": [],
            "educationAndQualificationLevelCodes": [],
            "positionOfferingCodes": [],
            "locationCodes": [],
            "euresFlagCodes": [],
            "otherBenefitsCodes": []
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                raw_jobs = data.get('jvs', [])

                for item in raw_jobs:
                    title = item.get('title', '')
                    if isinstance(title, dict):
                        title = title.get('en', list(title.values())[0] if title else '')
                    
                    translations = item.get('translations', {})
                    desc = ""
                    if 'en' in translations:
                        desc = translations['en'].get('description', '')
                    elif translations:
                        first_lang = list(translations.values())[0]
                        desc = first_lang.get('description', '')
                    
                    job_id = str(item.get('id', ''))
                    employer = item.get('employer', {})
                    company_name = employer.get('name', 'Unknown') if employer else 'Unknown'
                    
                    location_map = item.get('locationMap', {})
                    loc_str = ", ".join(location_map.keys()) if location_map else "Europe"

                    apply_url = f"https://europa.eu/eures/portal/jv-se/jv-details/{job_id}"

                    if job_id not in all_jobs:
                        all_jobs[job_id] = Job(
                            id=f"europass_{job_id}",
                            company=company_name,
                            position=title,
                            description=desc,
                            url=apply_url,
                            location=loc_str,
                            apply_url=apply_url,
                            date=str(item.get('creationDate', '')),
                            source="Europass / EURES"
                        )
        except Exception as e:
            print(f"Error fetching from Europass/EURES: {e}")

        return list(all_jobs.values())
