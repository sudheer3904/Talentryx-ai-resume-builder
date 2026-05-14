"""
Evidence Locker model: links resume claims to certificates/links/documents.
Used for proof records; display subtle icons in preview, hide in print mode.
"""
from app.database.db import get_db
import json

class Evidence:
    @staticmethod
    def get_all_by_resume(resume_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM evidence WHERE resume_id = %s ORDER BY id ASC",
            (resume_id,)
        )
        return cursor.fetchall()

    @staticmethod
    def add(resume_id, claim_text, evidence_link, evidence_type='Certificate', document_path=None):
        db = get_db()
        cursor = db.cursor()
        # Use only base-schema columns so it works before running update_schema.py
        cursor.execute(
            """INSERT INTO evidence (resume_id, claim_text, evidence_link, evidence_type)
               VALUES (%s, %s, %s, %s)""",
            (resume_id, claim_text, evidence_link or None, evidence_type)
        )
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def delete(evidence_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM evidence WHERE id = %s", (evidence_id,))
        db.commit()

    @staticmethod
    def update(evidence_id, claim_text=None, evidence_link=None, evidence_type=None, document_path=None):
        db = get_db()
        cursor = db.cursor()
        updates, params = [], []
        if claim_text is not None:
            updates.append("claim_text = %s")
            params.append(claim_text)
        if evidence_link is not None:
            updates.append("evidence_link = %s")
            params.append(evidence_link)
        if evidence_type is not None:
            updates.append("evidence_type = %s")
            params.append(evidence_type)
        if not updates:
            return
        params.append(evidence_id)
        cursor.execute(
            "UPDATE evidence SET " + ", ".join(updates) + " WHERE id = %s",
            tuple(params)
        )
        db.commit()
