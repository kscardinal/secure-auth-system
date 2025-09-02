import os
import hashlib

# 1️⃣ Your password as a string
password = "MySuperSecretPassword123!"

# 2️⃣ Convert password to bytes (UTF-8)
password_bytes = password.encode('utf-8')

# 3️⃣ Generate a random 256-bit (32-byte) salt
salt = os.urandom(32)  # 32 bytes = 256 bits

# 4️⃣ Combine password + salt
salted_password = password_bytes + salt

# 5️⃣ Hash using SHA-256
hash_value = hashlib.sha256(salted_password).hexdigest()

# 6️⃣ Optional: store salt as hex for database
salt_hex = salt.hex()

# ✅ Print results
print("Password bytes:", password_bytes)
print("Salt bytes:", salt)
print("Salt (hex):", salt_hex)
print("Hash:", hash_value)

