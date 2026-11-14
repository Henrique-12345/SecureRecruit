from pathlib import Path

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.config import settings
from app.core.exceptions import (
    AppError,
    app_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)


def _ensure_data_dir(path_str: str) -> Path:
    """Create upload/stego dirs; fall back to repo-root if CWD is backend/."""
    path = Path(path_str)
    candidates = [path] if path.is_absolute() else [Path.cwd() / path, Path.cwd().parent / path]
    last_error: OSError | None = None
    for candidate in candidates:
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            return candidate.resolve()
        except OSError as exc:
            last_error = exc
    raise RuntimeError(f"Cannot create data directory for {path_str}: {last_error}")


def _warn_insecure_defaults() -> None:
    if settings.APP_ENV.lower() not in {"production", "prod"}:
        return
    weak = []
    if settings.JWT_SECRET_KEY.startswith("change-me"):
        weak.append("JWT_SECRET_KEY")
    if settings.CRYPTO_MASTER_SECRET.startswith("change-me"):
        weak.append("CRYPTO_MASTER_SECRET")
    if weak:
        import logging

        logging.getLogger("securerecruit").warning(
            "Insecure default secrets in production: %s — rotate before academic demo goes public.",
            ", ".join(weak),
        )


def create_app() -> FastAPI:
    _ensure_data_dir(settings.UPLOAD_DIRECTORY)
    _ensure_data_dir(settings.STEGO_DIRECTORY)
    _warn_insecure_defaults()

    app = FastAPI(
        title=settings.APP_NAME,
        description="Plataforma de recrutamento e seleção para estudo acadêmico de cibersegurança.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        # Allows Vercel production/preview URLs even if CORS_ORIGINS is incomplete.
        allow_origin_regex=r"https://.*\.vercel\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)

    app.include_router(api_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "app": settings.APP_NAME}

    return app


app = create_app()
