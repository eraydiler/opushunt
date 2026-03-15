import os
import csv
from datetime import datetime
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import ApplicationRepository

class CSVApplicationRepository(ApplicationRepository):
    def __init__(self, filepath: str = "applications_history.csv"):
        self.filepath = filepath

    def save_application(self, job: Job, status: str):
        file_exists = os.path.isfile(self.filepath)
        
        with open(self.filepath, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            if not file_exists:
                writer.writerow(['Date', 'Company', 'Position', 'Location', 'URL', 'Status'])
                
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                job.company,
                job.position,
                job.location,
                job.url,
                status
            ])

    def get_applications(self) -> List[dict]:
        if not os.path.isfile(self.filepath):
            return []
            
        history = []
        with open(self.filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                history.append(row)
        return history
