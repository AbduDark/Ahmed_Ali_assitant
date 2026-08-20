"""JWT token generation/verification and password hashing."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.config import settings

# ── Password Hashing ────────────────────────────────────────

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a plaintext password using Argon2."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Tokens ───────────────────────────────────────────────

def create_access_token(user_id: str, role: str) -> str:
    """Create a short-lived JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_expire_minutes)
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: str) -> str:
    """Create a long-lived JWT refresh token."""
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_expire_days)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token. Raises JWTError on failure."""
    return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
