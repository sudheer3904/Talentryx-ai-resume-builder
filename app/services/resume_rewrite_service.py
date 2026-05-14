"""
Resume Rewriting Engine: adapt resume sections per career without fabricating experience.
Reorganizes sections, highlights relevant skills, adapts summary with role-specific keywords.
Uses same core data; only emphasis and order change.
"""
import copy
from app.services.career_mapping_service import (
    get_cluster_keywords_summary,
    get_cluster_skills,
    _load_job_clusters,
)


def _cluster_display_name(cluster_key):
    data = _load_job_clusters()
    return (data.get('clusters') or {}).get(cluster_key, {}).get('display_name', cluster_key.replace('_', ' ').title())


def rewrite_sections_for_career(sections, cluster_key):
    """
    For a given career (cluster_key), return a new sections dict with:
    - personal.role set to career display name
    - personal.summary adapted with role keywords (prepended phrase, no fabrication)
    - skills: reorder so cluster-relevant skills appear first (tech and soft)
    - experience/education/projects: unchanged (factual)
    """
    if not sections:
        return sections
    out = copy.deepcopy(sections)

    display_name = _cluster_display_name(cluster_key)
    keywords = get_cluster_keywords_summary(cluster_key)
    cluster_skill_set = set(get_cluster_skills(cluster_key))

    # Personal: set role (do not auto-prepend canned summary text)
    personal = out.get('personal') or {}
    personal = dict(personal)
    personal['role'] = display_name
    out['personal'] = personal

    # Skills: reorder to put cluster-matching skills first
    skills = out.get('skills')
    if isinstance(skills, dict):
        skills = dict(skills)
        for key in ('skills_tech', 'skills_soft', 'skills_languages'):
            raw = skills.get(key, '')
            if not raw:
                continue
            parts = [p.strip() for p in str(raw).replace(';', ',').split(',') if p.strip()]
            if not parts:
                continue
            matched = []
            rest = []
            for p in parts:
                if p.lower() in cluster_skill_set or any(term in p.lower() for term in cluster_skill_set):
                    matched.append(p)
                else:
                    rest.append(p)
            skills[key] = ', '.join(matched + rest) if (matched or rest) else raw
        out['skills'] = skills

    # Experience: reorder to put cluster-matching experiences first
    experience = out.get('experience')
    if isinstance(experience, list):
        matched_exp = []
        rest_exp = []
        for exp in experience:
            if not isinstance(exp, dict): 
                continue
            
            exp_text = (str(exp.get('role', '')) + " " + str(exp.get('description', '')) + " " + str(exp.get('company', ''))).lower()
            
            is_match = False
            for term in cluster_skill_set:
                if term in exp_text:
                    is_match = True
                    break
            
            if not is_match:
                for kw in keywords:
                    if kw.lower() in exp_text:
                        is_match = True
                        break
                        
            if is_match:
                matched_exp.append(exp)
            else:
                rest_exp.append(exp)
        
        out['experience'] = matched_exp + rest_exp

    # Projects: reorder to put cluster-matching projects first
    projects = out.get('projects')
    if isinstance(projects, list):
        matched_proj = []
        rest_proj = []
        for proj in projects:
            if not isinstance(proj, dict):
                continue
            
            proj_text = (str(proj.get('title', '')) + " " + str(proj.get('description', '')) + " " + str(proj.get('tech', ''))).lower()
            
            is_match = False
            for term in cluster_skill_set:
                if term in proj_text:
                    is_match = True
                    break
                    
            if not is_match:
                for kw in keywords:
                    if kw.lower() in proj_text:
                        is_match = True
                        break
                        
            if is_match:
                matched_proj.append(proj)
            else:
                rest_proj.append(proj)
                
        out['projects'] = matched_proj + rest_proj

    return out


def get_section_order_for_career(cluster_key):
    """
    Return preferred section order for this career (e.g. skills first for technical roles).
    Default order matches existing pdf_template: experience, education, skills, projects, certifications, hobbies.
    """
    data = _load_job_clusters()
    layout = (data.get('layout_by_career') or {}).get(cluster_key, 'one_column')
    if layout == 'two_column':
        return ['experience', 'education', 'skills', 'projects', 'certifications', 'hobbies']
    if layout == 'modern_flow':
        return ['experience', 'education', 'skills', 'projects', 'certifications', 'hobbies']
    return ['experience', 'education', 'skills', 'projects', 'certifications', 'hobbies']
