from fastapi import APIRouter
from .endpoints import translation, search

api_router = APIRouter()
api_router.include_router(translation.router, prefix="/translate", tags=["translation"])
api_router.include_router(search.router, prefix="/search", tags=["search"])