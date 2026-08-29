from fastapi import FastAPI

from apps.api.middleware import RequestContextMiddleware
from infrastructure.config import get_settings
from infrastructure.observability import configure_logging


def create_app() -> FastAPI:
    """Build the HTTP interface without embedding business rules in the client layer."""
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.add_middleware(RequestContextMiddleware, header_name=settings.request_id_header)

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "bakunity-infra"}

    return app


app = create_app()
