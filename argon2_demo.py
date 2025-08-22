import time
from argon2 import PasswordHasher

# Example password
password = "MySuperSecretPassword123!"

# Create a PasswordHasher with custom parameters
ph = PasswordHasher(
    time_cost=4,        # number of iterations
    memory_cost=1048576, # memory in KB
    parallelism=8,
    hash_len=32
)

# Start the timer
start_time = time.time()

# Hash the password
hash_value = ph.hash(password)

# Stop the timer
end_time = time.time()

# Print results
print("Hashed password:", hash_value)
print(f"Time taken: {end_time - start_time:.4f} seconds")
