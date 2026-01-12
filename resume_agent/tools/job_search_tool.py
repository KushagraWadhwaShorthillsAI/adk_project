import requests
import os
import re
from typing import List, Dict


def search_jobs_jsearch(
    keywords: str,
    country: str = "in",
    max_results: int = 20,
    user_experience_years: int = None
) -> List[Dict]:
    """
    Searches live job market using JSearch API (RapidAPI) with robust skill extraction.
    Filters jobs to match user's experience level.
    
    Args:
        keywords: Job titles to search for
        country: Country code (default: "in")
        max_results: Maximum results to return
        user_experience_years: User's total years of experience (filters jobs requiring <= this)
    """
    print(f"\n{'='*60}")
    print(f"🔧 TOOL CALLED: search_jobs_jsearch")
    print(f"🔍 Input: keywords='{keywords}', country='{country}', max_results={max_results}, user_experience={user_experience_years}")
    print(f"{'='*60}\n")

    api_key = os.getenv("RAPID_API_KEY")
    api_host = os.getenv("RAPID_API_HOST")

    if not api_key or not api_host:
        raise RuntimeError("RapidAPI credentials (RAPID_API_KEY, RAPID_API_HOST) not found in environment.")

    keywords = keywords.replace(',', ' ').strip()
    if not keywords:
        keywords = "Software Engineer"

    url = f"https://{api_host}/search"

    params = {
        "query": f"{keywords} in {country}",
        "page": "1",
        "num_pages": "1",
        "country": country,
        "date_posted": "all"
    }

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": api_host
    }

    response = requests.get(url, headers=headers, params=params, timeout=15)

    if response.status_code != 200:
        raise RuntimeError(
            f"JSearch API error: {response.status_code} - {response.text}"
        )

    data = response.json()
    jobs = []

    TECH_ANCHORS = {
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'kotlin', 'swift', 'scala', 'dart', 'solidity',
        'react', 'angular', 'vue', 'nextjs', 'next.js', 'remix', 'svelte', 'jquery', 'tailwind', 'bootstrap', 'sass', 'html', 'css', 'webpack', 'vite',
        'nodejs', 'node.js', 'django', 'flask', 'fastapi', 'express', 'spring', 'laravel', 'symfony', 'rails', 'graphql', 'rest', 'bridge', 'grpc',
        'ml', 'ai', 'nlp', 'pytorch', 'tensorflow', 'keras', 'scikit-learn', 'sklearn', 'pandas', 'numpy', 'opencv', 'huggingface', 'transformers', 'bert', 'gpt', 'llm', 'langchain', 'llama',
        'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s', 'jenkins', 'terraform', 'ansible', 'git', 'github', 'gitlab', 'ci/cd', 'nginx', 'apache',
        'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'mongo', 'redis', 'elasticsearch', 'cassandra', 'dynamodb', 'sqlite', 'mariadb', 'pinecone', 'milvus',
        'flutter', 'react native', 'ios', 'android', 'electron', 'unity', 'unreal',
        'fullstack', 'frontend', 'backend', 'devops', 'architect', 'agile', 'scrum', 'kanban', 'qa', 'automated testing', 'selenium', 'playwright', 'cypress'
    }

    VARIATION_MAP = {
        'nodejs': 'node.js', 'node js': 'node.js',
        'reactjs': 'react', 'react js': 'react',
        'k8s': 'kubernetes',
        'ml': 'machine learning', 'dl': 'deep learning',
        'pg': 'postgresql', 'postgres': 'postgresql'
    }

    for job in data.get("data", []):
        description = job.get("job_description", "")
        title = job.get("job_title", "")
        
        highlights = job.get("job_highlights", {})
        qualifications = " ".join(highlights.get("Qualifications", []))
        responsibilities = " ".join(highlights.get("Responsibilities", []))
        benefits = " ".join(highlights.get("Benefits", []))
        
        searchable_text = f"{title} {description} {qualifications} {responsibilities}".lower()
        
        found_skills = set()
        
        for anchor in TECH_ANCHORS:
            pattern = rf'\b{re.escape(anchor)}\b' if len(anchor) < 6 else re.escape(anchor)
            if re.search(pattern, searchable_text):
                found_skills.add(VARIATION_MAP.get(anchor, anchor))
        
        patterns = [
            r'\b[a-z]{1,2}\+\+\b',
            r'\b[a-z]{1,2}#\b',
            r'\b\.net\b',
            r'\b[a-z0-9]+\.[a-z]+\b',
            r'\b[a-z]+-[0-9]+\b'
        ]
        for p in patterns:
            for match in re.findall(p, searchable_text):
                found_skills.add(match)

        min_years = 1
        exp_match = re.search(r'(\d+)\+?\s*years?', searchable_text)
        if exp_match:
            min_years = int(exp_match.group(1))
        
        edu_level = "bachelor"
        if "master" in searchable_text:
            edu_level = "master"
        elif "phd" in searchable_text or "doctorate" in searchable_text:
            edu_level = "phd"

        location = f"{job.get('job_city', '')}, {job.get('job_state', '')}, {job.get('job_country', '')}".strip(", ")

        min_sal = job.get("job_min_salary")
        max_sal = job.get("job_max_salary")
        period = job.get("job_salary_period", "YEAR")
        salary_str = "Not Disclosed"
        if min_sal and max_sal:
            salary_str = f"${min_sal:,} - ${max_sal:,} per {period.lower()}"
        elif min_sal:
            salary_str = f"From ${min_sal:,} per {period.lower()}"

        jobs.append({
            "title": title,
            "company": job.get("employer_name"),
            "location": location or ("Remote" if job.get("job_is_remote") else "N/A"),
            "redirect_url": job.get("job_apply_link"),
            "description": description[:500] + "...",
            "skills": list(found_skills),
            "min_experience": min_years,
            "education_level": edu_level,
            "salary": salary_str,
            "is_remote": job.get("job_is_remote", False),
            "posted_at": job.get("job_posted_at_datetime_utc", ""),
            "highlights": {
                "qualifications": highlights.get("Qualifications", [])[:3],
                "responsibilities": highlights.get("Responsibilities", [])[:3]
            }
        })

    if user_experience_years is not None:
        filtered_jobs = []
        for job in jobs:
            job_min_exp = job.get("min_experience", 0)
            if job_min_exp == 0 or job_min_exp <= user_experience_years:
                filtered_jobs.append(job)
        
        print(f"📊 Experience Filter: {len(jobs)} jobs found, {len(filtered_jobs)} match experience level (<= {user_experience_years} years)")
        jobs = filtered_jobs

    result = jobs[:max_results]
    print(f"\n{'='*60}")
    print(f"✅ TOOL COMPLETED: search_jobs_jsearch")
    print(f"📊 Output: Returned {len(result)} jobs")
    if user_experience_years:
        print(f"🎯 Filtered for jobs requiring <= {user_experience_years} years experience")
    print(f"{'='*60}\n")
    return result
