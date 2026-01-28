from fastapi import APIRouter
#from app.api.authentication.view import router as auth_router
#from app.api.users.view import router as users_router
from app.api.product.view import router as products_router


api_router = APIRouter(
    prefix="/api", tags=["api"], responses={404: {"description": "Not found"}}
)
#api_router.include_router(auth_router)
#api_router.include_router(users_router)
api_router.include_router(products_router)

