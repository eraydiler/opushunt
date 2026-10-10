import requests
import re
import html
from typing import List
from src.domain.entities import Job
from src.domain.interfaces import JobRepository


class HackerNewsJobRepository(JobRepository):
    """
    Fetches jobs from Hacker News 'Who is hiring?' threads via Algolia API.
    API: http://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&query=Who%20is%20hiring
    """
    def fetch_jobs(self, tag: str = "ios") -> List[Job]:
        print(f"Fetching '{tag}' jobs from Hacker News...")
        jobs = []
        tags = [t.strip().lower() for t in tag.replace(';', ',').replace('|', ',').split(',') if t.strip()]

        try:
            # 1. Find the latest "Who is hiring?" thread
            search_url = "http://hn.algolia.com/api/v1/search_by_date?tags=story,author_whoishiring&query=Who%20is%20hiring&hitsPerPage=1"
            response = requests.get(search_url, timeout=10)

            if response.status_code != 200:
                print("  -> Failed to search HN threads")
                return []

            data = response.json()
            if not data.get('hits'):
                print("  -> No HN threads found")
                return []

            thread_id = data['hits'][0]['objectID']
            thread_title = data['hits'][0]['title']
            print(f"  -> Found thread: {thread_title} (ID: {thread_id})")

            # 2. Fetch comments (job posts) from that thread
            # Algolia limit is 1000 hits, which should cover most comments for a recent thread
            # We use search endpoint filtered by tag 'comment' and numeric filter for parent/story
            comments_url = f"http://hn.algolia.com/api/v1/search?tags=comment,story_{thread_id}&hitsPerPage=1000"
            comments_response = requests.get(comments_url, timeout=15)

            if comments_response.status_code != 200:
                print("  -> Failed to fetch HN comments")
                return []

            comments_data = comments_response.json()
            hits = comments_data.get('hits', [])
            print(f"  -> Analying {len(hits)} comments...")

            for hit in hits:
                text = hit.get('comment_text', '')
                if not text:
                    continue

                # Clean HTML for searching
                # HN comments are HTML escaped and contain <p> tags
                clean_text = html.unescape(text).replace('<p>', '\n').replace('</p>', '')
                clean_text_lower = clean_text.lower()

                # Check for matches
                matches_tag = False
                for t in tags:
                    # Regex for whole word match
                    pattern = r'(?<![a-zA-Z0-9_])' + re.escape(t) + r'(?![a-zA-Z0-9_])'
                    if re.search(pattern, clean_text_lower, re.IGNORECASE):
                        matches_tag = True
                        break

                if matches_tag:
                    # Extract Company and Position (Heuristic: usually first line)
                    lines = clean_text.split('\n')
                    first_line = lines[0] if lines else "Unknown Position"

                    # Try to split by common separators | or - or ,
                    company = "Hacker News"
                    position = first_line[:100] # Truncate if too long

                    if '|' in first_line:
                        parts = first_line.split('|')
                        company = parts[0].strip()
                        position = parts[1].strip()

                    job_id = str(hit.get('objectID'))
                    job_url = f"https://news.ycombinator.com/item?id={job_id}"

                    jobs.append(Job(
                        id=f"hn_{job_id}",
                        company=company,
                        position=position,
                        description=text, # Keep original HTML for the UI to render
                        url=job_url,
                        location="Remote (Likely)", # HN threads are often remote-friendly, but hard to parse reliably without AI
                        apply_url=job_url,
                        date=hit.get('created_at', ''),
                        source="Hacker News"
                    ))

            return jobs

        except Exception as e:
            print(f"Error fetching from Hacker News: {e}")
            return []
