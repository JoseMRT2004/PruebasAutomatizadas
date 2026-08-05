"""FastAPI application factory and entry point."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from src.config import settings
from src.db import close_connection, init_db
from src.presentation.routes import router
from src.services.auth_service import auth_service

STATIC_DIR = Path(__file__).resolve().parent / "presentation" / "static"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    auth_service.seed_default_users()
    yield
    close_connection()


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        max_age=settings.session_ttl_minutes * 60,
        same_site="lax",
    )

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
    app.include_router(router)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
