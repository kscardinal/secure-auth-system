from passlib.context import CryptContext
import json
import os
from dotenv import load_dotenv
from icecream import ic

# Load environment variables
load_dotenv()

FILENAME = os.getenv("USERS")

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

# Load users from JSON safely
def load_users(filename: str) -> dict:
    if not os.path.exists(filename):
        print(f"[INFO] File '{filename}' not found. Creating and adding default Admin user.")
        default_user = {
            "Admin": hash_password("Password123!")
        }
        save_users(filename, default_user)
        return default_user

    try:
        with open(filename, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"[WARN] File '{filename}' is invalid JSON. Recreating with default Admin user.")
        default_user = {
            "Admin": hash_password("Password123!")
        }
        save_users(filename, default_user)
        return default_user
    except Exception as e:
        print(f"[ERROR] Error reading file '{filename}': {e}")
        return {}

# Save users to JSON
def save_users(filename: str, users: dict):
    try:
        with open(filename, "w") as f:
            json.dump(users, f, indent=4)
        print(f"[INFO] Users saved to '{filename}'")
    except Exception as e:
        print(f"[ERROR] Failed to save users: {e}")

# Add a new user (if username is unique)
def add_user(filename: str, username: str, password: str) -> bool:
    users = load_users(filename)
    if username in users:
        print(f"[ERROR] Username '{username}' already exists.")
        return False
    users[username] = hash_password(password)
    save_users(filename, users)
    print(f"[SUCCESS] User '{username}' added.")
    return True

# -------------------------------
# MAIN PROGRAM
# -------------------------------
if not FILENAME:
    print("[ERROR] USERS env variable not set.")
    exit(1)

username = input('What is your username? : ')
password = input('What is your password? : ')
ic(f'Username: {username} || Password: {password}')

add_user(FILENAME, username, password)

print("\n=== Login ===")
users = load_users(FILENAME)

while True:
    input_username = input("Username: ")

    if input_username in users:
        input_password = input("Password: ")
        stored_hash = users[input_username]

        if verify_password(input_password, stored_hash):
            print(f"[SUCCESS] Welcome, {input_username}!")
            break
        else:
            print("[ERROR] Incorrect password.")
    else:
        print("[ERROR] Username not found.")
