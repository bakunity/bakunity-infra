from fastapi import FastAPI

from infrastructure.config import get_settings


def create_app() -> FastAPI:
    """Build the HTTP interface without embedding business rules in the client layer."""
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version="0.1.0")

    @app.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        return {"status": "ok", "service": "bakunity-infra"}

    return app


app = create_app()
