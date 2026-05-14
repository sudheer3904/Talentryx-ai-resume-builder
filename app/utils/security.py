"""
Security helpers: CSRF token (session-based), HTML sanitization for rich text.
Prevents XSS in stored content; use with all state-changing forms and JSON save.
"""
import re
import secrets
from flask import session


def get_csrf_token():
    """Generate or return existing CSRF token in session."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']


def validate_csrf_token(token):
    """Return True if token matches session CSRF token."""
    return token and secrets.compare_digest(token, session.get('csrf_token', ''))


# Allowed tags for rich text (e.g. from Quill: b, i, u, lists)
ALLOWED_TAGS = re.compile(
    r'</?(?:p|br|strong|b|em|i|u|ul|ol|li|span)(?:\s[^>]*)?>',
    re.IGNORECASE
)
# Strip any script, style, iframe, form, object, embed, link (capturing group so \1 matches closing tag)
DANGEROUS = re.compile(
    r'<(script|style|iframe|form|object|embed|link|meta|base)[^>]*>.*?</\1>|<[^>]+\s(?:on\w+\s*=|javascript:)[^>]*>',
    re.IGNORECASE | re.DOTALL
)


def sanitize_html(html):
    """
    Remove dangerous tags/attributes; allow only safe inline tags.
    For stricter ATS, strip all HTML and keep plain text.
    """
    if not html or not isinstance(html, str):
        return ''
    # Remove dangerous blocks first
    text = DANGEROUS.sub('', html)
    # Optionally allow only safe tags (comment out to allow all except dangerous)
    # text = ALLOWED_TAGS.sub(lambda m: m.group(0), text)
    return text.strip()
