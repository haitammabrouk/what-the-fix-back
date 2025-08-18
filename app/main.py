from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.routes import API_ROUTER
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version=settings.api_version,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(API_ROUTER, prefix=f"/api/{settings.api_version}")