from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app.routes.auth import login_required
from app.services.interview_service import (
    get_questions_for_role,
    score_answer,
    save_interview,
    summarize_answers,
    get_questions_for_career,
    ROLE_QUESTIONS,
)
from app.services.career_mapping_service import _load_job_clusters, get_cluster_keywords_summary

bp = Blueprint('interview', __name__, url_prefix='/interview')


@bp.route('/setup')
@login_required
def setup():
    """Setup page: optional resume_id to pull role + missing skills for tailored questions."""
    return render_template('interview/setup.html')


@bp.route('/career/<string:cluster_key>/start/<int:resume_id>')
@login_required
def career_start(cluster_key, resume_id):
    """
    Entry page for a career-specific mock interview triggered from multi-career UI.
    Shows brief description and Start Interview button.
    """
    clusters = (_load_job_clusters() or {}).get('clusters', {})
    info = clusters.get(cluster_key, {})
    display_name = info.get('display_name', cluster_key.replace('_', ' ').title())
    keywords = get_cluster_keywords_summary(cluster_key) or []
    match_score = request.args.get('score')
    return render_template(
        'interview/interview_start.html',
        cluster_key=cluster_key,
        resume_id=resume_id,
        display_name=display_name,
        keywords=keywords,
        match_score=match_score,
    )


@bp.route('/career/<string:cluster_key>/begin', methods=['POST'])
@login_required
def career_begin(cluster_key):
    """
    Initialize a career-specific interview session:
    - Use MLService to get missing skills for this career
    - Generate mixed technical/behavioral questions
    - Store in session and render structured session UI
    """
    resume_id = request.form.get('resume_id')
    if not resume_id or not str(resume_id).isdigit():
        return redirect(url_for('resume.dashboard'))

    clusters = (_load_job_clusters() or {}).get('clusters', {})
    info = clusters.get(cluster_key, {})
    display_name = info.get('display_name', cluster_key.replace('_', ' ').title())

    # Missing skills via MLService gap analysis for this specific career
    missing_skills = []
    try:
        from app.services.ml_service import MLService

        ml = MLService()
        gap = ml.analyze_skill_gap(int(resume_id), display_name)
        if gap:
            missing_skills = gap.get('missing_skills', []) or []
    except Exception:
        missing_skills = []

    questions = get_questions_for_career(cluster_key, missing_skills=missing_skills)
    session['interview_role'] = display_name
    session['interview_career_key'] = cluster_key
    session['interview_questions'] = questions
    session['interview_q_index'] = 0
    session['interview_answers'] = []

    return render_template(
        'interview/interview_session.html',
        role=display_name,
        total_questions=len(questions),
    )


@bp.route('/roles')
@login_required
def list_roles():
    """Return list of role names for dropdown (from question bank)."""
    roles = sorted(ROLE_QUESTIONS.keys())
    return jsonify({'roles': roles})


@bp.route('/start', methods=['POST'])
@login_required
def start():
    try:
        j = request.get_json(silent=True) or {}
    except Exception:
        j = {}
    role = (request.form.get('role') or j.get('role') or 'general').lower().strip()
    resume_id = request.form.get('resume_id') or j.get('resume_id')
    missing_skills = []
    if resume_id and str(resume_id).isdigit():
        from app.services.ml_service import MLService
        ml = MLService()
        recs = ml.recommend_jobs(int(resume_id))
        if recs:
            gap = ml.analyze_skill_gap(int(resume_id), recs[0]['role'])
            if gap:
                missing_skills = gap.get('missing_skills', [])
    questions = get_questions_for_role(role, missing_skills=missing_skills)
    session['interview_role'] = role
    session['interview_questions'] = questions
    session['interview_q_index'] = 0
    session['interview_answers'] = []
    return render_template('interview/chat.html', role=role, total_questions=len(questions))


@bp.route('/next_question', methods=['POST'])
@login_required
def next_question():
    questions = session.get('interview_questions', [])
    index = session.get('interview_q_index', 0)
    if index < len(questions):
        question = questions[index]
        session['interview_q_index'] = index + 1
        return jsonify({'status': 'continue', 'question': question, 'index': index + 1, 'total': len(questions)})
    return jsonify({'status': 'finished', 'message': 'Interview complete!'})


@bp.route('/submit_answer', methods=['POST'])
@login_required
def submit_answer():
    data = request.get_json() or {}
    answer = data.get('answer', '')
    question = data.get('question', '')
    score, feedback = score_answer(question, answer)
    answers = session.get('interview_answers', [])
    answers.append({'question': question, 'answer': answer, 'score': score, 'feedback': feedback})
    session['interview_answers'] = answers
    return jsonify({'feedback': feedback, 'score': score})


@bp.route('/finish', methods=['POST'])
@login_required
def finish():
    """Called when interview ends: compute overall score and persist to DB."""
    answers = session.get('interview_answers', [])
    role = session.get('interview_role', 'general')
    questions = session.get('interview_questions', [])
    if not answers:
        return jsonify({'status': 'error', 'message': 'No answers to save'}), 400
    total = sum(a.get('score', 0) for a in answers)
    avg_score = round(total / len(answers), 2)
    strengths, weaknesses, courses = summarize_answers(answers)
    feedback_summary = f"Average score: {avg_score}. Answered {len(answers)} questions."
    try:
        save_interview(
            session['user_id'],
            role,
            avg_score,
            feedback_summary,
            answers,
            questions,
        )
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    # Persist last-result snapshot for result page
    session['interview_last_result'] = {
        'role': role,
        'score': avg_score,
        'answers': answers,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'courses': courses,
    }
    session.pop('interview_answers', None)
    session.pop('interview_questions', None)
    session.pop('interview_q_index', None)
    return jsonify(
        {
            'status': 'success',
            'score': avg_score,
            'message': 'Interview saved.',
            'strengths': strengths,
            'weaknesses': weaknesses,
            'courses': courses,
        }
    )


@bp.route('/result')
@login_required
def result():
    """Render last interview result summary."""
    data = session.get('interview_last_result')
    if not data:
        return redirect(url_for('resume.dashboard'))
    return render_template(
        'interview/interview_result.html',
        role=data.get('role', 'Interview'),
        score=data.get('score', 0),
        strengths=data.get('strengths', []),
        weaknesses=data.get('weaknesses', []),
        courses=data.get('courses', []),
    )
