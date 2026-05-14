"""
Multi-Career Resume: Skill Extraction, Transferable Skill Mapping, Career Path Detection.
Uses TF-IDF + Cosine Similarity against job clusters. Does not modify existing ml_service or nlp_service.
"""
import json
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _load_job_clusters():
    """Load job clusters from app/data/job_clusters.json."""
    base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base, 'app', 'data', 'job_clusters.json')
    if not os.path.exists(path):
        path = os.path.join(os.path.dirname(__file__), '..', 'data', 'job_clusters.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_skills_full(resume_data):
    """
    Skill Extraction Module: extract technical skills, soft skills, tools, certifications, projects.
    resume_data: dict with keys personal, education, experience, skills, certifications, projects.
    Returns dict with lists: technical, soft, tools, certifications, project_techs, and full_text for TF-IDF.
    """
    result = {
        'technical': [],
        'soft': [],
        'tools': [],
        'certifications': [],
        'project_techs': [],
        'full_text': '',
    }
    # From skills section
    skills = resume_data.get('skills') or {}
    if isinstance(skills, dict):
        for key, val in [('skills_tech', 'technical'), ('skills_soft', 'soft'), ('skills_languages', 'technical')]:
            raw = skills.get(key, '')
            if raw:
                tokens = [x.strip().lower() for x in str(raw).replace(',', ' ').replace(';', ' ').split() if x.strip()]
                result[val].extend(tokens)
    # From experience
    experience = resume_data.get('experience')
    if isinstance(experience, list):
        for exp in experience:
            if isinstance(exp, dict):
                desc = (exp.get('description') or '') + ' ' + (exp.get('role') or '') + ' ' + (exp.get('company') or '')
                result['full_text'] += ' ' + desc
    # From education
    education = resume_data.get('education')
    if isinstance(education, list):
        for edu in education:
            if isinstance(edu, dict):
                result['full_text'] += ' ' + (edu.get('degree') or '') + ' ' + (edu.get('institution') or '')
    # From projects
    projects = resume_data.get('projects')
    if isinstance(projects, list):
        for proj in projects:
            if isinstance(proj, dict):
                result['full_text'] += ' ' + (proj.get('title') or '') + ' ' + (proj.get('description') or '')
                tech = proj.get('tech', '')
                if tech:
                    result['project_techs'].extend([x.strip().lower() for x in str(tech).replace(',', ' ').split() if x.strip()])
    # From personal summary
    personal = resume_data.get('personal') or {}
    if isinstance(personal, dict) and personal.get('summary'):
        result['full_text'] += ' ' + str(personal['summary'])
    # From certifications
    certifications = resume_data.get('certifications')
    if isinstance(certifications, list):
        for cert in certifications:
            name = ''
            if isinstance(cert, dict):
                name = cert.get('name') or cert.get('title') or ''
            elif isinstance(cert, str):
                name = cert
            if name:
                result['certifications'].append(name.strip().lower())
                result['full_text'] += ' ' + name
    # Dedupe
    result['technical'] = list(dict.fromkeys(result['technical'] + result['project_techs']))
    result['soft'] = list(dict.fromkeys(result['soft']))
    result['full_text'] = re.sub(r'[^\w\s]', ' ', result['full_text'].lower())
    result['full_text'] = re.sub(r'\s+', ' ', result['full_text']).strip()
    return result


def get_career_paths(resume_data, top_n=3):
    """
    Transferable Skill Mapping + Career Path Detection.
    Compute similarity (TF-IDF + cosine) between resume and each job cluster; return top N careers with scores.
    """
    data = _load_job_clusters()
    clusters = data.get('clusters', {})
    if not clusters:
        return []

    extracted = extract_skills_full(resume_data)
    resume_doc = extracted['full_text']
    if not resume_doc.strip():
        resume_doc = ' '.join(extracted['technical'] + extracted['soft'])

    cluster_docs = []
    cluster_keys = []
    for key, info in clusters.items():
        skill_list = info.get('skills', [])
        doc = ' '.join(skill_list) + ' ' + (info.get('display_name', '') or '')
        cluster_docs.append(doc)
        cluster_keys.append(key)

    if not resume_doc:
        # Fallback: return first 3 clusters by order
        return [
            {'cluster_key': cluster_keys[i], 'display_name': clusters[cluster_keys[i]].get('display_name', cluster_keys[i]), 'score': 0.3 - i * 0.05}
            for i in range(min(top_n, len(cluster_keys)))
        ]

    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=3000, ngram_range=(1, 2))
        all_docs = [resume_doc] + cluster_docs
        matrix = vectorizer.fit_transform(all_docs)
        sims = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    except Exception as e:
        print(f"TF-IDF Error: {e}")
        # Return fallback rankings if vectorization fails
        return [
            {'cluster_key': cluster_keys[i], 'display_name': clusters[cluster_keys[i]].get('display_name', cluster_keys[i]), 'score': 0.3 - i * 0.05}
            for i in range(min(top_n, len(cluster_keys)))
        ]

    scored = []
    for i, key in enumerate(cluster_keys):
        scored.append({
            'cluster_key': key,
            'display_name': clusters[key].get('display_name', key),
            'score': round(float(sims[i]), 4),
        })
    scored.sort(key=lambda x: x['score'], reverse=True)
    return scored[:top_n]


def get_layout_and_theme_for_career(cluster_key):
    """Return (layout, theme) for a career key for PDF generation."""
    data = _load_job_clusters()
    layout = (data.get('layout_by_career') or {}).get(cluster_key, 'one_column')
    theme = (data.get('theme_by_career') or {}).get(cluster_key, 'corporate')
    return layout, theme


def get_transferable_alternatives(cluster_key):
    """Return list of transferable career keys for a given cluster."""
    data = _load_job_clusters()
    clusters = data.get('clusters', {})
    info = clusters.get(cluster_key, {})
    return info.get('transferable_to', [])


def get_cluster_keywords_summary(cluster_key):
    """Return list of role-specific keywords for summary adaptation."""
    data = _load_job_clusters()
    clusters = data.get('clusters', {})
    info = clusters.get(cluster_key, {})
    return info.get('keywords_summary', [])


def get_cluster_skills(cluster_key):
    """Return list of skills for a career cluster (for skill reordering)."""
    data = _load_job_clusters()
    clusters = data.get('clusters', {})
    info = clusters.get(cluster_key, {})
    return [s.lower() for s in info.get('skills', [])]
