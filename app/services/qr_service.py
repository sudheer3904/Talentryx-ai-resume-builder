"""
QR Code service: generates base64 PNG QR codes for LinkedIn, GitHub, Portfolio.
Used in PDF export; dual QR display when multiple links available; hide block if none.
"""
import qrcode
import base64
from io import BytesIO


class QRService:
    @staticmethod
    def generate_base64(data, box_size=12, border=4):
        """Generate a single QR code as base64 PNG string. Returns None if data is empty."""
        if not data or not str(data).strip():
            return None
        url = str(data).strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        qr = qrcode.QRCode(
            version=None,
            # Use higher error correction so codes remain scannable
            # even after PDF rendering/compression.
            error_correction=qrcode.constants.ERROR_CORRECT_Q,
            box_size=box_size,
            border=border,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    @staticmethod
    def get_qr_codes_for_resume(personal_section):
        """
        Build dict of link_key -> base64 PNG for LinkedIn, GitHub, Portfolio.
        Only include keys where the user actually provided a link (non-empty).
        Order: linkedin, github, portfolio. Empty dict = hide QR block.
        """
        if not personal_section:
            return {}
        links = [
            ('linkedin', personal_section.get('linkedin')),
            ('github', personal_section.get('github')),
            ('portfolio', personal_section.get('portfolio') or personal_section.get('website')),
        ]
        qr_codes = {}
        for key, url in links:
            if url and str(url).strip():
                qr_codes[key] = QRService.generate_base64(url)
        return qr_codes
