"""
Resume orchestration: load resume + sections for editor/PDF/DOCX/JSON export.
Uses Resume and ResumeSection models; design stored in resume.design JSON.
"""
from app.models.resume import Resume, ResumeSection


def get_resume_with_sections(resume_id):
    """Returns (resume dict, sections dict) or (None, None)."""
    resume = Resume.get_by_id(resume_id)
    if not resume:
        return None, None
    sections_list = ResumeSection.get_all_by_resume(resume_id)
    sections = {}
    for sec in sections_list:
        sections[sec['section_name']] = sec['section_content']
    return resume, sections


def sections_for_export(resume_id):
    """Same as get_resume_with_sections; alias for download/export flows."""
    return get_resume_with_sections(resume_id)


def get_resume_json_export(resume_id):
    """Return full resume + sections as a single JSON-serializable dict (for JSON download)."""
    resume, sections = get_resume_with_sections(resume_id)
    if not resume:
        return None
    return {
        'title': resume.get('title'),
        'language': resume.get('language'),
        'target_role': resume.get('target_role'),
        'design': resume.get('design'),
        'photo_path': resume.get('photo_path'),
        'sections': sections,
    }
