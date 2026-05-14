"""
Multi-Career Resume: generate 3 career-specific resumes from one input.
Routes: page, analyze (API), download PDF per version, preview.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, make_response, current_app
from app.routes.auth import login_required
from app.models.resume import Resume, ResumeSection
from app.services.resume_service import get_resume_with_sections
from app.services.career_mapping_service import get_career_paths, get_layout_and_theme_for_career
from app.services.resume_rewrite_service import rewrite_sections_for_career
from app.services.pdf_service import generate_pdf
from app.utils.translations import get_translations
import json

bp = Blueprint('multi_career', __name__, url_prefix='/resume')


def _resume_sections_to_data(resume_id):
    """Build resume_data dict (sections as keys) for career mapping from resume_id."""
    sections_list = ResumeSection.get_all_by_resume(resume_id)
    return {sec['section_name']: sec['section_content'] for sec in sections_list}


@bp.route('/<int:resume_id>/multi-career')
@login_required
def multi_career_page(resume_id):
    """Multi-career resume generator page: analyze and download 3 versions."""
    resume = Resume.get_by_id(resume_id)
    if not resume or resume['user_id'] != session['user_id']:
        return redirect(url_for('resume.dashboard'))
    return render_template('resume/multi_career.html', resume=resume)


@bp.route('/<int:resume_id>/multi-career/analyze', methods=['POST'])
@login_required
def analyze_careers(resume_id):
    """API: analyze resume and return top 3 career paths with scores."""
    resume = Resume.get_by_id(resume_id)
    if not resume or resume['user_id'] != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403
    resume_data = _resume_sections_to_data(resume_id)
    careers = get_career_paths(resume_data, top_n=3)
    return jsonify({
        'status': 'success',
        'careers': [
            {
                'rank': i + 1,
                'cluster_key': c['cluster_key'],
                'display_name': c['display_name'],
                'score': round(c['score'] * 100, 1),
                'label': 'Primary' if i == 0 else ('Transferable' if i == 1 else 'Alternative'),
            }
            for i, c in enumerate(careers)
        ],
    })


@bp.route('/<int:resume_id>/multi-career/preview/<int:version>')
@login_required
def preview_career(resume_id, version):
    """Preview one of the 3 career versions as HTML (no PDF). version in 1..3."""
    resume, sections = get_resume_with_sections(resume_id)
    if not resume or resume['user_id'] != session['user_id']:
        return redirect(url_for('resume.dashboard'))
    
    resume_data = _resume_sections_to_data(resume_id)
    careers = get_career_paths(resume_data, top_n=3)
    if version < 1 or version > len(careers):
        return redirect(url_for('multi_career.multi_career_page', resume_id=resume_id))
    
    career = careers[version - 1]
    cluster_key = career['cluster_key']
    rewritten = rewrite_sections_for_career(sections, cluster_key)
    
    # Defaults from career mapping
    default_layout, theme = get_layout_and_theme_for_career(cluster_key)
    
    # Design handling
    design = resume.get('design') or {}
    if isinstance(design, str):
        try: design = json.loads(design)
        except: design = {}
        
    # User overrides via query params or persistent design
    layout = request.args.get('layout') or design.get('layout') or default_layout
    color = request.args.get('color') or design.get('color') or '#2c3e50'
    
    design = {**design, 'layout': layout, 'color': color}
    lang = resume.get('language', 'English')
    translations = get_translations(lang)
    
    from app.services.qr_service import QRService
    qr_codes = QRService.get_qr_codes_for_resume(rewritten.get('personal', {}))
    photo_path = resume.get('photo_path')
    if photo_path:
        import os
        abs_path = os.path.join(current_app.static_folder, photo_path)
        if os.path.exists(abs_path):
            photo_path = abs_path
        else:
            photo_path = None

    return render_template(
        'resume/pdf_template.html',
        resume={**resume, 'design': design},
        sections=rewritten,
        theme=theme,
        qr_codes=qr_codes,
        photo_path=photo_path,
        design=design,
        t=translations,
    )


@bp.route('/<int:resume_id>/multi-career/download/<int:version>')
@login_required
def download_career_pdf(resume_id, version):
    """Download PDF for career version 1, 2, or 3."""
    resume, sections = get_resume_with_sections(resume_id)
    if not resume or resume['user_id'] != session['user_id']:
        return redirect(url_for('resume.dashboard'))
        
    resume_data = _resume_sections_to_data(resume_id)
    careers = get_career_paths(resume_data, top_n=3)
    if version < 1 or version > len(careers):
        return redirect(url_for('multi_career.multi_career_page', resume_id=resume_id))
        
    career = careers[version - 1]
    cluster_key = career['cluster_key']
    display_name = career['display_name']
    rewritten = rewrite_sections_for_career(sections, cluster_key)
    
    # Defaults from career mapping
    default_layout, theme = get_layout_and_theme_for_career(cluster_key)
    
    # Design handling
    design = resume.get('design') or {}
    if isinstance(design, str):
        try: design = json.loads(design)
        except: design = {}

    # User overrides
    layout = request.args.get('layout') or design.get('layout') or default_layout
    color = request.args.get('color') or design.get('color') or '#2c3e50'
    
    design = {**design, 'layout': layout, 'color': color}
    lang = resume.get('language', 'English')
    translations = get_translations(lang)
    
    pdf = generate_pdf(
        {**resume, 'design': design, 'target_role': display_name},
        rewritten,
        theme=theme,
        translations=translations,
        format_type=None, # Use the layout/color we specifically passed in 'design'
    )
    if not pdf:
        return redirect(url_for('multi_career.multi_career_page', resume_id=resume_id))
        
    safe_title = "".join(c for c in (resume.get('title') or 'resume') if (ord(c) < 128 and c.isalnum()) or c in ' _-')[:60] or 'resume'
    safe_career = "".join(c for c in display_name if (ord(c) < 128 and c.isalnum()) or c in ' _-').replace(' ', '_')
    filename = f"{safe_title}_{safe_career}.pdf"
    
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
