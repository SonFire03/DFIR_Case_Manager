from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "IncidentDesk"
    environment: str = os.getenv("INCIDENTDESK_ENV", "dev")
    database_url: str = os.getenv("INCIDENTDESK_DATABASE_URL", "sqlite:///./incidentdesk.db")
    secret_key: str = os.getenv("INCIDENTDESK_SECRET_KEY", "incidentdesk-dev-key")


settings = Settings()
