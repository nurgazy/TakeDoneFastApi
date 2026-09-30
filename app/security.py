import asyncio
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.config import settings


def _hash_password_sync(password: str) -> str:
    # bcrypt принимает байты и пароль не длиннее 72 байт
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def _verify_password_sync(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode("utf-8")[:72]
    hash_bytes = hashed_password.encode("utf-8")
    try:
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except (ValueError, TypeError):
        return False


async def hash_password(password: str) -> str:
    return await asyncio.to_thread(_hash_password_sync, password)


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    return await asyncio.to_thread(_verify_password_sync, plain_password, hashed_password)


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


async def create_access_token(user_id: int) -> str:
    return await asyncio.to_thread(
        _create_token,
        str(user_id),
        "access",
        timedelta(minutes=settings.access_token_expire_minutes),
    )


async def create_refresh_token(user_id: int) -> str:
    return await asyncio.to_thread(
        _create_token,
        str(user_id),
        "refresh",
        timedelta(days=settings.refresh_token_expire_days),
    )


def _decode_token(token: str, expected_type: str) -> int | None:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
    if payload.get("type") != expected_type:
        return None
    subject = payload.get("sub")
    if subject is None:
        return None
    try:
        return int(subject)
    except (TypeError, ValueError):
        return None


async def decode_token(token: str, expected_type: str) -> int | None:
    return await asyncio.to_thread(_decode_token, token, expected_type)