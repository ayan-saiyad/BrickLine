import csv
import io
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

from sqlalchemy import select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.models import ImportRun, LegoSet, ReleaseEvent, SetChange, utcnow

LOCK_ID = 72193411
REQUIRED_FIELDS = {
    "set_number",
    "name",
    "theme",
    "release_date",
    "retirement_date",
    "status",
    "date_confidence",
    "source_url",
    "source_name",
}
STATUSES = {"upcoming", "available", "retiring", "retired"}
CONFIDENCE = {"confirmed", "estimated"}


@dataclass
class ImportRow:
    set_number: str
    name: str
    theme: str
    piece_count: int | None
    image_url: str | None
    release_date: date
    retirement_date: date | None
    status: str
    confidence: str
    source_url: str
    source_name: str


class ImportBusyError(RuntimeError):
    pass


class ImportValidationError(ValueError):
    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors[:10]))
        self.errors = errors


def fetch_source(location: str) -> str:
    if location.startswith(("https://", "http://")):
        request = Request(location, headers={"User-Agent": "brickline-importer/0.1"})
        with urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8-sig")
    return Path(location).read_text(encoding="utf-8-sig")


def parse_csv(content: str) -> list[ImportRow]:
    reader = csv.DictReader(io.StringIO(content))
    missing = REQUIRED_FIELDS - set(reader.fieldnames or [])
    if missing:
        raise ImportValidationError([f"missing columns: {', '.join(sorted(missing))}"])

    rows: list[ImportRow] = []
    errors: list[str] = []
    seen: set[str] = set()
    for line_number, raw in enumerate(reader, start=2):
        try:
            set_number = raw["set_number"].strip()
            if not set_number or set_number in seen:
                raise ValueError("set number is blank or duplicated")
            seen.add(set_number)
            status = raw["status"].strip().lower()
            confidence = raw["date_confidence"].strip().lower()
            if status not in STATUSES:
                raise ValueError(f"unknown status {status!r}")
            if confidence not in CONFIDENCE:
                raise ValueError(f"unknown confidence {confidence!r}")
            retirement = raw["retirement_date"].strip()
            pieces = raw.get("piece_count", "").strip()
            rows.append(
                ImportRow(
                    set_number=set_number,
                    name=raw["name"].strip(),
                    theme=raw["theme"].strip(),
                    piece_count=int(pieces) if pieces else None,
                    image_url=raw.get("image_url", "").strip() or None,
                    release_date=date.fromisoformat(raw["release_date"].strip()),
                    retirement_date=date.fromisoformat(retirement) if retirement else None,
                    status=status,
                    confidence=confidence,
                    source_url=raw["source_url"].strip(),
                    source_name=raw["source_name"].strip(),
                )
            )
            if not rows[-1].name or not rows[-1].theme or not rows[-1].source_url:
                raise ValueError("name, theme, and source URL are required")
        except (TypeError, ValueError) as exc:
            errors.append(f"line {line_number}: {exc}")
    if errors:
        raise ImportValidationError(errors)
    if not rows:
        raise ImportValidationError(["the source has no records"])
    return rows


def _event_values(row: ImportRow) -> list[tuple[str, date]]:
    values = [("release", row.release_date)]
    if row.retirement_date:
        values.append(("retirement", row.retirement_date))
    return values


def _apply_rows(session: Session, rows: list[ImportRow], run: ImportRun) -> None:
    for row in rows:
        lego_set = session.get(LegoSet, row.set_number)
        before = None
        if lego_set:
            before = {
                "name": lego_set.name,
                "theme": lego_set.theme,
                "piece_count": lego_set.piece_count,
                "image_url": lego_set.image_url,
                "status": lego_set.status,
            }
        else:
            lego_set = LegoSet(set_number=row.set_number)
            session.add(lego_set)

        lego_set.name = row.name
        lego_set.theme = row.theme
        lego_set.piece_count = row.piece_count
        lego_set.image_url = row.image_url
        lego_set.status = row.status
        lego_set.updated_at = utcnow()

        after = {
            "name": row.name,
            "theme": row.theme,
            "piece_count": row.piece_count,
            "image_url": row.image_url,
            "status": row.status,
        }
        changes = {
            key: {"from": before.get(key) if before else None, "to": value}
            for key, value in after.items()
            if before is None or before.get(key) != value
        }

        for event_type, event_date in _event_values(row):
            event = session.scalar(
                select(ReleaseEvent).where(
                    ReleaseEvent.set_number == row.set_number,
                    ReleaseEvent.event_type == event_type,
                )
            )
            event_before = None
            if event:
                event_before = (event.event_date, event.confidence, event.source_url)
            else:
                event = ReleaseEvent(set_number=row.set_number, event_type=event_type)
                session.add(event)
            event.event_date = event_date
            event.confidence = row.confidence
            event.source_name = row.source_name
            event.source_url = row.source_url
            event.import_run_id = run.id
            event.updated_at = utcnow()
            event_after = (event_date, row.confidence, row.source_url)
            if event_before != event_after:
                changes[event_type] = {
                    "from": [str(value) for value in event_before] if event_before else None,
                    "to": [str(value) for value in event_after],
                }

        if row.retirement_date is None:
            retirement = session.scalar(
                select(ReleaseEvent).where(
                    ReleaseEvent.set_number == row.set_number,
                    ReleaseEvent.event_type == "retirement",
                )
            )
            if retirement:
                changes["retirement"] = {
                    "from": [
                        str(retirement.event_date),
                        retirement.confidence,
                        retirement.source_url,
                    ],
                    "to": None,
                }
                session.delete(retirement)

        if changes:
            session.add(SetChange(set_number=row.set_number, import_run_id=run.id, changes=changes))


def run_import(engine: Engine, location: str, source_name: str) -> ImportRun:
    with engine.connect() as connection:
        locked = True
        if connection.dialect.name == "postgresql":
            locked = bool(
                connection.scalar(text("select pg_try_advisory_lock(:id)"), {"id": LOCK_ID})
            )
        if not locked:
            raise ImportBusyError("another import is already running")

        session = Session(bind=connection, expire_on_commit=False)
        run = ImportRun(source_name=source_name, source_url=location, state="running")
        session.add(run)
        session.commit()
        try:
            rows = parse_csv(fetch_source(location))
            _apply_rows(session, rows, run)
            run.state = "succeeded"
            run.imported_count = len(rows)
            run.finished_at = utcnow()
            session.commit()
        except Exception as exc:
            session.rollback()
            run = session.get(ImportRun, run.id)
            run.state = "failed"
            run.finished_at = utcnow()
            run.error = str(exc)[:2000]
            if isinstance(exc, ImportValidationError):
                run.rejected_count = len(exc.errors)
            session.commit()
            raise
        finally:
            session.close()
            if connection.dialect.name == "postgresql":
                connection.execute(text("select pg_advisory_unlock(:id)"), {"id": LOCK_ID})
                connection.commit()
        return run
