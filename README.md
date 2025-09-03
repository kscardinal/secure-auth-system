# 📌 secure-auth-system 
`secure-auth-system` is a secure authentication system with account management features built with Flask and SQLite.


![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-green)
![GitHub commit activity](https://img.shields.io/github/commit-activity/t/kscardinal/secure-auth-system)
![GitHub last commit](https://img.shields.io/github/last-commit/kscardinal/secure-auth-system)

---

## Table of Contents  
- [Overview](#Overview)
- [Features](#features)
- [Tech Stack](#Tech-Stack)
- [Project Structure](#project-structure)
- [Setup](#setup)
- [Usage](#usage)
- [Security Features](#security-features)
- [API Endpoints](#API-Endpoints)
- [License](#License)

---

## Overview  

`secure-auth-system` is a secure authentication system built with Flask, designed to manage user accounts and provide robust password handling and recovery features. It uses Argon2 for password hashing, stores user data in a SQLite database, and supports account creation, login, password resets, and backup code verification. The system integrates email functionality for sending backup codes and password reset notifications, and tracks user activity such as login attempts and password resets. Environment variables are used for sensitive email credentials, and CORS is configured to allow secure cross-origin requests from a specified frontend. Overall, the project aims to provide a secure, user-friendly authentication backend for web applications.  

---

## Features  

- Secure user authentication with Argon2 password hashing
- Account creation with email verification
- Password reset functionality with backup codes
- Brute force protection with login attempt tracking
- Password strength requirements:
	- Minimum 12 characters
	- Must contain uppercase and lowercase letters
	- Must contain numbers and special characters
	- Dictionary word checks
	- Sequential character checks
- User activity tracking (login attempts, password resets, etc.)
- Responsive web interface.

---

## Tech Stack  

- **Frontend**: HTML, CSS, JavaScript 
- **Backend**: Python, Flask
- **Database**: SQLite
- **Other Tools**: Argon2  

---

## Project Structure  

- secure-auth-system/
- ├── [`server.py`](server.py)                           # Main Flask application with API endpoints
- ├── [`databse.py`](database.py)                         # Database initialization and schema
- ├── [`Login.html`](Login.html)                         # Login page
- ├── [`CreateAccount.html`](CreateAccount.html)          # Account creation page
- ├── [`ForgotPassword.html`](ForgotPassword.html)        # Password reset page
- ├── [`Details.html`](Details.html)                     # User account details page
- └── `style_*.css`                       # CSS stylesheet


---

## Setup

1. **Install uv**
	Download and install [uv](https://github.com/astral-sh/uv) from the official repository or use:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv self update
uv python install 3.13
```

2. **Create a virtual environment**
```bash
uv venv
```

3. **Install dependencies**
```bash
uv pip install -e .
```

4. **Add a `.env` file**
	- Create a file named `.env` in the project root directory.
	- Add the following line (no quotes):
```bash
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-specific-password
```
5. Initialize the database:
```bash
python database.py
```

---

## Usage

1. Start the server:
```python
python server.py
```
2. Open [`Login`](http://127.0.0.1:5500/Login.html) page on the web


---

## Security Features

- Secure password hashing with Argon2
- Session-based authentication
- CORS protection
- Backup code system for account recovery
- Account lockout after failed attempts
- Password strength validation
- Email verification

---

## API Endpoints

| Endpoint              | Method | Description                  |
| --------------------- | ------ | ---------------------------- |
| `/create-account`     | POST   | Create new user account      |
| `/login`              | POST   | User authentication          |
| `/send-backup-code`   | POST   | Send recovery code via email |
| `/verify-backup-code` | POST   | Verify recovery code         |
| `/update-password`    | POST   | Change user password         |
| `/user-details`       | GET    | Get user account information |

---

## License

This project is licensed under the MIT License, which means you are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, as long as you include the original copyright and license notice in any copy of the software. The software is provided "as is," without warranty of any kind.

