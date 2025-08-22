import re
from argon2 import PasswordHasher
from colorama import init, Fore

init(autoreset=True)

# Argon2 password hasher
ph = PasswordHasher(
    time_cost=4,
    memory_cost=1048576,
    parallelism=8,
    hash_len=32
)

# Strength levels for bar
STRENGTH_LEVELS = [
    ("Super Weak", Fore.RED),
    ("Weak", Fore.LIGHTRED_EX),
    ("Moderate", Fore.YELLOW),
    ("Strong", Fore.LIGHTGREEN_EX),
    ("Super Strong", Fore.GREEN)
]

# Forbidden characters pattern
FORBIDDEN_PATTERN = r"[ \t\n\r\"']"
SPECIAL_PATTERN = r"[!@#$%^&*()_\-+=\[\]{}|;:'\",.<>?/]"
UPPER_PATTERN = r"[A-Z]"
LOWER_PATTERN = r"[a-z]"
NUMBER_PATTERN = r"[0-9]"

def validate_password(password):
    """
    Validates password and returns (is_valid, list_of_errors)
    """
    errors = []

    if len(password) < 12:
        errors.append("Password is too short. Minimum 12 characters.")

    if re.search(FORBIDDEN_PATTERN, password):
        errors.append("Password contains forbidden characters (spaces, quotes, etc).")

    if not re.search(UPPER_PATTERN, password):
        errors.append("Password must contain at least one uppercase letter.")

    if not re.search(LOWER_PATTERN, password):
        errors.append("Password must contain at least one lowercase letter.")

    if not re.search(NUMBER_PATTERN, password):
        errors.append("Password must contain at least one number.")

    if not re.search(SPECIAL_PATTERN, password):
        errors.append("Password must contain at least one special character.")

    return (len(errors) == 0, errors)

def password_strength_bar(password):
    """
    Prints a 20-character strength bar with color and label
    """
    length = len(password)
    # Determine discrete level (0-4)
    level_index = min(length // 4, 4)
    label, color = STRENGTH_LEVELS[level_index]

    # Bar: 5 levels, each level = 4 characters
    bar = '-' * ((level_index + 1) * 4) + ' ' * (20 - (level_index + 1) * 4)
    print(color + bar)
    print(label)

def main():
    while True:
        password = input("Enter a password: ")

        is_valid, errors = validate_password(password)
        password_strength_bar(password)

        if is_valid:
            # Hash the password with Argon2
            hashed_password = ph.hash(password)
            print("\nPassword is valid and securely hashed!")
            print(f"Hashed password:\n{hashed_password}")
            break
        else:
            print("\n".join(errors))
            print("Please try again.\n")

if __name__ == "__main__":
    main()
