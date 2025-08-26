from flask import Flask, request, jsonify
from flask_cors import CORS
from argon2 import PasswordHasher

app = Flask(__name__)

# Allow your frontend specifically
CORS(app, origins=["http://127.0.0.1:5500"])

# Create Argon2 hasher
ph = PasswordHasher(
    time_cost=4,
    memory_cost=102400,  # use 100 MB (not 1 GB so your PC doesn't freeze)
    parallelism=8,
    hash_len=32
)

@app.route("/hash-password", methods=["POST"])
def hash_password():
    data = request.get_json()
    password = data.get("password", "")

    print("DEBUG received data:", data)
    print("DEBUG extracted password:", password, type(password))
    
    hash_value = ph.hash(password)
    return jsonify({"hashed_password": hash_value})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
