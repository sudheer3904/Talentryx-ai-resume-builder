"""
Mock interview: questions by role + missing skills, keyword-based answer scoring.
Stores history in interviews table. Designed for future ChatGPT API integration.
"""
import re
import json
import os
import random
from app.database.db import get_db

# Legacy role-based question bank (kept for backward compatibility) -----------------
ROLE_QUESTIONS = {
    'general': [
        "Tell me about yourself.",
        "What are your greatest strengths?",
        "Where do you see yourself in 5 years?",
        "Why do you want this role?",
        "Describe a challenging project and how you handled it.",
    ],
    'software engineer': [
        "Explain the difference between TCP and UDP.",
        "What is a REST API?",
        "How do you handle errors in your code?",
        "Describe your experience with version control.",
        "How do you approach code reviews?",
    ],
    'data scientist': [
        "What is overfitting and how do you prevent it?",
        "Explain supervised vs unsupervised learning.",
        "How do you handle missing data?",
        "Describe a time you communicated insights to non-technical stakeholders.",
    ],
    'frontend developer': [
        "How do you ensure a web app is accessible?",
        "Explain the difference between responsive and adaptive design.",
        "How do you optimize frontend performance?",
    ],
    'devops engineer': [
        "Explain CI/CD and how you have used it.",
        "How do you secure containers and orchestration?",
        "Describe your experience with infrastructure as code.",
    ],
    'full stack developer': [
        "How do you balance frontend and backend priorities?",
        "Describe your approach to API design.",
    ],
    'project manager': [
        "How do you handle scope creep?",
        "Describe your experience with Agile or Scrum.",
        "How do you resolve conflict within a team?",
    ],
}

# Keywords per question (optional): used to score answer relevance. Key = question text or index.
ANSWER_KEYWORDS = {
    "rest api": ["rest", "api", "http", "get", "post", "stateless", "resource"],
    "tcp": ["tcp", "reliable", "connection", "udp", "packets"],
    "overfitting": ["overfitting", "validation", "cross-validation", "regularization", "bias", "variance"],
    "supervised": ["labeled", "supervised", "unsupervised", "training", "target"],
    "ci/cd": ["ci", "cd", "pipeline", "automation", "deploy", "jenkins", "github actions"],
}


def _keyword_score(question_lower, answer_lower):
    """Simple keyword scoring: count relevant keywords found in answer. Returns 0-100."""
    for qkey, keywords in ANSWER_KEYWORDS.items():
        if qkey in question_lower:
            found = sum(1 for k in keywords if k in answer_lower)
            return min(100, 20 + found * 25)
    # Generic: length and common action words
    words = answer_lower.split()
    if len(words) < 10:
        return 30
    if len(words) < 30:
        return 50
    action = ["developed", "led", "implemented", "designed", "analyzed", "managed", "improved"]
    if any(a in answer_lower for a in action):
        return 70
    return 55


# JSON-based question bank ---------------------------------------------------------

_QUESTION_BANK_CACHE = None


