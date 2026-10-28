import os
import json
from typing import List
from google import genai
from src.domain.entities import Job, Resume
from src.domain.interfaces import LLMService


class GeminiLLMService(LLMService):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

        # Models to try in order. 3.7 Flash is deprecated and redirects to 3.8.
        self.models = [
            "gemini-3.8-flash",
            "gemini-2.5-flash",
            "gemini-flash-latest",
        ]

    def generate_cover_letter(self, job: Job, resume: Resume) -> str:
        if not self.client:
            return "API Key missing. Cannot generate cover letter."

        prompt = f"""
        You are an experienced Professional Developer and Career Coach. Write a professional, tailored cover letter for the following job application.

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

    def filter_relevant_jobs(self, jobs: List[Job], resume: Resume, tags: str) -> List[Job]:
        """
        Uses LLM to evaluate a list of jobs against the candidate's resume and keywords.
        Returns only the jobs that are a strong semantic match.
        """
        if not self.client or not jobs:
            return jobs  # Return original list if API is missing or list is empty

        # Prepare a compressed version of jobs to save tokens
        jobs_data = []
        for j in jobs:
            jobs_data.append({
                "id": j.id,
                "title": j.position,
                "company": j.company,
                "description_snippet": j.description[:800] # Give enough context to decide
            })

        prompt = f"""
        You are an expert IT Recruiter and Career Coach.
        Your task is to filter a list of job postings to find ONLY the best matches for a candidate.

        Candidate's Target Keywords: {tags}
        Candidate's Resume Snippet:
        {resume.content[:3000]}

        Job Postings (JSON):
        {json.dumps(jobs_data, ensure_ascii=False)}

        Task:
        Analyze each job. Does it strongly match the candidate's profile and keywords?
        Ignore jobs that are clearly for different roles (e.g., HR, Sales, Customer Success, Backend-only) even if they mention the keyword.
        Return ONLY a raw JSON list of string IDs for the jobs that pass the filter. Do not include markdown formatting, backticks, or any other text.
        Example Output: ["123", "abc-456"]
        """

        last_error = None
        for model_name in self.models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )

                # Clean the response text to extract JSON
                result_text = response.text.strip()
                if result_text.startswith("```json"):
                    result_text = result_text[7:]
                if result_text.startswith("```"):
                    result_text = result_text[3:]
                if result_text.endswith("```"):
                    result_text = result_text[:-3]

                approved_ids = json.loads(result_text.strip())

                if isinstance(approved_ids, list):
                    filtered_jobs = [j for j in jobs if j.id in approved_ids]
                    return filtered_jobs

            except Exception as e:
                print(f"AI Filtering error with model {model_name}: {e}")
                last_error = e
                continue

        print(f"Failed to AI filter jobs: {last_error}")
        return jobs  # Fallback to returning all if AI fails
