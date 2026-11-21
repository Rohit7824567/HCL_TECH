"""Small, dependency-free session token and password helpers."""
import base64
import hashlib
import hmac
import json
import os
import time

PASSWORD_ITERATIONS = 310_000
TOKEN_TTL_SECONDS = 60 * 60 * 12

def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PASSWORD_ITERATIONS)
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${_b64(salt)}${_b64(derived)}"

def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, iterations, salt, expected = stored.split("$")
        if scheme != "pbkdf2_sha256": return False
        actual = _b64(hashlib.pbkdf2_hmac("sha256", password.encode(), base64.urlsafe_b64decode(salt + "=="), int(iterations)))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False

def create_token(user_id: int, email: str) -> str:
    payload = _b64(json.dumps({"sub": user_id, "email": email, "exp": int(time.time()) + TOKEN_TTL_SECONDS}, separators=(",", ":")).encode())
    secret = os.getenv("AUTH_SECRET", "local-development-only-change-this-secret").encode()
    signature = _b64(hmac.new(secret, payload.encode(), hashlib.sha256).digest())
    return f"{payload}.{signature}"

def read_token(token: str):
    try:
        payload, signature = token.split(".", 1)
        secret = os.getenv("AUTH_SECRET", "local-development-only-change-this-secret").encode()
        expected = _b64(hmac.new(secret, payload.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(expected, signature): return None
        body = json.loads(base64.urlsafe_b64decode(payload + "=="))
        return body if int(body["exp"]) > int(time.time()) else None
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return None
