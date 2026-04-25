from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db import init_db
from app.routers import api_artifacts, api_cases, api_iocs, api_reports, web

app = FastAPI(title=settings.app_name, version="0.1.0")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(web.router)
app.include_router(api_cases.router)
app.include_router(api_iocs.router)
app.include_router(api_artifacts.router)
app.include_router(api_reports.router)


@app.on_event("startup")
def startup_event() -> None:
    init_db()
