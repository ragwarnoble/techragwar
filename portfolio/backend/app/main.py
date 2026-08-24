from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base
from .database import engine
from .routes import router


Base.metadata.create_all(
    bind=engine
)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


origins = [
    origin.strip()
    for origin in settings.cors_origins.split(",")
]


app.add_middleware(
    CORSMiddleware,

    allow_origins=origins,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


app.include_router(router)


@app.get("/")
def root():

    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/health",
    }
