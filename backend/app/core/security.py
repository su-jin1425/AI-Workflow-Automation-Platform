from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Returns:
        UTF-8 encoded bcrypt hash string.
    """
    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12),
    )

    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.
    """
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )
    except ValueError:
        return False


def create_access_token(subject: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    payload: dict[str, Any] = {
        "sub": subject,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )