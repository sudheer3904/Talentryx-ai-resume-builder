from app import create_app
from app.database.db import init_db
from app.database.seed_jobs import seed_jobs
from app.database.seed_courses import seed_courses
import mysql.connector
from config import Config

def create_database():
    try:
        # Connect explicitly to mysql server to create the db
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.MYSQL_DB}")
        print(f"Database '{Config.MYSQL_DB}' created or already exists.")
        conn.close()
    except Exception as e:
        print(f"Failed to create database: {e}")

app = create_app()

def setup():
    # 1. Create DB if not exists
    create_database()
    
    # 2. Init Tables and Seed Data
    with app.app_context():
        print("Initializing Database Tables...")
        try:
            init_db()
            print("Database Initialized.")
            
            print("Seeding Jobs...")
            seed_jobs()
            
            print("Seeding Courses...")
            seed_courses()
            
            print("Setup Complete!")
        except Exception as e:
            print(f"Setup failed during initialization: {e}")

if __name__ == "__main__":
    setup()
