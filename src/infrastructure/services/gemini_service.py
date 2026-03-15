import os
from google import genai
from src.domain.entities import Job, Resume
from src.domain.interfaces import LLMService

class GeminiLLMService(LLMService):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        
        # Models to try in order
        self.models = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-flash-latest",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ]

    def generate_cover_letter(self, job: Job, resume: Resume) -> str:
        if not self.client:
            return "API Key missing. Cannot generate cover letter."

        prompt = f"""
        You are an experienced iOS Developer. Write a professional, tailored cover letter for the following job application.
        
        Resume:
        {resume.content}
        
        Job Details:
        Company: {job.company}
        Position: {job.position}
        Description: {job.description[:2000]}... (truncated)
        
        Rules:
        1. Write in English.
        2. Address to {job.company}.
        3. Highlight relevant skills from the resume.
        4. Keep it concise (max 250 words).
        5. No placeholders.
        """
        
        last_error = None
        for model_name in self.models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                return response.text
            except Exception as e:
                last_error = e
                continue
                
        return f"Error generating cover letter: {last_error}"
