import os
import csv
import streamlit as st
from datetime import datetime
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import ApplicationRepository

class SessionApplicationRepository(ApplicationRepository):
    """
    Stores application history in Streamlit's Session State.
    Data is lost when the browser tab is closed (secure for multi-user).
    """
    def __init__(self):
        if 'application_history' not in st.session_state:
            st.session_state['application_history'] = []

    def save_application(self, job: Job, status: str):
        record = {
            'Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Company': job.company,
            'Position': job.position,
            'Location': job.location,
            'URL': job.url,
            'Status': status
        }
        st.session_state['application_history'].append(record)

    def get_applications(self) -> List[dict]:
        return st.session_state.get('application_history', [])
