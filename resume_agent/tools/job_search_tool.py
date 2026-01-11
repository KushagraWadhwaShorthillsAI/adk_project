import requests
import os
import re
from typing import List, Dict


def search_jobs_jsearch(
    keywords: str,
    country: str = "in",
    max_results: int = 20
) -> List[Dict]:
    """
    Searches live job market using JSearch API (RapidAPI) with robust skill extraction.
    """

    api_key = os.getenv("RAPID_API_KEY")
    api_host = os.getenv("RAPID_API_HOST")

    if not api_key or not api_host:
        raise RuntimeError("RapidAPI credentials (RAPID_API_KEY, RAPID_API_HOST) not found in environment.")

    # Clean keywords: strip commas and extra whitespace
    keywords = keywords.replace(',', ' ').strip()
    if not keywords:
        # Fallback to a general tech search if keywords is empty
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

    # Smarter & Comprehensive Tech Anchors
    TECH_ANCHORS = {
        # Languages
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'kotlin', 'swift', 'scala', 'dart', 'solidity',
        # Web & Frontend
        'react', 'angular', 'vue', 'nextjs', 'next.js', 'remix', 'svelte', 'jquery', 'tailwind', 'bootstrap', 'sass', 'html', 'css', 'webpack', 'vite',
        # Backend & APIs
        'nodejs', 'node.js', 'django', 'flask', 'fastapi', 'express', 'spring', 'laravel', 'symfony', 'rails', 'graphql', 'rest', 'bridge', 'grpc',
        # Data Science & AI
        'ml', 'ai', 'nlp', 'pytorch', 'tensorflow', 'keras', 'scikit-learn', 'sklearn', 'pandas', 'numpy', 'opencv', 'huggingface', 'transformers', 'bert', 'gpt', 'llm', 'langchain', 'llama',
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'k8s', 'jenkins', 'terraform', 'ansible', 'git', 'github', 'gitlab', 'ci/cd', 'nginx', 'apache',
        # Databases & Cache
        'sql', 'mysql', 'postgresql', 'postgres', 'mongodb', 'mongo', 'redis', 'elasticsearch', 'cassandra', 'dynamodb', 'sqlite', 'mariadb', 'pinecone', 'milvus',
        # Mobile & Desktop
        'flutter', 'react native', 'ios', 'android', 'electron', 'unity', 'unreal',
        # Roles & Methodologies
        'fullstack', 'frontend', 'backend', 'devops', 'architect', 'agile', 'scrum', 'kanban', 'qa', 'automated testing', 'selenium', 'playwright', 'cypress'
    }

    # Common variation map for normalization
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
        
        # Combine title, description, and highlights for better skill extraction
        highlights = job.get("job_highlights", {})
        qualifications = " ".join(highlights.get("Qualifications", []))
        responsibilities = " ".join(highlights.get("Responsibilities", []))
        benefits = " ".join(highlights.get("Benefits", []))
        
        searchable_text = f"{title} {description} {qualifications} {responsibilities}".lower()
        
        # Inlined Robust Extraction
        found_skills = set()
        
        # 1. Direct Anchor Matching (Permissive)
        for anchor in TECH_ANCHORS:
            # Match strictly with boundaries for short words, more relaxed for long ones
            pattern = rf'\b{re.escape(anchor)}\b' if len(anchor) < 6 else re.escape(anchor)
            if re.search(pattern, searchable_text):
                # Normalize and Add
                found_skills.add(VARIATION_MAP.get(anchor, anchor))
        
        # 2. Regex for specialty formats (C++, C#, .NET, etc.)
        patterns = [
            r'\b[a-z]{1,2}\+\+\b',       # C++
            r'\b[a-z]{1,2}#\b',          # C#
            r'\b\.net\b',                 # .NET
            r'\b[a-z0-9]+\.[a-z]+\b',    # Node.js, .NET
            r'\b[a-z]+-[0-9]+\b'          # AWS-3, etc
        ]
        for p in patterns:
            for match in re.findall(p, searchable_text):
                found_skills.add(match)

        # Basic Experience & Education heuristics
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

        # Salary formatting
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
            "description": description[:500] + "...", # Truncate for efficiency
            "skills": list(found_skills),
            "min_experience": min_years, 
            "education_level": edu_level,
            "salary": salary_str,
            "is_remote": job.get("job_is_remote", False),
            "posted_at": job.get("job_posted_at_datetime_utc", ""),
            "highlights": {
                "qualifications": highlights.get("Qualifications", [])[:3], # Top 3
                "responsibilities": highlights.get("Responsibilities", [])[:3] # Top 3
            }
        })

    return jobs[:max_results]
