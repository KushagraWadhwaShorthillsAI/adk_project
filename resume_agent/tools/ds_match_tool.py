from typing import Dict, List, Any

def _generate_ascii_bar(percentage: float, length: int = 10) -> str:
    """Generates a simple ASCII bar chart."""
    filled_length = int(length * percentage / 100)
    bar = "█" * filled_length + "░" * (length - filled_length)
    return f"{bar} {percentage:.1f}%"

def compute_resume_job_match(resume, jobs) -> Dict[str, Any]:
    """
    Deterministic statistical matching with ASCII visualization.
    
    Args:
        resume: Dict with keys: skills (list), total_experience_years (int), education_level (str)
        jobs: List of job dicts from search_jobs_jsearch
    
    Returns:
        Dict with top_matches and market_stats
    """
    print(f"\n{'='*60}")
    print(f"🔧 TOOL CALLED: compute_resume_job_match")
    print(f"📊 Input: resume type={type(resume).__name__}, jobs count={len(jobs) if isinstance(jobs, list) else 'N/A'}")
    print(f"{'='*60}\n")
    
    # Input validation
    if not isinstance(jobs, list):
        return {"error": f"Expected 'jobs' to be a list, got {type(jobs).__name__}"}
    
    if not jobs:
        return {"error": "No jobs provided for matching"}
    
    if isinstance(resume, str):
        resume_skills = set(resume.lower().split())
        resume_exp = 1
        resume_edu = "bachelor"
    elif isinstance(resume, dict):
        resume_skills = set(s.lower() for s in resume.get("skills", []))
        resume_exp = resume.get("total_experience_years", 0)
        resume_edu = resume.get("education_level", "").lower()
    else:
        return {"error": f"Expected 'resume' to be dict or str, got {type(resume).__name__}"}

    job_scores = []

    for job in jobs:
        if not isinstance(job, dict):
            continue
            
        job_skills = set(s.lower() for s in job.get("skills", []))
        if not job_skills and job.get("description"):
             desc_tokens = set(job.get("description").lower().split())
             job_skills = desc_tokens.intersection(resume_skills) 

        min_exp = job.get("min_experience", 0)
        edu_req = job.get("education_level", "").lower()

        if not job_skills:
            skill_match = 0.0
            matched_skills = []
        else:
            intersection_set = resume_skills.intersection(job_skills)
            skill_match = len(intersection_set) / len(job_skills)
            matched_skills = list(intersection_set)

        if min_exp <= 0:
            exp_fit = 1.0
        else:
            ratio = resume_exp / min_exp
            exp_fit = min(ratio, 1.0)

        edu_fit = 1.0
        if "master" in edu_req and "master" not in resume_edu:
            edu_fit = 0.8
        elif "phd" in edu_req and "phd" not in resume_edu:
            edu_fit = 0.6

        final_score = (
            0.7 * skill_match +
            0.2 * exp_fit +
            0.1 * edu_fit
        ) * 100

        job_scores.append({
            "title": job.get("title"),
            "company": job.get("company"),
            "location": job.get("location"),
            "url": job.get("redirect_url") or job.get("url"),
            "score": round(final_score, 1),
            "match_graph": _generate_ascii_bar(final_score),
            "skill_match_percentage": round(skill_match * 100, 1),
            "skill_match_graph": _generate_ascii_bar(skill_match * 100),
            "matched_skills": matched_skills,
            "missing_skills": list(job_skills - resume_skills)[:5],
            "salary": job.get("salary", "Not Disclosed"),
            "is_remote": job.get("is_remote", False),
            "posted_at": job.get("posted_at", ""),
            "highlights": job.get("highlights", {})
        })

    job_scores.sort(key=lambda x: x["score"], reverse=True)
    top_jobs = job_scores[:10]

    result = {
        "top_matches": top_jobs,
        "market_stats": {
            "total_jobs_analyzed": len(jobs),
            "average_match_score": round(sum(j["score"] for j in job_scores) / len(job_scores), 1) if job_scores else 0,
        }
    }
    
    print(f"\n{'='*60}")
    print(f"✅ TOOL COMPLETED: compute_resume_job_match")
    print(f"📊 Output: {len(top_jobs)} top matches, avg score: {result['market_stats']['average_match_score']}")
    print(f"{'='*60}\n")
    
    return result
