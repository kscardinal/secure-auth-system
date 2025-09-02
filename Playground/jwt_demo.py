from jose import jwt, JWTError
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Get the JWT secret key and algorithm
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM")

def create_token(subject: str, role: str, expires_in_minutes=60):
    payload = {
        "sub": subject,
        "role": role,
        "exp": datetime.utcnow() + timedelta(minutes=expires_in_minutes)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def generate_pdf_endpoint(token: str):
    payload = verify_token(token)
    if not payload:
        return "Access Denied: Invalid Token"
    if payload.get("role") not in ["client", "admin"]:
        return "Access Denied: Insufficient permissions"
    return "PDF Generated Successfully!"

def admin_only_endpoint(token: str):
    payload = verify_token(token)
    if not payload:
        return "Access Denied: Invalid Token"
    if payload.get("role") != "admin":
        return "Access Denied: Admins only"
    return "Admin Panel Accessed"

# Simulate usage
if __name__ == "__main__":
    # Create tokens
    client_token = create_token("mobile_app", "client")
    admin_token = create_token("admin_user", "admin")

    print("Client token:", client_token)
    print("Admin token:", admin_token)

    # Simulate client trying to generate a PDF
    print("\nClient trying to generate PDF:")
    print(generate_pdf_endpoint(client_token))  # Allowed

    print("\nClient trying to access admin panel:")
    print(admin_only_endpoint(client_token))  # Denied

    # Simulate admin accessing admin panel
    print("\nAdmin accessing admin panel:")
    print(admin_only_endpoint(admin_token))  # Allowed