def _load_question_bank():
    """
    Load JSON question bank from app/data/interview_questions.json.
    Loads from disk every time so updates reflect immediately.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, 'data', 'interview_questions.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def get_questions_for_role(role, missing_skills=None, limit=10):
    """
    Returns list of question strings for the role. If missing_skills provided,
    prepends "How did you use / learn [skill]?" style questions (max 3).
    """
    role_lower = (role or 'general').lower().strip()
    questions = list(ROLE_QUESTIONS.get(role_lower, ROLE_QUESTIONS['general']))
    questions = questions + ROLE_QUESTIONS['general'][:2]
    # Add missing-skill questions
    if missing_skills and len(missing_skills) > 0:
        for skill in missing_skills[:3]:
            questions.insert(0, f"How have you used or learned {skill}?")
    return questions[:limit]


def get_questions_for_career(cluster_key, missing_skills=None, limit=35):
    """
    Career-specific question selection using JSON bank and missing skills.
    cluster_key: e.g. 'frontend_developer', 'ui_ux_designer'.
    Returns ordered list of up to 20 technical + 10 behavioral questions.
    """
    bank = _load_question_bank() or {}
    entry = bank.get(cluster_key) or {}
    technical = list(entry.get('technical') or [])
    behavioral = list(entry.get('behavioral') or [])

    questions = []

    # 1) Missing-skill prompts (up to 3) at the top
    if missing_skills:
        for skill in missing_skills[:3]:
            questions.append(f"How have you used or learned {skill} in your projects?")

    # 2) Mix technical and behavioral questions
    random.shuffle(technical)
    random.shuffle(behavioral)

    desired_tech = min(20, len(technical))
    desired_beh = min(10, len(behavioral))

    questions.extend(technical[:desired_tech])
    questions.extend(behavioral[:desired_beh])

    # 3) Fallback to legacy role-based questions if still short and no bank entry exists
    if len(questions) < 5:
        legacy_role = cluster_key.replace('_', ' ')
        legacy_extra = get_questions_for_role(legacy_role, missing_skills=None, limit=limit)
        for q in legacy_extra:
            if q not in questions:
                questions.append(q)
            if len(questions) >= limit:
                break

    return questions[:limit]


def score_answer(question, answer):
    """Returns a score 0-100 and short feedback. Uses keyword scoring."""
    if not (answer or str(answer).strip()):
        return 0, "Please provide an answer."
    q_lower = (question or "").lower()
    a_lower = (answer or "").lower().strip()
    score = _keyword_score(q_lower, a_lower)
    word_count = len(a_lower.split())
    if word_count < 10:
        score = min(score, 40)
        feedback = "Try to elaborate more with specific examples."
    elif word_count > 100:
        feedback = "Good depth. Consider being concise in an actual interview."
    else:
        feedback = "Good answer." if score >= 60 else "Add more relevant keywords or examples."
    return min(100, score), feedback


def summarize_answers(answers):
    """
    Derive simple strengths / improvement areas from per-question scores.
    answers: list[{question, answer, score, feedback}]
    """
    if not answers:
        return [], [], []
    strengths = []
    weaknesses = []
    for a in answers:
        q = (a.get('question') or '').strip()
        s = a.get('score', 0)
        if not q:
            continue
        if s >= 70:
            strengths.append(q)
        elif s <= 50:
            weaknesses.append(q)

    # Very lightweight course suggestions based on weak areas keywords
    courses = []
    joined = " ".join(weaknesses).lower()
    if any(k in joined for k in ["react", "frontend", "hooks", "dom"]):
        courses.append("Advanced React & Frontend Architecture")
    if any(k in joined for k in ["performance", "optimiz"]):
        courses.append("Web Performance Optimization")
    if any(k in joined for k in ["testing", "selenium", "regression"]):
        courses.append("Test Automation with Selenium and PyTest")

    return strengths, weaknesses, courses


def save_interview(user_id, job_role, total_score, feedback_summary, answers_json, questions_used):
    """Persist interview to DB. Works with base schema (no JSON columns) or after migration."""
    db = get_db()
    cursor = db.cursor()
    try:
        ajs = json.dumps(answers_json) if isinstance(answers_json, list) else answers_json
        qjs = json.dumps(questions_used) if isinstance(questions_used, list) else questions_used
        cursor.execute(
            """INSERT INTO interviews (user_id, job_role, score, feedback, answers_json, questions_used)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user_id, job_role, total_score, feedback_summary or '', ajs, qjs)
        )
    except Exception:
        # Base schema has no answers_json, questions_used - insert only base columns
        cursor.execute(
            """INSERT INTO interviews (user_id, job_role, score, feedback)
               VALUES (%s, %s, %s, %s)""",
            (user_id, job_role, total_score, feedback_summary or '')
        )
    db.commit()
    return cursor.lastrowid
