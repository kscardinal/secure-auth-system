import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask import Flask, session
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

# Get email and password from .env file
sender_email = os.getenv("SENDER_EMAIL")
sender_password = os.getenv("SENDER_PASSWORD")

# Define the DB file
DB_FILE = "users.db"

# Start up the Flask app and allow cookies
app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500"], supports_credentials=True)
app.secret_key = "supersecretkey" 

# Setting up the hashing
ph = PasswordHasher(time_cost=4, memory_cost=102400, parallelism=8, hash_len=32)



# Function to generate the backup_code (6 random digits)
def generate_backup_code():
    # Generates a 10-digit numeric string
    return ''.join([str(secrets.randbelow(6)) for _ in range(6)])



# Function to create the user
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



# Create the account
@app.route("/create-account", methods=["POST"])
def create_account():
    data = request.get_json()
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")
    email = data.get("email", "")
    username = data.get("username", "")
    password = data.get("password", "")

    # Connect to DB and get data
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Check if username or email already exist
    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return jsonify({"status": "error", "message": "Username or email already exists"}), 400

    # If they don't exist, create the user and add data to the DB
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



# Check username or email to see if they exist
@app.route("/check-username-email", methods=["POST"])
def check_username_email():
    data = request.get_json()
    username = data.get("username", "")
    email = data.get("email", "")

    # Connect to DB and get data
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)", (username, email))
    existing = cursor.fetchone()
    conn.close()

    # Verify if the email or username exist in the records
    if existing:
        return jsonify({"exists": True})
    else:
        return jsonify({"exists": False})



# Login to account
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username_or_email = data.get("username_or_email", "")
    password = data.get("password", "")

    # Connect to DB and get data
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Find user by username or email (case-insensitive)
    cursor.execute(
        "SELECT id, password FROM users WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)",
        (username_or_email, username_or_email)
    )
    row = cursor.fetchone()

    # If email doesn't exist, user doesn't exist
    if not row:
        conn.close()
        return jsonify({"status": "error", "message": "User does not exist"}), 404

    # User exists, get the user_id and hashed password for verification
    user_id, stored_hash = row

    try:
        # Hash inputted password and compared to previously hashed password
        ph.verify(stored_hash, password)

        # Add user ID to session (Cookies) so we can use get the data later
        session["user_id"] = user_id

        # Password correct → update last_accessed
        now = datetime.utcnow().isoformat()
        cursor.execute("UPDATE users SET last_accessed = ? WHERE id = ?", (now, user_id))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Logged in successfully"})

    # Message if the email exists bu the password was inputted wrong
    except exceptions.VerifyMismatchError:
        conn.close()
        return jsonify({"status": "error", "message": "Email exists but password is incorrect"}), 401



# Function to send email with given email, subject, and body
def send_email(to_email, subject, body):
    # Defining the variables for sending the message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Sending the data using gmail and variables in the .env file
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)



# Function to get backup code from email in th DB
def get_backup_code(email):
    # Connect to DB and get the data
    conn = sqlite3.connect("users.db") 
    cursor = conn.cursor()

    cursor.execute("SELECT backup_code FROM users WHERE LOWER(email) = LOWER(?)", (email,))
    row = cursor.fetchone()

    conn.close()
    return row[0] if row else None



# Send the backup code to email
@app.route("/send-backup-code", methods=["POST"])
def send_backup_code():
    data = request.get_json()
    email = data.get("email")

    # Verify an email was inputted
    if not email:
        return jsonify({"success": False, "message": "No email provided"}), 400

    # Get backup code from DB
    backup_code = get_backup_code(email)

    # Verify there was a backup code for the given email
    if not backup_code:
        return jsonify({"success": False, "message": "Email not found"}), 404

    # Send email with backup code
    try:
        send_email(email, "Your Backup Code", f"Here is your backup code: {backup_code}")
        return jsonify({"success": True, "message": "Backup code sent successfully"})
    except Exception as e:
        print("Error sending email:", e)
        return jsonify({"success": False, "message": "Failed to send email"}), 500



# Verify backup code that was sent to email
@app.route("/verify-backup-code", methods=["POST"])
def verify_backup_code():
    data = request.json
    email = data.get("email")
    backup_code = data.get("backup_code")

    # Connect to DB and get the data
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT backup_code FROM users WHERE LOWER(email) = LOWER(?)", (email,))
    user = cursor.fetchone()
    conn.close()

    # Verify the backup code
    if user and user[0] == backup_code:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})



# Update password
@app.route("/update-password", methods=["POST"])
def update_password():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("new_password")

    # Check if form has inputed data
    if not email or not new_password:
        return jsonify({"success": False, "message": "Email and password required"}), 400

    # Hash the new password
    hashed_pw = ph.hash(new_password)
    now = datetime.utcnow().isoformat()
    new_backup_code = generate_backup_code()

    # Connect to the DB and update the paaswork and lastest_rest
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET password = ?, latest_reset = ?, password_resets = password_resets + 1, backup_code = ?
        WHERE LOWER(email) = LOWER(?)
        """,
        (hashed_pw, now, new_backup_code, email)
    )

    conn.commit()
    conn.close()

    return jsonify({"success": True})



# Update number of attempts to login with password
@app.route("/update-login-attempts", methods=["POST"])
def update_login_attempts():
    data = request.get_json()
    email = data.get("email")
    attempts = data.get("login_attempts", 0)

    # Connect to DB and update login attempts
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET login_attempts = ? WHERE LOWER(email) = LOWER(?)",
        (attempts, email)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": f"Login attempts updated to {attempts}"})



# Update number of attempts to verify backup code
@app.route("/update-verification-attempts", methods=["POST"])
def update_verification_attempts():
    data = request.get_json()
    email = data.get("email")
    attempts = data.get("verification_attempts", 0)

    # Connect to DB and update verification attempts
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET verification_attempts = ? WHERE LOWER(email) = LOWER(?)",
        (attempts, email)
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": f"verification_attempts updated to {attempts}"})



# Get user details
@app.route("/user-details", methods=["GET"])
def user_details():
    if "user_id" not in session:
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    user_id = session["user_id"]

    # Connect to DB and get the data
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, date_created, last_accessed, login_attempts, latest_reset, password_resets, verification_attempts FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    # Check if data is returned and report error if not
    if row:
        username, email, date_created, last_accessed, login_attempts, latest_reset,  password_resets, verification_attempts = row
        return jsonify({
            "status": "success",
            "username": username,
            "email": email,
            "date_created": date_created,
            "last_accessed": last_accessed,
            "login_attempts": login_attempts,
            "latest_reset": latest_reset,
            "password_resets": password_resets,
            "verification_attempts": verification_attempts
        })
    else:
        return jsonify({"status": "error", "message": "User not found"}), 404


# Main Program
if __name__ == "__main__":
    app.run(port=5000, debug=True)
