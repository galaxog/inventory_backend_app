from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status


from app.api.users.schemas import UserCreate, UserOut
from app import models
from app.utils.security import hash_password


router = APIRouter()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, request: Request):
    cfg = request.app.state.cfg

    email = payload.email.lower()
    if len(payload.password) < cfg.MIN_PASSWORD_LEN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password too short")

    existing = models.User.query.filter(
        models.User.email == email
    ).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    user = models.User(
        email=email,
        hashed_password=hash_password(payload.password, rounds=cfg.BCRYPT_LOG_ROUNDS),
        is_active=True,
    )
    models.db.session.add(user)
    models.db.session.commit()
    models.db.session.refresh(user)
    return user
