from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.routes.auth import login_required
from app.services.nlp_service import NLPService
from app.models.resume import Resume, ResumeSection
import json
import logging
from app.database.db import get_db

bp = Blueprint('analysis', __name__, url_prefix='/analysis')

@bp.route('/<int:resume_id>/analyze')
@login_required
def analyze_resume(resume_id):
    nlp = NLPService()
    print(f"DEBUG: Analyzing Resume ID: {resume_id}")
    try:
        job_recs = nlp.recommend_jobs(resume_id)
        # Fix match_score vs score inconsistency if any
        for rec in job_recs:
             if 'score' in rec and 'match_score' not in rec:
                  rec['match_score'] = rec['score']
        print(f"DEBUG: Recommendations: {job_recs}")
    except Exception as e:
        print(f"ERROR in recommend_jobs: {e}")
        job_recs = []
    
    # Analyze gap for the top recommendation if available
    gap_analysis = None
    if job_recs:
        top_role = job_recs[0]['role']
        gap_analysis = nlp.analyze_skill_gap(resume_id, top_role)
        
    # Calculate ATS Score
    resume = Resume.get_by_id(resume_id)
    sections_list = ResumeSection.get_all_by_resume(resume_id)
    
    # Reconstruct sections dict
    sections_dict = {}
    full_text = ""
    for s in sections_list:
        name = s['section_name']
        content = s['section_content']
        sections_dict[name] = content
        
        if isinstance(content, str):
            full_text += content + " "
        elif isinstance(content, dict):
            full_text += " ".join([str(v) for v in content.values() if v]) + " "
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    full_text += " ".join([str(v) for v in item.values() if v]) + " "
                else:
                    full_text += str(item) + " "
    
    ats_result = nlp.calculate_ats_score(full_text, sections_dict)
    
    # NEW logic for detailed Job Cards
    detailed_jobs = []
    try:
        from app.services.job_recommender import recommend_jobs
        from app.services.job_roles import JOB_ROLES
        extracted_skills = nlp.extract_skills_list(sections_dict)
        if not extracted_skills:
            import re
            extracted_skills = list(set(re.findall(r'\b[a-zA-Z]+\b', full_text.lower())))
        detailed_jobs = recommend_jobs(extracted_skills, JOB_ROLES)
    except Exception as e:
        print("Error evaluating detailed_jobs:", e)
    
    return jsonify({
        'status': 'success',
        'recommendations': job_recs,
        'gap_analysis': gap_analysis,
        'ats_score': ats_result,
        'detailed_jobs': detailed_jobs
    })

def match_jobs(user_skills):
    """
    Compare user skills with job required_skills.
    Calculate match percentage = (matched skills / required skills) * 100
    Return top 10-15 recommended jobs sorted by match %.
    """
    user_skills_lower = set([s.lower() for s in user_skills if s])
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    
    # Get all jobs
    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()
    
    # Get all sources
    cursor.execute("SELECT * FROM job_sources")
    sources = cursor.fetchall()
    
    # Map sources to job_id
    sources_by_job = {}
    for src in sources:
        jid = src['job_id']
        if jid not in sources_by_job:
            sources_by_job[jid] = []
        sources_by_job[jid].append(src)
        
    scored_jobs = []
    
    for job in jobs:
        try:
            req_skills = json.loads(job['required_skills'])
        except Exception:
            req_skills = []
            
        if not req_skills:
            continue
            
        req_skills_lower = set([s.lower() for s in req_skills if s])
        matched_skills = req_skills_lower.intersection(user_skills_lower)
        missing_skills = req_skills_lower - user_skills_lower
        
        match_pct = (len(matched_skills) / len(req_skills_lower)) * 100
        
        if match_pct > 0: # Only recommend if >0% match? Or maybe always score and sort
            job_sources = sources_by_job.get(job['id'], [])
            
            scored_jobs.append({
                'id': job['id'],
                'job_title': job['job_title'],
                'category': job['category'],
                'demand_level': job['demand_level'],
                'match_percentage': round(match_pct),
                'matched_skills': [s.title() for s in matched_skills],
                'missing_skills': [s.title() for s in missing_skills],
                'optional_skills': json.loads(job['optional_skills']) if job.get('optional_skills') else [],
                'platforms': job_sources
            })
            
    # Sort by match percentage (desc)
    scored_jobs.sort(key=lambda x: x['match_percentage'], reverse=True)
    
    # Return top 15
    return scored_jobs[:15]

@bp.route('/recommend-jobs', methods=['POST'])
@login_required
def recommend_jobs_api():
    """
    API endpoint to evaluate user skills and return job recommendations across platforms.
    Accepts JSON body: { "skills": ["Python", "Flask", ...] }
    """
    data = request.get_json() or {}
    user_skills = data.get('skills', [])
    
    if not user_skills:
        return jsonify({"status": "error", "message": "No skills provided"}), 400
        
    recommended = match_jobs(user_skills)
    
    return jsonify({
        "status": "success",
        "jobs": recommended
    })

