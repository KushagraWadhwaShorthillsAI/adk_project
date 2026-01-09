import requests
import os
from typing import List, Dict


def search_jobs_adzuna(
    keywords: str,
    country: str = "in",
    max_results: int = 20
) -> List[Dict]:
    """
    Searches live job market using Adzuna API and returns structured results.
    """

    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    if not app_id or not app_key:
        raise EnvironmentError("Adzuna API credentials not set.")

    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": keywords,
        "content-type": "application/json",
        "results_per_page": max_results
    }

    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        raise RuntimeError(
            f"Adzuna API error: {response.status_code} - {response.text}"
        )

    data = response.json()
    jobs = []

    for job in data.get("results", []):
        description = job.get("description", "").lower()

        # naive skill extraction (can improve later)
        skills = [
            s for s in keywords.lower().split()
            if s in description
        ]

        jobs.append({
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "redirect_url": job.get("redirect_url"), # Pass the URL!
            "description": description, # Pass full description for downstream analysis
            "skills": skills,
            "min_experience": 1,  # default assumption
            "education_level": "bachelor"
        })

    return jobs
