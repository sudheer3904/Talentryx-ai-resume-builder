from app.database.db import get_db
import mysql.connector
import json

class Resume:
    def __init__(self, id, user_id, title, language, target_role):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.language = language
        self.target_role = target_role

    @staticmethod
    def create(user_id, title, language='English', target_role='General'):
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute(
                "INSERT INTO resumes (user_id, title, language, target_role) VALUES (%s, %s, %s, %s)",
                (user_id, title, language, target_role)
            )
            resume_id = cursor.lastrowid
            db.commit()
            return resume_id
        except mysql.connector.Error as e:
            print(f"Error creating resume: {e}")
            return None

    @staticmethod
    def get_all_by_user(user_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM resumes WHERE user_id = %s ORDER BY updated_at DESC", (user_id,))
        return cursor.fetchall()

    @staticmethod
    def get_by_id(resume_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM resumes WHERE id = %s", (resume_id,))
        resume = cursor.fetchone()
        if resume and resume.get('design'):
            try:
                resume['design'] = json.loads(resume['design'])
            except Exception:
                resume['design'] = {}
        elif resume:
            resume['design'] = {}
        return resume

    @staticmethod
    def update(resume_id, title, language, target_role, design=None, photo_path=None):
        db = get_db()
        cursor = db.cursor()
        query = "UPDATE resumes SET title=%s, language=%s, target_role=%s"
        params = [title, language, target_role]
        if design is not None:
            query += ", design=%s"
            params.append(json.dumps(design) if isinstance(design, dict) else design)
        if photo_path:
            query += ", photo_path=%s"
            params.append(photo_path)
        query += " WHERE id=%s"
        params.append(resume_id)
        try:
            cursor.execute(query, tuple(params))
        except mysql.connector.Error as e:
            # If design or photo_path column doesn't exist (schema not migrated), update without them
            if e.errno == 1054:  # Unknown column
                query = "UPDATE resumes SET title=%s, language=%s, target_role=%s WHERE id=%s"
                cursor.execute(query, (title, language, target_role, resume_id))
            else:
                raise
        db.commit()

    @staticmethod
    def delete(resume_id):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM resumes WHERE id = %s", (resume_id,))
        db.commit()

class ResumeSection:
    @staticmethod
    def get_all_by_resume(resume_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM resume_sections WHERE resume_id = %s ORDER BY sort_order ASC", (resume_id,))
        sections = cursor.fetchall()
        for s in sections:
            raw = s.get('section_content')
            if raw:
                try:
                    s['section_content'] = json.loads(raw)
                except (TypeError, ValueError):
                    s['section_content'] = None
        return sections

    @staticmethod
    def update_or_create(resume_id, section_name, content, sort_order):
        db = get_db()
        cursor = db.cursor()
        try:
            content_json = json.dumps(content, default=str)
        except (TypeError, ValueError):
            content_json = "{}"
        cursor.execute(
            "SELECT id FROM resume_sections WHERE resume_id=%s AND section_name=%s",
            (resume_id, section_name)
        )
        existing = cursor.fetchone()
        row_id = existing[0] if existing else None
        if row_id is not None:
            cursor.execute(
                "UPDATE resume_sections SET section_content=%s, sort_order=%s WHERE id=%s",
                (content_json, sort_order, row_id)
            )
        else:
            cursor.execute(
                "INSERT INTO resume_sections (resume_id, section_name, section_content, sort_order) VALUES (%s, %s, %s, %s)",
                (resume_id, section_name, content_json, sort_order)
            )
        db.commit()
