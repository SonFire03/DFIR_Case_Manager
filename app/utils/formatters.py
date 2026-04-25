from __future__ import annotations

from datetime import datetime


def utc_now() -> datetime:
    return datetime.utcnow()


def normalize_tags(raw_tags: str) -> str:
    tags = [t.strip().lower() for t in raw_tags.split(",") if t.strip()]
    unique = sorted(set(tags))
    return ",".join(unique)
