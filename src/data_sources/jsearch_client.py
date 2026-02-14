import requests
from src.config import Config

BASE_URL = "https://jsearch.p.rapidapi.com/search"

def fetch_jobs_jsearch(keyword="data scientist", location="United States", page=1):
    """
    Fetch real-time job postings using JSearch API (RapidAPI).
    Returns a normalized list of job dictionaries.
    """

    if not Config.RAPIDAPI_KEY:
        raise RuntimeError("Missing RAPIDAPI_KEY in environment variables.")

    headers = {
        "X-RapidAPI-Key": Config.RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }

    querystring = {
        "query": f"{keyword} in {location}",
        "page": str(page),
        "num_pages": "1",
        "date_posted": "all"
    }

    response = requests.get(BASE_URL, headers=headers, params=querystring, timeout=30)
    response.raise_for_status()
    results = response.json().get("data", [])

    jobs = []
    for job in results:
        jobs.append({
            "id": job.get("job_id"),
            "title": job.get("job_title"),
            "company": job.get("employer_name"),
            "location": job.get("job_city") or job.get("job_country"),
            "description": job.get("job_description"),
            "created": job.get("job_posted_at_datetime_utc")
        })

    return jobs
