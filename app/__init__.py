from __future__ import annotations

import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import JSONResponse
# from fastapi_jwt_auth import AuthJWT
# from fastapi_jwt_auth.exceptions import AuthJWTException
# from pydantic_settings import BaseSettings

from app.api.product.exceptions import (
    ProductAlreadyExistsException,
    ProductNotFoundException,
    InvalidInventoryUpdateException
)
from app.state import setup_state
from app.api.authentication.exceptions import APIAuthError


def create_app(env_name: Optional[str] = None) -> FastAPI:
    """Factory: initialize state + return a FastAPI app."""

    state = setup_state(env_name)
    cfg = state.settings

    app = FastAPI(title="Sample Inventory Service", description="FastAPI + Postgres + SQLAlchemy + Alembic service")
    app.state.cfg = cfg

    # Attach DB factory + engine (Flask-SQLAlchemy-like surface)
    from app.models import db
    app.state.db = db.session
    app.state.db_engine = db.engine
    # JWT config is loaded from app.state.cfg (patterned after your existing app)
    # @AuthJWT.load_config
    # def _jwt_config() -> BaseSettings:
    #     class JWTSettings(BaseSettings):
    #         authjwt_secret_key: str = cfg.JWT_SECRET_KEY
    #         authjwt_algorithm: str = cfg.JWT_ALGORITHM
    #         authjwt_access_token_expires = cfg.JWT_ACCESS_TOKEN_EXPIRES
    #         authjwt_refresh_token_expires = cfg.JWT_REFRESH_TOKEN_EXPIRES
    #     return JWTSettings()

    # Routers
    from app.api import api_router
    app.include_router(api_router)

    # Exception handlers
    # @app.exception_handler(AuthJWTException)
    # def _authjwt_exception_handler(request, exc: AuthJWTException):
    #     return JSONResponse(status_code=exc.status_code, content={"message": exc.message})
    #
    # @app.exception_handler(APIAuthError)
    # def _api_auth_error_handler(request, exc: APIAuthError):
    #     return JSONResponse(status_code=exc.status_code, content={"message": exc.description})

    @app.exception_handler(ProductAlreadyExistsException)
    async def product_already_exists_exception_handler(request, exc: ProductAlreadyExistsException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.description},
        )

    @app.exception_handler(ProductNotFoundException)
    async def product_not_found_exception_handler(request, exc: ProductNotFoundException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.description},
        )

    @app.exception_handler(InvalidInventoryUpdateException)
    async def invalid_inventory_update_exception_handler(request, exc: InvalidInventoryUpdateException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.description},
        )

    # Basic startup/shutdown hooks
    logger = logging.getLogger("api")

    @app.on_event("startup")
    async def _startup():
        logger.info("API starting...")

    @app.on_event("shutdown")
    async def _shutdown():
        try:
            from app.models import dispose_engine
            dispose_engine()
        except Exception:
            pass

    return app
