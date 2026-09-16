from datetime import UTC, date, datetime
from typing import Any

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow() -> datetime:
    return datetime.now(UTC)


class LegoSet(Base):
    __tablename__ = "lego_sets"

    set_number: Mapped[str] = mapped_column(String(24), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    theme: Mapped[str] = mapped_column(String(100), index=True)
    piece_count: Mapped[int | None] = mapped_column(Integer)
    image_url: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(24), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    events: Mapped[list["ReleaseEvent"]] = relationship(
        back_populates="lego_set", cascade="all, delete-orphan"
    )


class ImportRun(Base):
    __tablename__ = "import_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_name: Mapped[str] = mapped_column(String(120), index=True)
    source_url: Mapped[str] = mapped_column(Text)
    state: Mapped[str] = mapped_column(String(20), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    imported_count: Mapped[int] = mapped_column(Integer, default=0)
    rejected_count: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text)


class ReleaseEvent(Base):
    __tablename__ = "release_events"
    __table_args__ = (UniqueConstraint("set_number", "event_type"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    set_number: Mapped[str] = mapped_column(
        ForeignKey("lego_sets.set_number", ondelete="CASCADE"), index=True
    )
    event_type: Mapped[str] = mapped_column(String(20), index=True)
    event_date: Mapped[date] = mapped_column(Date, index=True)
    confidence: Mapped[str] = mapped_column(String(20))
    source_name: Mapped[str] = mapped_column(String(120))
    source_url: Mapped[str] = mapped_column(Text)
    import_run_id: Mapped[int] = mapped_column(ForeignKey("import_runs.id"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    lego_set: Mapped[LegoSet] = relationship(back_populates="events")


class SetChange(Base):
    __tablename__ = "set_changes"

    id: Mapped[int] = mapped_column(primary_key=True)
    set_number: Mapped[str] = mapped_column(String(24), index=True)
    import_run_id: Mapped[int] = mapped_column(ForeignKey("import_runs.id"))
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    changes: Mapped[dict[str, Any]] = mapped_column(JSON)
