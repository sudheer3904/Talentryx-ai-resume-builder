def calculate_match(user_skills, job_skills):
    if not job_skills: return 0
    
    # Normalize skills to lowercase for better matching
    user_skills_lower = [s.lower().strip() for s in user_skills if s]
    job_skills_lower = [s.lower().strip() for s in job_skills if s]
    
    match_count = len(set(user_skills_lower) & set(job_skills_lower))
    return match_count / len(job_skills)

def recommend_jobs(user_skills, JOB_ROLES):
    results = []
    for job, data in JOB_ROLES.items():
        skill_score = calculate_match(user_skills, data["skills"])
        demand_score = data["demand"]
        final_score = (0.7 * skill_score) + (0.3 * demand_score)
        
        user_skills_lower = [s.lower().strip() for s in user_skills if s]
        missing_skills = [
            skill for skill in data["skills"] 
            if skill.lower().strip() not in user_skills_lower
        ]
        
        results.append({
            "job": job,
            "score": round(final_score * 100, 2),
            "required_skills": data["skills"],
            "missing_skills": missing_skills,
            "trend": data["trend"],
            "apply_link": data["apply_link"]
        })
    
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:5]
