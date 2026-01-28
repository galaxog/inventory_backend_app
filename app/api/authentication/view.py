from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.orm import Session

from app import models
from app.api.authentication.schemas import LoginRequest, TokenPair
from app.api.dependencies import get_db
from app.utils.security import verify_password

router = APIRouter()


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, request: Request, Authorize: AuthJWT = Depends()):
    user = models.User.query.filter(models.User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad credentials"
        )

    subject = str(user.id)
    access_token = Authorize.create_access_token(subject=subject)
    refresh_token = Authorize.create_refresh_token(subject=subject)

    # Persist refresh token by JTI for rotation/revocation (no raw-token storage)
    cfg = request.app.state.cfg
    refresh_jti = Authorize.get_jti(refresh_token)
    token = models.RefreshToken(
        user_id=user.id,
        jti=refresh_jti,
        revoked=False,
        expires_at=datetime.utcnow() + cfg.JWT_REFRESH_TOKEN_EXPIRES,
    )
    models.db.session.add(token)
    models.db.session.commit()

    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenPair)
def refresh(request: Request, Authorize: AuthJWT = Depends()):
    """Rotate refresh token and return a new access+refresh pair."""
    Authorize.jwt_refresh_token_required()

    # Read raw refresh token from Authorization header to extract JTI for lookup
    authz = request.headers.get("Authorization", "")
    if not authz.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token"
        )
    raw_refresh = authz.split(" ", 1)[1].strip()

    refresh_jti = Authorize.get_jti(raw_refresh)

    row = models.RefreshToken.query.filter(
        models.RefreshToken.jti == refresh_jti
    ).first()

    if not row or row.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token revoked or unknown",
        )
    if row.expires_at <= datetime.utcnow():
        row.revoked = True
        models.db.session.add(row)
        models.db.session.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired"
        )

    subject = Authorize.get_jwt_subject()
    if str(row.user_id) != str(subject):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token mismatch"
        )

    # Revoke old token (rotation)
    row.revoked = True
    models.db.session.add(row)
    models.db.session.commit()

    # Issue new pair
    access_token = Authorize.create_access_token(subject=subject)
    new_refresh = Authorize.create_refresh_token(subject=subject)
    new_jti = Authorize.get_jti(new_refresh)

    cfg = request.app.state.cfg
    token = models.RefreshToken(
        user_id=row.user_id,
        jti=new_jti,
        revoked=False,
        expires_at=datetime.utcnow() + cfg.JWT_REFRESH_TOKEN_EXPIRES,
    )
    models.db.session.add(token)
    models.db.session.commit()

    return TokenPair(access_token=access_token, refresh_token=new_refresh)
