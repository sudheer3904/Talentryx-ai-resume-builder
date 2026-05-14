"""
PDF export using design JSON and role-based theme.
Corporate = ATS-friendly one-column; Technical = two-column; Creative = modern_flow.
QR codes via QRService; UTF-8 encoding for multi-language.
"""
import os
import json
from flask import render_template, current_app  # type: ignore

HAS_PDFKIT = False
try:
    import pdfkit  # type: ignore
    HAS_PDFKIT = True
except ImportError:
    pass

from app.services.qr_service import QRService  # type: ignore


# Map download format/role to template theme and section order
ROLE_THEME_MAP = {
    'corporate': {'theme': 'corporate', 'layout': 'one_column'},
    'technical': {'theme': 'technical', 'layout': 'two_column'},
    'creative': {'theme': 'creative', 'layout': 'modern_flow'},
    'ats': {'theme': 'corporate', 'layout': 'one_column'},
    'minimal': {'theme': 'minimal', 'layout': 'one_column'},
    'academic': {'theme': 'academic', 'layout': 'one_column'},
}


def get_theme_for_role(target_role, format_type=None):
    """
    format_type: 'corporate' | 'technical' | 'creative' (user choice at download).
    target_role: resume's target_role (e.g. "Software Engineer").
    """
    if format_type:
        fmt = format_type.lower()
        if fmt in ROLE_THEME_MAP:
            return ROLE_THEME_MAP[fmt]['theme']
    role = (target_role or '').lower()
    if 'developer' in role or 'engineer' in role:
        return 'technical'
    if 'research' in role or 'scientist' in role:
        return 'research'
    return 'corporate'


def generate_pdf(resume_data, sections, theme='corporate', translations=None, format_type=None):
    """
    Generate PDF from resume_data (includes design, photo_path) and sections dict.
    theme can be overridden by format_type (corporate/technical/creative).
    """
    design = resume_data.get('design')
    if isinstance(design, str):
        try:
            design = json.loads(design)
        except Exception:
            design = {}
    design = design or {}

    import typing
    design_dict = typing.cast(typing.Dict[str, typing.Any], design if isinstance(design, dict) else {})

    # Override layout by format type for role-based download
    if format_type:
        fmt = format_type.lower()
        if fmt in ROLE_THEME_MAP:
            design_dict = {**design_dict, 'layout': ROLE_THEME_MAP[fmt]['layout']}
            theme = ROLE_THEME_MAP[fmt]['theme']

    qr_codes = QRService.get_qr_codes_for_resume(sections.get('personal', {}))

    photo_path = resume_data.get('photo_path')
    if photo_path:
        abs_path = os.path.join(current_app.static_folder, photo_path)
        if not os.path.exists(abs_path):
            photo_path = None
        else:
            photo_path = abs_path.replace('\\', '/')

    try:
        layout_color = design_dict.get('color') or '#2c3e50'
        main_color = design_dict.get('color') or '#000'
        font_family = design_dict.get('font') or "'Helvetica', 'Arial', sans-serif"
        line_height = design_dict.get('spacing') or 1.4
        font_size = design_dict.get('fontSize') or 10.5
        
        custom_css = f"""
        <style>
        body {{
            font-family: {font_family};
            line-height: {line_height};
            font-size: {font_size}pt;
        }}
        h1, h2, h3, .section-title {{
            color: {main_color};
        }}
        h2.section-title {{
            border-bottom: 2.5px solid {main_color};
        }}
        .layout-modern_flow .header-container,
        .theme-creative .header-container {{
            background-color: {layout_color};
        }}
        .layout-modern_flow h2.section-title::after,
        .theme-creative h2.section-title::after {{
            background: {layout_color};
        }}
        </style>
        """
        template_file = 'resume/pdf_template.html'
        selected_template = design_dict.get('template')
        if selected_template:
            template_file = f'resume_templates/{selected_template}.html'
            
        html_content = render_template(
            template_file,
            resume=resume_data,
            sections=sections,
            theme=theme,
            qr_codes=qr_codes,
            photo_path=photo_path,
            design=design_dict,
            custom_css=custom_css,
            t=translations or {},
        )
    except Exception as e:
        import traceback
        print(f"PDF template error: {e}")
        traceback.print_exc()
        return None

    options = {
        'page-size': 'A4',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': None,
    }

    if HAS_PDFKIT:
        import pdfkit as _pdfkit  # type: ignore
        wkhtmltopdf_path = current_app.config.get('WKHTMLTOPDF_PATH') or r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
        if not os.path.exists(wkhtmltopdf_path):
            wkhtmltopdf_path = 'wkhtmltopdf'
        config = _pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
        try:
            return _pdfkit.from_string(html_content, False, options=options, configuration=config)
        except Exception as e:
            import traceback
            print(f"PDF generation error: {e}")
            traceback.print_exc()
            return None
    return None


def _strip_html(text):
    """Remove HTML tags for plain-text DOCX content."""
    if not text:
        return ''
    import re
    return re.sub(r'<[^>]+>', '', str(text)).replace('&nbsp;', ' ').strip()

def generate_docx(resume_data, sections, translations=None):
    """
    Generate DOCX using python-docx. Layout follows design.layout hint;
    sections rendered in order: personal, summary, experience, education, skills, projects, etc.
    """
    try:
        from docx import Document  # type: ignore
        from docx.shared import Pt  # type: ignore
        from docx.enum.text import WD_ALIGN_PARAGRAPH  # type: ignore
    except ImportError:
        print("python-docx not installed")
        return None

    doc = Document()
    style = doc.styles['Normal']
    style.font.size = Pt(11)

    personal = sections.get('personal', {})
    name = personal.get('full_name', '')
    if name:
        p = doc.add_paragraph()
        run = p.add_run(name)
        run.bold = True
        run.font.size = Pt(18)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    contact_parts = []
    if personal.get('email'):
        contact_parts.append(personal['email'])
    if personal.get('phone'):
        contact_parts.append(personal['phone'])
    if personal.get('location'):
        contact_parts.append(personal['location'])
    if contact_parts:
        doc.add_paragraph(' | '.join(contact_parts), style='Normal').alignment = WD_ALIGN_PARAGRAPH.CENTER

    if personal.get('summary'):
        doc.add_paragraph('Summary', style='Heading 2')
        doc.add_paragraph(_strip_html(personal['summary']))

    def add_section(title, items, item_to_para):
        if not items:
            return
        doc.add_paragraph(title, style='Heading 2')
        for it in items:
            doc.add_paragraph(item_to_para(it))

    add_section('Experience', sections.get('experience', []), lambda e: f"{e.get('company', '')} — {e.get('role', '')}\n{e.get('start', '')} - {e.get('end', '')}\n{_strip_html(e.get('description', ''))}")
    add_section('Education', sections.get('education', []), lambda e: f"{e.get('institution', '')} — {e.get('degree', '')} ({e.get('year', '')})")
    add_section('Projects', sections.get('projects', []), lambda p: f"{p.get('title', '')}\n{p.get('tech', '')}\n{_strip_html(p.get('description', ''))}")

    skills = sections.get('skills', {})
    if isinstance(skills, dict) and (skills.get('skills_tech') or skills.get('skills_soft')):
        doc.add_paragraph('Skills', style='Heading 2')
        parts = []
        if skills.get('skills_tech'):
            parts.append(f"Technical: {skills['skills_tech']}")
        if skills.get('skills_soft'):
            parts.append(f"Soft: {skills['skills_soft']}")
        doc.add_paragraph('\n'.join(parts))

    import io
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()
