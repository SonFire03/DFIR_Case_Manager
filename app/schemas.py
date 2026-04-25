from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.models import CaseSeverity, CaseStatus, ConfidenceLevel, IOCType


class CaseBase(BaseModel):
    title: str
    description: str = ""
    severity: CaseSeverity = CaseSeverity.MEDIUM
    priority: int = Field(default=3, ge=1, le=5)
    owner: str
    tags: str = ""


class CaseCreate(CaseBase):
    case_id: str | None = None


class CaseUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: CaseStatus | None = None
    severity: CaseSeverity | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    owner: str | None = None
    tags: str | None = None


class CaseRead(CaseBase):
    case_id: str
    status: CaseStatus
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None

    class Config:
        from_attributes = True


class TimelineCreate(BaseModel):
    timestamp: datetime | None = None
    event_type: str = "generic"
    title: str
    details: str = ""
    actor: str = "analyst"
    linked_type: str | None = None
    linked_id: str | None = None


class TimelineRead(TimelineCreate):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class IOCCreate(BaseModel):
    ioc_type: IOCType
    value: str
    source: str = ""
    confidence: ConfidenceLevel = ConfidenceLevel.MEDIUM
    tags: str = ""
    note: str = ""


class IOCUpdate(BaseModel):
    ioc_type: IOCType | None = None
    value: str | None = None
    source: str | None = None
    confidence: ConfidenceLevel | None = None
    tags: str | None = None
    note: str | None = None


class IOCRead(IOCCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ArtifactCreate(BaseModel):
    artifact_type: str
    title: str
    content: str
    description: str = ""
    added_by: str = "analyst"


class ArtifactUpdate(BaseModel):
    artifact_type: str | None = None
    title: str | None = None
    content: str | None = None
    description: str | None = None
    added_by: str | None = None


class ArtifactRead(ArtifactCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class NoteCreate(BaseModel):
    note: str
    author: str = "analyst"
    important: bool = False


class NoteRead(NoteCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
