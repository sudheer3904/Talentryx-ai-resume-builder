"""
Legacy file service: delegates to qr_service and pdf_service for backward compatibility.
"""
from app.services.qr_service import QRService
from app.services.pdf_service import generate_pdf as _generate_pdf


class FileService:
    """Kept for backward compatibility; use QRService and pdf_service directly in new code."""

    @staticmethod
    def generate_qr_base64(data):
        return QRService.generate_base64(data)

    @staticmethod
    def generate_pdf(resume_data, sections, theme='technical', translations=None, format_type=None):
        return _generate_pdf(resume_data, sections, theme, translations, format_type)
