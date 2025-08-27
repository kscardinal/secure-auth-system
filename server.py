import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from argon2 import PasswordHasher
from argon2 import exceptions
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")

DB_FILE = "users.db"

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500"])

ph = PasswordHasher(time_cost=4, memory_cost=102400, parallelism=8, hash_len=32)

def generate_backup_code():
    # Generates a 10-digit numeric string
    return ''.join([str(secrets.randbelow(10)) for _ in range(10)])


def create_user(first_name, last_name, email, username, password_hash):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()
    backup_code = generate_backup_code()  # <-- generate the backup code

    cursor.execute('''
        INSERT INTO users (first_name, last_name, email, username, password, date_created, backup_code)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (first_name, last_name, email, username, password_hash, now, backup_code))

    conn.commit()
    conn.close()

@app.route("/create-account", methods=["POST"])
def create_account():
    data = request.get_json()
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    email = data.get("email", "")
    username = data.get("username", "")
    password = data.get("password", "")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if username or email already exist
    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return jsonify({"status": "error", "message": "Username or email already exists"}), 400

    try:
        password_hash = ph.hash(password)
        now = datetime.utcnow().isoformat()
        backup_code = generate_backup_code()  # <-- generate the backup code
        cursor.execute('''
            INSERT INTO users (first_name, last_name, email, username, password, date_created, backup_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, email, username, password_hash, now, backup_code))

        conn.commit()
        conn.close()
        return jsonify({"status": "success", "backup_code": backup_code})
    except Exception as e:
        conn.close()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/check-username-email", methods=["POST"])
def check_username_email():
    data = request.get_json()
    username = data.get("username", "")
    email = data.get("email", "")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)", (username, email))
    existing = cursor.fetchone()
    conn.close()

    if existing:
        return jsonify({"exists": True})
    else:
        return jsonify({"exists": False})


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username_or_email = data.get("username_or_email", "")
    password = data.get("password", "")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Find user by username or email (case-insensitive)
    cursor.execute(
        "SELECT id, password FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)",
        (username_or_email, username_or_email)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "User does not exist"}), 404

    user_id, stored_hash = row

    try:
        ph.verify(stored_hash, password)
        # Password correct → update last_accessed
        now = datetime.utcnow().isoformat()
        cursor.execute("UPDATE users SET last_accessed = ? WHERE id = ?", (now, user_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Logged in successfully"})

    except exceptions.VerifyMismatchError:
        conn.close()
        return jsonify({"status": "error", "message": "Email exists but password is incorrect"}), 401


def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

def get_backup_code(email):
    """Fetch backup code for a given email from the DB"""
    conn = sqlite3.connect("users.db")  # change to your DB
    cursor = conn.cursor()

    cursor.execute("SELECT backup_code FROM users WHERE LOWER(email) = LOWER(?)", (email,))
    row = cursor.fetchone()

    conn.close()
    return row[0] if row else None

@app.route("/send-backup-code", methods=["POST"])
def send_backup_code():
    data = request.get_json()
    email = data.get("email")

    if not email:
        return jsonify({"success": False, "message": "No email provided"}), 400

    # Get backup code from DB
    backup_code = get_backup_code(email)

    if not backup_code:
        return jsonify({"success": False, "message": "Email not found"}), 404

    try:
        send_email(email, "Your Backup Code", f"Here is your backup code: {backup_code}")
        return jsonify({"success": True, "message": "Backup code sent successfully"})
    except Exception as e:
        print("Error sending email:", e)
        return jsonify({"success": False, "message": "Failed to send email"}), 500

def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row  # <-- enables dict-style access
    return conn


@app.route("/verify-backup-code", methods=["POST"])
def verify_backup_code():
    data = request.json
    email = data.get("email")
    backup_code = data.get("backup_code")

    conn = get_db_connection()
    user = conn.execute(
        "SELECT backup_code FROM users WHERE LOWER(email) = LOWER(?)", (email,)
    ).fetchone()
    conn.close()

    if user and user["backup_code"] == backup_code:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@app.route("/update-password", methods=["POST"])
def update_password():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("new_password")

    if not email or not new_password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    # Hash the new password
    hashed_pw = ph.hash(new_password)
    now = datetime.utcnow().isoformat()

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET password = ?, latest_reset = ?, password_resets = password_resets + 1
        WHERE LOWER(email) = LOWER(?)
        """,
        (hashed_pw, now, email)
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
