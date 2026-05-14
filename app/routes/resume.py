from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from app.routes.auth import login_required
from app.models.resume import Resume, ResumeSection
import json

bp = Blueprint('resume', __name__)

@bp.route('/resume/translations/<string:lang>')
def get_translations_json(lang):
    from app.utils.translations import get_translations
    return jsonify(get_translations(lang))

@bp.route('/templates-gallery')
def global_templates_gallery():
    # Global template gallery (without specific resume)
    from app.services.template_service import CATEGORIES
    return render_template('resume/templates_gallery.html', categories=CATEGORIES, resume=None)

@bp.route('/select_template', methods=['POST'])
def global_select_template():
    # Global select template, simply setting the session as requested
    data = request.json or {}
    session['selected_template'] = data.get('template')
    return {"status": "success"}

@bp.route('/resume/<int:resume_id>/templates-gallery')
@login_required
def templates_gallery(resume_id):
    resume = Resume.get_by_id(resume_id)
    if not resume or resume['user_id'] != session['user_id']:
        return redirect(url_for('resume.dashboard'))
    
    from app.services.template_service import CATEGORIES
    return render_template('resume/templates_gallery.html', resume=resume, categories=CATEGORIES)

@bp.route('/resume/<int:resume_id>/template-preview/<template_name>')
@login_required
def template_preview(resume_id, template_name):
    from app.services.resume_service import get_resume_with_sections
    from app.services.qr_service import QRService
    from app.services.template_service import get_template_layout_and_theme
    import os
    
    resume, sections = get_resume_with_sections(resume_id)
    if not resume or resume['user_id'] != session['user_id']:
        return redirect(url_for('resume.dashboard'))
    
    from app.utils.translations import get_translations
    lang = resume.get('language', 'English')
    translations = get_translations(lang)
    
    design = resume.get('design')
    if isinstance(design, str):
        try:
            design = json.loads(design)
        except:
            design = {}
    if not design:
        design = {}
        
    layout, theme = get_template_layout_and_theme(template_name)
    design['layout'] = layout
    design['template'] = template_name
    
    qr_codes = QRService.get_qr_codes_for_resume(sections.get('personal', {}))
    
    photo_path = resume.get('photo_path')
    if photo_path:
        abs_path = os.path.join(current_app.static_folder, photo_path)
        if not os.path.exists(abs_path):
            photo_path = None
        else:
            photo_path = abs_path.replace('\\', '/')
            
    return render_template(
        f'resume_templates/{template_name}.html', 
        resume=resume, 
        sections=sections, 
        t=translations, 
        theme=theme,
        design=design,
        qr_codes=qr_codes,
        photo_path=photo_path
    )

@bp.route('/api/render-dummy-template/<template_name>', methods=['POST'])
def render_dummy_template(template_name):
    """Render a template using provided dummy JSON data, bypassing database."""
    from app.services.template_service import get_template_layout_and_theme
    from app.utils.translations import get_translations
    
    data = request.json or {}
    resume_data = data.get('resume', {})
    sections_data = data.get('sections', {})
    
    layout, theme = get_template_layout_and_theme(template_name)
    design = resume_data.get('design', {})
    design['layout'] = layout
    design['template'] = template_name
    
    lang = resume_data.get('language', 'English')
    translations = get_translations(lang)
    
    return render_template(
        f'resume_templates/{template_name}.html', 
        resume=resume_data, 
        sections=sections_data, 
        t=translations, 
        theme=theme,
        design=design,
        qr_codes=None,
        photo_path=None
    )

@bp.route('/resume/<int:resume_id>/select-template/<template_name>', methods=['POST'])
@login_required
def select_template(resume_id, template_name):
    resume = Resume.get_by_id(resume_id)
    if not resume or resume['user_id'] != session['user_id']:
        return jsonify({'status': 'error', 'message': 'Forbidden'}), 403
    
    design = resume.get('design')
    if isinstance(design, str):
        try:
            design = json.loads(design)
        except:
            design = {}
    if not design:
        design = {}
    
    from app.services.template_service import get_template_layout_and_theme
    layout, theme = get_template_layout_and_theme(template_name)
    
    design['template'] = template_name
    design['layout'] = layout
    
    # Update resume with the new design
    Resume.update(resume_id, resume['title'], resume['language'], resume['target_role'], design=design)
    
    return jsonify({'status': 'success', 'message': 'Template selected'})


@bp.route('/dashboard')
@login_required
def dashboard():
    resumes = Resume.get_all_by_user(session['user_id'])
    return render_template('dashboard.html', resumes=resumes)

