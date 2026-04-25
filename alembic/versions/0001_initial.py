"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-25
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


case_status = sa.Enum("OPEN", "IN_PROGRESS", "CLOSED", name="casestatus")
case_severity = sa.Enum("CRITICAL", "HIGH", "MEDIUM", "LOW", name="caseseverity")
ioc_type = sa.Enum("IP", "DOMAIN", "URL", "HASH", "CVE", "EMAIL", name="ioctype")
confidence_level = sa.Enum("LOW", "MEDIUM", "HIGH", name="confidencelevel")


def upgrade() -> None:
    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", case_status, nullable=False),
        sa.Column("severity", case_severity, nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("owner", sa.String(length=120), nullable=False),
        sa.Column("tags", sa.String(length=400), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cases_case_id"), "cases", ["case_id"], unique=True)
    op.create_index(op.f("ix_cases_owner"), "cases", ["owner"], unique=False)
    op.create_index(op.f("ix_cases_title"), "cases", ["title"], unique=False)

    op.create_table(
        "timeline_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("details", sa.Text(), nullable=False),
        sa.Column("actor", sa.String(length=120), nullable=False),
        sa.Column("linked_type", sa.String(length=50), nullable=True),
        sa.Column("linked_id", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_timeline_events_case_id"), "timeline_events", ["case_id"], unique=False)
    op.create_index(op.f("ix_timeline_events_timestamp"), "timeline_events", ["timestamp"], unique=False)

    op.create_table(
        "case_iocs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("ioc_type", ioc_type, nullable=False),
        sa.Column("value", sa.String(length=512), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("confidence", confidence_level, nullable=False),
        sa.Column("tags", sa.String(length=400), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_case_iocs_case_id"), "case_iocs", ["case_id"], unique=False)
    op.create_index(op.f("ix_case_iocs_ioc_type"), "case_iocs", ["ioc_type"], unique=False)
    op.create_index(op.f("ix_case_iocs_value"), "case_iocs", ["value"], unique=False)

    op.create_table(
        "artifacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("artifact_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("added_by", sa.String(length=120), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_artifacts_artifact_type"), "artifacts", ["artifact_type"], unique=False)
    op.create_index(op.f("ix_artifacts_case_id"), "artifacts", ["case_id"], unique=False)

    op.create_table(
        "analyst_notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("author", sa.String(length=120), nullable=False),
        sa.Column("important", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["case_id"], ["cases.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analyst_notes_case_id"), "analyst_notes", ["case_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_analyst_notes_case_id"), table_name="analyst_notes")
    op.drop_table("analyst_notes")

    op.drop_index(op.f("ix_artifacts_case_id"), table_name="artifacts")
    op.drop_index(op.f("ix_artifacts_artifact_type"), table_name="artifacts")
    op.drop_table("artifacts")

    op.drop_index(op.f("ix_case_iocs_value"), table_name="case_iocs")
    op.drop_index(op.f("ix_case_iocs_ioc_type"), table_name="case_iocs")
    op.drop_index(op.f("ix_case_iocs_case_id"), table_name="case_iocs")
    op.drop_table("case_iocs")

    op.drop_index(op.f("ix_timeline_events_timestamp"), table_name="timeline_events")
    op.drop_index(op.f("ix_timeline_events_case_id"), table_name="timeline_events")
    op.drop_table("timeline_events")

    op.drop_index(op.f("ix_cases_title"), table_name="cases")
    op.drop_index(op.f("ix_cases_owner"), table_name="cases")
    op.drop_index(op.f("ix_cases_case_id"), table_name="cases")
    op.drop_table("cases")
