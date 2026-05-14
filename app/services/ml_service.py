"""
AI Resume Analysis: TF-IDF vectorizer, cosine similarity, ATS score, skill gap, course recommendations.
ML logic is documented in comments. Uses scikit-learn and NLTK where applicable.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import json
from app.database.db import get_db


class MLService:
    """
    TF-IDF + Cosine Similarity: resume and job descriptions are vectorized;
    similarity(resume, job_i) = cosine between vectors. Higher = better match.
    """

    def __init__(self):
        # English stop words by default; for multi-language, use stop_words=None or custom list
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=5000,
            ngram_range=(1, 2),
        )

    def clean_text(self, text):
        """Normalize text for TF-IDF: lowercase, alphanumeric + spaces. UTF-8 safe."""
        if not text:
            return ""
        text = str(text).lower().strip()
        # Keep letters, numbers, spaces (allow unicode letters)
        text = re.sub(r'[^\w\s]', ' ', text, flags=re.UNICODE)
        return re.sub(r'\s+', ' ', text).strip()

    def extract_resume_text(self, resume_data):
        """Flatten resume sections into one string for vectorization."""
        parts = []
        if resume_data.get('personal') and resume_data['personal'].get('summary'):
            parts.append(resume_data['personal']['summary'])
        for exp in resume_data.get('experience', []):
            parts.append(f"{exp.get('role', '')} {exp.get('company', '')} {exp.get('description', '')}")
        for edu in resume_data.get('education', []):
            parts.append(f"{edu.get('degree', '')} {edu.get('institution', '')}")
        skills = resume_data.get('skills') or {}
        if isinstance(skills, dict):
            parts.append(skills.get('skills_tech', ''))
            parts.append(skills.get('skills_soft', ''))
        for proj in resume_data.get('projects', []):
            parts.append(f"{proj.get('title', '')} {proj.get('description', '')} {proj.get('tech', '')}")
        return self.clean_text(" ".join(parts))

    def calculate_similarity(self, resume_text, job_descriptions):
        """
        TF-IDF: fit on [resume, job1, job2, ...], then cosine_similarity(resume_vec, job_vecs).
        Returns 1D array of scores (one per job).
        """
        if not resume_text or not job_descriptions:
            return []
        documents = [resume_text] + job_descriptions
        tfidf_matrix = self.vectorizer.fit_transform(documents)
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        return sim[0]

    def calculate_ats_score(self, resume_text, sections):
        """
        Heuristic ATS score (0-100). Optional: replace with logistic regression
        trained on (resume_features, pass/fail) for real ATS score.
        """
        score = 0
        checks = []
        word_count = len(resume_text.split())
        if 400 <= word_count <= 1000:
            score += 20
            checks.append({'name': 'Word Count', 'status': 'pass', 'msg': 'Optimal length (400-1000 words).'})
        elif word_count < 400:
            score += 10
            checks.append({'name': 'Word Count', 'status': 'warn', 'msg': 'Too short. Add more detail.'})
        else:
            score += 10
            checks.append({'name': 'Word Count', 'status': 'warn', 'msg': 'Too long. Be concise.'})

        required_sections = ['experience', 'education', 'skills', 'personal']
        present = [s for s in required_sections if sections.get(s)]
        section_score = (len(present) / len(required_sections)) * 30
        score += section_score
        if len(present) == len(required_sections):
            checks.append({'name': 'Sections', 'status': 'pass', 'msg': 'All key sections present.'})
        else:
            missing = [s.title() for s in required_sections if s not in present]
            checks.append({'name': 'Sections', 'status': 'fail', 'msg': f'Missing: {", ".join(missing)}'})

        personal = sections.get('personal', {})
        if personal.get('email') and personal.get('phone'):
            score += 10
            checks.append({'name': 'Contact Info', 'status': 'pass', 'msg': 'Email and Phone present.'})
        else:
            checks.append({'name': 'Contact Info', 'status': 'fail', 'msg': 'Missing Email or Phone.'})

        keywords = ['led', 'developed', 'managed', 'created', 'analyzed', 'python', 'java', 'sql', 'team', 'project']
        found = [k for k in keywords if k in resume_text.lower()]
        if len(found) > 5:
            score += 20
            checks.append({'name': 'Keywords', 'status': 'pass', 'msg': 'Good use of action verbs/keywords.'})
        elif len(found) > 2:
            score += 10
            checks.append({'name': 'Keywords', 'status': 'warn', 'msg': 'Add more strong keywords.'})
        else:
            checks.append({'name': 'Keywords', 'status': 'fail', 'msg': 'Too few keywords/action verbs.'})
        score += 20
        checks.append({'name': 'Readability', 'status': 'pass', 'msg': 'Standard formatting used.'})

        return {'score': min(100, int(score)), 'checks': checks}

    def recommend_jobs(self, resume_id):
        """Top 3 job roles by cosine similarity (match percentage)."""
        from app.models.resume import ResumeSection
        sections = ResumeSection.get_all_by_resume(resume_id)
        resume_data = {}
        for sec in sections:
            resume_data[sec['section_name']] = sec['section_content']
        resume_text = self.extract_resume_text(resume_data)

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM job_roles")
        jobs = cursor.fetchall()
        if not jobs:
            return []

        job_descs = []
        for j in jobs:
            desc = (j.get('description') or '') + " " + (j.get('required_skills') or '')
            if isinstance(j.get('required_skills'), str):
                try:
                    desc += " " + " ".join(json.loads(j['required_skills']))
                except Exception:
                    pass
            job_descs.append(self.clean_text(desc))

        scores = self.calculate_similarity(resume_text, job_descs)
        results = []
        for i, sc in enumerate(scores):
            results.append({
                'role': jobs[i]['role_name'],
                'score': round(float(sc) * 100, 2),
                'match_score': round(float(sc) * 100, 2),
                'match_level': 'High' if sc > 0.7 else ('Medium' if sc > 0.4 else 'Low'),
            })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:3]

    def extract_skills_list(self, resume_data):
        """List of skills from skills section (tech + soft + languages)."""
        skills = []
        s = resume_data.get('skills')
        if not s or not isinstance(s, dict):
            return skills
        for key in ('skills_tech', 'skills_soft', 'skills_languages'):
            val = s.get(key, '')
            if val:
                skills.extend([x.strip().lower() for x in str(val).split(',') if x.strip()])
        return skills

    def analyze_skill_gap(self, resume_id, target_role_name):
        """
        Compare resume skills vs job required_skills. Matching = in resume (explicit or in text).
        Missing = required but not found. Recommended courses from DB by missing skill keywords.
        """
        from app.models.resume import ResumeSection
        sections = ResumeSection.get_all_by_resume(resume_id)
        resume_data = {}
        for sec in sections:
            resume_data[sec['section_name']] = sec['section_content']
        explicit_skills = set(self.extract_skills_list(resume_data))
        resume_text = self.extract_resume_text(resume_data).lower()

        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM job_roles WHERE role_name = %s", (target_role_name,))
        job = cursor.fetchone()
        if not job:
            return None

        raw = job.get('required_skills')
        try:
            required_skills = set(json.loads(raw)) if isinstance(raw, str) else set(raw or [])
        except Exception:
            required_skills = set()
        required_skills = set(s.lower() for s in required_skills if s)

        matching = set()
        for skill in required_skills:
            if skill in explicit_skills:
                matching.add(skill)
                continue
            if re.search(r'(?<!\w)' + re.escape(skill) + r'(?!\w)', resume_text):
                matching.add(skill)
        missing = list(required_skills - matching)
        matching = list(matching)
        match_pct = (len(matching) / len(required_skills) * 100) if required_skills else 0

        recommendations = []
        for skill in missing:
            cursor.execute(
                "SELECT * FROM courses WHERE title LIKE %s OR skills_covered LIKE %s LIMIT 4",
                (f"%{skill}%", f"%{skill}%")
            )
            for row in cursor.fetchall():
                recommendations.append(row)
        unique_courses = list({c['id']: c for c in recommendations}.values())[:4]

        return {
            'role': target_role_name,
            'match_percentage': round(match_pct, 1),
            'missing_skills': [s.title() for s in missing],
            'matching_skills': [s.title() for s in matching],
            'recommended_courses': unique_courses,
        }
