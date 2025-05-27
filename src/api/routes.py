from fastapi import APIRouter
from .endpoints import translation, search, weather, classification, calculator

api_router = APIRouter()
api_router.include_router(translation.router, prefix="/translate", tags=["translation"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(weather.router, prefix='/weather', tags=['weather'])
api_router.include_router(classification.router, prefix='/classify', tags=['weather'])
api_router.include_router(calculator.router, prefix='/calculate', tags=['calculate'])