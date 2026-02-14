import requests
from src.config import Config

BASE_URL = "https://api.adzuna.com/v1/api/jobs"

def fetch_jobs(keyword="data", location="united states", results=50):
    url = f"{BASE_URL}/{Config.ADZUNA_COUNTRY}/search/1"
    params = {
        "app_id": Config.ADZUNA_APP_ID,
        "app_key": Config.ADZUNA_APP_KEY,
        "what": keyword,
        "where": location,
        "results_per_page": results,
        "content-type": "application/json"
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()["results"]

    jobs = []
    for job in data:
        jobs.append({
            "id": job.get("id"),
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "description": job.get("description"),
            "created": job.get("created")
        })
    return jobs
