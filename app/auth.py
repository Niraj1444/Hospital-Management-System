import hashlib
import secrets

from app.database import execute, fetch_all


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000).hex()


def ensure_default_admin():
    existing = fetch_all("SELECT user_id FROM users WHERE username=?", ("admin",))
    if existing:
        return
    salt = secrets.token_hex(16)
    password_hash = hash_password("admin123", salt)
    execute(
        "INSERT INTO users(username, password_hash, salt) VALUES(?,?,?)",
        ("admin", password_hash, salt),
    )


def authenticate(username, password):
    rows = fetch_all("SELECT password_hash, salt FROM users WHERE username=?", (username,))
    if not rows:
        return False
    saved_hash, salt = rows[0]
    return saved_hash == hash_password(password, salt)
