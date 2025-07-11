import string
import random
import secrets
from passlib.context import CryptContext

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

PASSWORD_LENGTH :  int = 1
INCLUDE_NUMBERS : bool = False
INCLUDE_SPECIAL_CHARACTERS : bool = False

while True:
    length = input("How long do you want your password? (1 - 128 characters) : ")

    try:
        number = int(length)

        if number > 128:
            print("ERROR - Too big")
        elif number < 1:
            print("ERROR - Too small")
        else:
            PASSWORD_LENGTH = number
            break

    except ValueError:
        print("ERROR - That was not a valid integer")

while True:
    digits = input("Do you want to include numbers? (y or n) : ")

    if digits.lower() in ['y', 'yes']:
        INCLUDE_NUMBERS = True
        break
    elif digits.lower() in ['n', 'no']:
        INCLUDE_NUMBERS = False
        break
    else:
        print('[ERROR - Do not understand - Please follow instructions]')


while True:
    digits = input("Do you want to include special characters? (y or n) : ")

    if digits.lower() in ['y', 'yes']:
        INCLUDE_SPECIAL_CHARACTERS = True
        break
    elif digits.lower() in ['n', 'no']:
        INCLUDE_SPECIAL_CHARACTERS = False
        break
    else:
        print('[ERROR - Do not understand - Please follow instructions]')


CHARACTER_SET = list(string.ascii_letters)

if INCLUDE_NUMBERS:
    CHARACTER_SET += list(string.digits)  # 0-9

if INCLUDE_SPECIAL_CHARACTERS:
    CHARACTER_SET += list(string.punctuation)  # !@#$%^&*()_+ etc.

def generate_password():
    return ''.join(secrets.choice(CHARACTER_SET) for _ in range(PASSWORD_LENGTH))

while True:
    password = generate_password()

    if not any(c in string.ascii_letters for c in password):
        print("ERROR - No letters - Generating again")
    elif not any(c in string.digits for c in password):
        print("ERROR - No digits - Generating again")
    elif not any(c in string.punctuation for c in password):
        print("ERROR - No special characters - Generating again")
    else:
        print(f"Password Generated : {password}")
        break