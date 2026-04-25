from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class CaseStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class CaseSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class IOCType(str, enum.Enum):
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    HASH = "hash"
    CVE = "cve"
    EMAIL = "email"


class ConfidenceLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Case(Base):
    __tablename__ = "cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus), default=CaseStatus.OPEN)
    severity: Mapped[CaseSeverity] = mapped_column(Enum(CaseSeverity), default=CaseSeverity.MEDIUM)
    priority: Mapped[int] = mapped_column(Integer, default=3)
    owner: Mapped[str] = mapped_column(String(120), index=True)
    tags: Mapped[str] = mapped_column(String(400), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    timeline_events: Mapped[list[TimelineEvent]] = relationship(
        back_populates="case", cascade="all, delete-orphan", order_by="TimelineEvent.timestamp"
    )
    iocs: Mapped[list[CaseIOC]] = relationship(back_populates="case", cascade="all, delete-orphan")
    artifacts: Mapped[list[Artifact]] = relationship(back_populates="case", cascade="all, delete-orphan")
    notes: Mapped[list[AnalystNote]] = relationship(back_populates="case", cascade="all, delete-orphan")


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    event_type: Mapped[str] = mapped_column(String(64), default="generic")
    title: Mapped[str] = mapped_column(String(255))
    details: Mapped[str] = mapped_column(Text, default="")
    actor: Mapped[str] = mapped_column(String(120), default="system")
    linked_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    linked_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    case: Mapped[Case] = relationship(back_populates="timeline_events")


class CaseIOC(Base):
    __tablename__ = "case_iocs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    ioc_type: Mapped[IOCType] = mapped_column(Enum(IOCType), index=True)
    value: Mapped[str] = mapped_column(String(512), index=True)
    source: Mapped[str] = mapped_column(String(255), default="")
    confidence: Mapped[ConfidenceLevel] = mapped_column(Enum(ConfidenceLevel), default=ConfidenceLevel.MEDIUM)
    tags: Mapped[str] = mapped_column(String(400), default="")
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped[Case] = relationship(back_populates="iocs")


class Artifact(Base):
    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    artifact_type: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, default="")
    added_by: Mapped[str] = mapped_column(String(120), default="analyst")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped[Case] = relationship(back_populates="artifacts")


class AnalystNote(Base):
    __tablename__ = "analyst_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    case_id: Mapped[int] = mapped_column(ForeignKey("cases.id", ondelete="CASCADE"), index=True)
    note: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(120), default="analyst")
    important: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    case: Mapped[Case] = relationship(back_populates="notes")