@bp.route('/resume/create', methods=('POST',))
@login_required
def create():
    title = request.form['title']
    language = request.form.get('language', 'English')
    resume_id = Resume.create(session['user_id'], title, language)
    if resume_id:
        return redirect(url_for('resume.editor', resume_id=resume_id))
    flash('Error creating resume')
    return redirect(url_for('resume.dashboard'))

@bp.route('/resume/<int:resume_id>/editor')
@login_required
def editor(resume_id):
    resume = Resume.get_by_id(resume_id)
    if not resume or resume['user_id'] != session['user_id']:
        return redirect(url_for('resume.dashboard'))
    
    sections = ResumeSection.get_all_by_resume(resume_id)
    
    # Translations
    from app.utils.translations import get_translations
    lang = resume.get('language', 'English')
    translations = get_translations(lang)
    
    from app.services.template_service import CATEGORIES
    return render_template('resume/editor.html', resume=resume, sections=sections, t=translations, categories=CATEGORIES)

@bp.route('/resume/<int:resume_id>/save', methods=('POST',))
@login_required
def save_resume(resume_id):
    resume = Resume.get_by_id(resume_id)
    if not resume or resume['user_id'] != session['user_id']:
        return jsonify({'status': 'error', 'message': 'Forbidden'}), 403
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data'}), 400
    try:
        from app.utils.security import sanitize_html
        def sanitize_section(content):
            if content is None:
                return None
            if isinstance(content, dict):
                return {str(k): sanitize_html(v) if isinstance(v, str) and k in ('description', 'summary') else (sanitize_section(v) if isinstance(v, (dict, list)) else v) for k, v in content.items()}
            if isinstance(content, list):
                return [sanitize_section(item) for item in content]
            return content
        title = (data.get('title') or '')[:100]
        language = (data.get('language') or 'English')[:20]
        target_role = (data.get('target_role') or '')[:100]
        Resume.update(resume_id, title, language, target_role, design=data.get('design'))
        for i, section in enumerate(data.get('sections', [])):
            name = (section.get('name') or '')[:50]
            if not name:
                continue
            content = sanitize_section(section.get('content'))
            ResumeSection.update_or_create(resume_id, name, content, i)
        return jsonify({'status': 'success', 'message': 'Resume saved!'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/resume/<int:resume_id>/upload_photo', methods=['POST'])
@login_required
def upload_photo(resume_id):
    if 'photo' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        import os
        from werkzeug.utils import secure_filename
        
        filename = secure_filename(f"resume_{resume_id}_{file.filename}")
        save_path = os.path.join(current_app.static_folder, 'uploads', 'photos', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        file.save(save_path)
        
        # Save relative path to DB
        photo_db_path = f"uploads/photos/{filename}"
        
        # Get current resume data to preserve other fields
        # Note: Ideally Resume.update should handle partial updates better, but we'll fetch first
        resume = Resume.get_by_id(resume_id)
        Resume.update(
            resume_id, 
            resume['title'], 
            resume['language'], 
            resume['target_role'],
            design=resume.get('design'), # Verify if this is needed or if None is ignore
            photo_path=photo_db_path
        )
        
        return jsonify({'status': 'success', 'photo_path': url_for('static', filename=photo_db_path)})

@bp.route('/resume/<int:resume_id>/delete', methods=('POST',))
@login_required
def delete(resume_id):
    resume = Resume.get_by_id(resume_id)
    if resume and resume['user_id'] == session['user_id']:
        Resume.delete(resume_id)
        flash('Resume deleted.')
    return redirect(url_for('resume.dashboard'))

@bp.route('/resume/<int:resume_id>/download')
@login_required
def download_pdf(resume_id):
    """Legacy: download as PDF with default theme. Prefer /resume/<id>/download/<format>?format_type=..."""
    return download_resume(resume_id, 'pdf')


@bp.route('/resume/<int:resume_id>/download/<format_type>')
@login_required
def download_resume(resume_id, format_type='pdf'):
    """
    Role-based multi-format download. format_type: pdf | docx | json.
    Query param: format_style=corporate|technical|creative (for PDF/DOCX layout).
    """
    from flask import make_response
    from app.services.resume_service import get_resume_with_sections
    from app.services.pdf_service import generate_pdf, get_theme_for_role, generate_docx
    from app.utils.translations import get_translations

    resume, sections = get_resume_with_sections(resume_id)
    if not resume or resume['user_id'] != session['user_id']:
        return redirect(url_for('resume.dashboard'))

    format_style = request.args.get('format_style', '').lower() or None
    theme = get_theme_for_role(resume.get('target_role'), format_style)
    lang = resume.get('language', 'English')
    translations = get_translations(lang)
    safe_title = "".join(c for c in (resume.get('title') or 'resume') if (ord(c) < 128 and c.isalnum()) or c in ' _-')[:80] or 'resume'

    if format_type == 'json':
        from app.services.resume_service import get_resume_json_export
        data = get_resume_json_export(resume_id)
        if not data:
            return redirect(url_for('resume.dashboard'))
        response = make_response(json.dumps(data, indent=2, default=str))
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = f'attachment; filename="{safe_title}.json"'
        return response

    if format_type == 'docx':
        docx_bytes = generate_docx(resume, sections, translations)
        if docx_bytes:
            response = make_response(docx_bytes)
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            response.headers['Content-Disposition'] = f'attachment; filename="{safe_title}.docx"'
            return response
        flash('Error generating DOCX.')
        return redirect(url_for('resume.editor', resume_id=resume_id))

    # PDF (default)
    pdf = generate_pdf(resume, sections, theme, translations, format_style)
    if pdf:
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{safe_title}.pdf"'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    flash('Error generating PDF. Ensure wkhtmltopdf is installed.')
    return redirect(url_for('resume.editor', resume_id=resume_id))

@bp.route('/resume/import', methods=['POST'])
@login_required
def import_resume():
    if 'resume_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'})
    
    file = request.files['resume_file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'})
        
    if file:
        import os
        from werkzeug.utils import secure_filename
        from app.services.nlp_service import NLPService
        
        filename = secure_filename(file.filename)
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext not in ['.pdf', '.docx', '.doc']:
            return jsonify({'status': 'error', 'message': 'Invalid file type. Allowed: PDF, DOCX'})
             
        # Save temp - ensure upload folder exists
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'tmp')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
            
        temp_path = os.path.join(upload_folder, filename)
        file.save(temp_path)
        
        try:
            nlp = NLPService()
            parsed_data = nlp.parse_resume(temp_path, file_ext)
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if parsed_data:
                return jsonify({'status': 'success', 'data': parsed_data})
            else:
                return jsonify({'status': 'error', 'message': 'Could not parse resume text'})
        except Exception as e:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({'status': 'error', 'message': str(e)})

    return jsonify({'status': 'error', 'message': 'Upload failed'})


