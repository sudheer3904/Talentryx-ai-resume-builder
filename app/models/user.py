from app.database.db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

class User:
    def __init__(self, id, username, email, password_hash):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash

    @staticmethod
    def create(username, email, password):
        db = get_db()
        cursor = db.cursor()
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, hashed_pw)
            )
            db.commit()
            return True
        except mysql.connector.Error as e:
            # Handle duplicate entry or other errors
            print(f"Error creating user: {e}")
            return False

    @staticmethod
    def get_by_email(email):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash']
            )
        return None

    @staticmethod
    def get_by_id(user_id):
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                password_hash=user_data['password_hash']
            )
        return None

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_password(self, new_password):
        db = get_db()
        cursor = db.cursor()
        hashed_pw = generate_password_hash(new_password, method='pbkdf2:sha256')
        try:
            cursor.execute("UPDATE users SET password_hash = %s WHERE id = %s", (hashed_pw, self.id))
            db.commit()
            self.password_hash = hashed_pw
            return True
        except mysql.connector.Error as e:
            print(f"Error updating password: {e}")
            return False
