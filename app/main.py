"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.routes import documents, feedback, search, upload
from src.config import get_settings
from src.database import check_database_health
from src.aws import check_s3_health
from src.logging_config import new_request_id, setup_logging
from src.schemas import HealthResponse

BASE_DIR = Path(__file__).resolve().parent
settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Starting %s", settings.app_name)
    logger.info("Configuration: %s", settings.safe_repr())
    yield
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key.get_secret_value(),
    max_age=86400,
)

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.state.templates = templates

static_dir = BASE_DIR / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    rid = new_request_id()
    request.state.request_id = rid
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response


@app.get("/health", response_model=HealthResponse)
async def health():
    db_ok = check_database_health()
    s3_ok = check_s3_health()
    ai_status = "enabled" if settings.ai_available else "disabled"
    return HealthResponse(
        application="ok",
        database="ok" if db_ok else "error",
        s3="ok" if s3_ok else "error",
        ai=ai_status,
    )


@app.get("/health/database")
async def health_database():
    ok = check_database_health()
    return {"status": "ok" if ok else "error"}


@app.get("/health/s3")
async def health_s3():
    ok = check_s3_health()
    return {"status": "ok" if ok else "error"}


app.include_router(upload.router)
app.include_router(documents.router)
app.include_router(search.router)
app.include_router(feedback.router)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return templates.TemplateResponse(
            request,
            "error.html",
            {"detail": "An internal error occurred. Please contact support."},
            status_code=500,
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal error occurred. Please contact support."},
    )
