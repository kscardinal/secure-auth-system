## LOTO Testing Project
A secure authentication system with account management features built with Flask and SQLite.

---

### Features
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
- Responsive web interface

---

### Tech Stack
- Backend: Python/Flask
- Database: SQLite
- Frontend: HTML/CSS/JavaScript
- Password Hashing: Argon2
- Email: SMTP (Gmail)

---

### Setup
1. Clone the repository
2. Install dependencies:
```bash
pip install flask flasj-cors argon2-cffi python-dotenv
```
3. Create a .env file with email credentials:
```
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-specific-password
```
4. Initialize the database:
```bash
python database.py
```
5. Start the server:
```bash
python server.py
```
6. Open [Login.html](http://127.0.0.1:5500/Login.html) in your browser to access the application

---

### Project Structure
- [`server.py`](server.py) - Main Flask application with API endpoints
- [`database.py`](database.py) - Database initialization and schema
- [`Login.html`](Login.html) - Login page
- [`CreateAccount.html`](CreateAccount.html) - Account creation page
- [`ForgotPassword.html`](ForgotPassword.html) - Password reset page
- [`Details.html`](Details.html) - User account details page
- `style_*.css` - CSS stylesheets

---

### Security Features
- Secure password hashing with Argon2
- Session-based authentication
- CORS protection
- Backup code system for account recovery
- Account lockout after failed attempts
- Password strength validation
- Email verification

---

### API Endpoints
| Endpoint              | Method | Description                  |
| --------------------- | ------ | ---------------------------- |
| `/create-account`     | POST   | Create new user account      |
| `/login`              | POST   | User authentication          |
| `/send-backup-code`   | POST   | Send recovery code via email |
| `/verify-backup-code` | POST   | Verify recovery code         |
| `/update-password`    | POST   | Change user password         |
| `/user-details`       | GET    | Get user account information |

---

### License
MIT

---

### Contributing
Feel free to submit issues and enhancement requests!

---

### Note
This is a testing/development project - additional security measures would be needed for production use.
