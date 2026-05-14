"""
Schema migration script. Run after initial schema.sql.
Adds: design, photo_path on resumes; evidence.document_path, evidence.created_at;
interviews.answers_json, interviews.questions_used.
"""
from app import create_app
from app.database.db import get_db
import mysql.connector

app = create_app()

def add_column_if_missing(cursor, table, column, definition, friendly_name):
    """Try to add column; ignore if already exists (errno 1060)."""
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        print(f"Added '{friendly_name}' to {table}.")
    except mysql.connector.Error as err:
        if err.errno == 1060:
            print(f"'{friendly_name}' already exists on {table}.")
        else:
            print(f"Error adding '{friendly_name}': {err}")

def update_schema():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        print("Updating Database Schema...")

        add_column_if_missing(cursor, "resumes", "design", "JSON", "design")
        add_column_if_missing(cursor, "resumes", "photo_path", "VARCHAR(255)", "photo_path")

        add_column_if_missing(cursor, "evidence", "document_path", "VARCHAR(255)", "document_path")
        add_column_if_missing(cursor, "evidence", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP", "created_at")

        add_column_if_missing(cursor, "interviews", "answers_json", "JSON", "answers_json")
        add_column_if_missing(cursor, "interviews", "questions_used", "JSON", "questions_used")

        db.commit()
        print("Schema update complete.")

if __name__ == "__main__":
    update_schema()
