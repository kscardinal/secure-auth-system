import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from argon2 import PasswordHasher

DB_FILE = "users.db"

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500"])

ph = PasswordHasher(time_cost=4, memory_cost=102400, parallelism=8, hash_len=32)

def create_user(first_name, last_name, email, username, password_hash):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    now = datetime.utcnow().isoformat()

    cursor.execute('''
        INSERT INTO users (first_name, last_name, email, username, password, date_created)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (first_name, last_name, email, username, password_hash, now))

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

    try:
        password_hash = ph.hash(password)
        create_user(first_name, last_name, email, username, password_hash)
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":
    app.run(port=5000, debug=True)