# ---------- Evidence Locker ----------
@bp.route('/resume/<int:resume_id>/evidence')
@login_required
def list_evidence(resume_id):
    resume = Resume.get_by_id(resume_id)
    if not resume or resume['user_id'] != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403
    from app.models.evidence import Evidence
    items = Evidence.get_all_by_resume(resume_id)
    return jsonify({'status': 'success', 'evidence': items})


@bp.route('/resume/<int:resume_id>/evidence', methods=['POST'])
@login_required
def add_evidence(resume_id):
    resume = Resume.get_by_id(resume_id)
    if not resume or resume['user_id'] != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json() or {}
    claim_text = (data.get('claim_text') or '').strip()[:255]
    evidence_link = (data.get('evidence_link') or '').strip()[:255]
    evidence_type = (data.get('evidence_type') or 'Certificate')[:50]
    if not claim_text:
        return jsonify({'status': 'error', 'message': 'Claim text required'}), 400
    from app.models.evidence import Evidence
    eid = Evidence.add(resume_id, claim_text, evidence_link or None, evidence_type)
    return jsonify({'status': 'success', 'id': eid})


@bp.route('/resume/<int:resume_id>/evidence/<int:evidence_id>', methods=['DELETE'])
@login_required
def delete_evidence(resume_id, evidence_id):
    resume = Resume.get_by_id(resume_id)
    if not resume or resume['user_id'] != session['user_id']:
        return jsonify({'error': 'Forbidden'}), 403
    from app.models.evidence import Evidence
    Evidence.delete(evidence_id)
    return jsonify({'status': 'success'})

# ---------- Translation Engine ----------
@bp.route('/api/resume/translate', methods=['POST'])
@login_required
def translate_resume_content():
    data = request.json or {}
    resume_data = data.get('resumeData')
    target_lang = data.get('targetLang')
    
    if not resume_data or not target_lang:
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400
        
    try:
        from app.services.translation_engine import translation_engine
        translated_data = translation_engine.translateResume(resume_data, target_lang)
        return jsonify({
            'status': 'success',
            'translatedData': translated_data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

