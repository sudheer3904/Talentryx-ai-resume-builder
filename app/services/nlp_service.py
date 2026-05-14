"""
NLP service: backward-compatible facade delegating to MLService and ParserService.
Existing routes (analysis, import) continue to work without changes.
"""
from app.services.ml_service import MLService
from app.services.parser_service import ParserService


class NLPService:
    """Delegates to MLService (TF-IDF, ATS, job match, skill gap) and ParserService (PDF/DOCX parse)."""

    def __init__(self):
        self._ml = MLService()

    def clean_text(self, text):
        return self._ml.clean_text(text)

    def extract_resume_text(self, resume_data):
        return self._ml.extract_resume_text(resume_data)

    def calculate_similarity(self, resume_text, job_descriptions):
        return self._ml.calculate_similarity(resume_text, job_descriptions)

    def calculate_ats_score(self, resume_text, sections):
        return self._ml.calculate_ats_score(resume_text, sections)

    def recommend_jobs(self, resume_id):
        results = self._ml.recommend_jobs(resume_id)
        for r in results:
            if 'match_score' not in r:
                r['match_score'] = r.get('score', 0)
        return results

    def extract_skills_list(self, resume_data):
        return self._ml.extract_skills_list(resume_data)

    def analyze_skill_gap(self, resume_id, target_role_name):
        return self._ml.analyze_skill_gap(resume_id, target_role_name)

    def parse_resume(self, file_path, file_ext):
        return ParserService.parse_resume(file_path, file_ext)

    def extract_text_from_pdf(self, file_path):
        return ParserService.extract_text_from_pdf(file_path)

    def extract_text_from_docx(self, file_path):
        return ParserService.extract_text_from_docx(file_path)

    def structure_resume_text(self, text):
        return ParserService.structure_resume_text(text)
