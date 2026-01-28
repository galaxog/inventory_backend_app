from __future__ import annotations

import hashlib

from passlib.hash import bcrypt


def hash_password(password: str, rounds: int) -> str:
    return bcrypt.using(rounds=rounds).hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.verify(password, hashed_password)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
