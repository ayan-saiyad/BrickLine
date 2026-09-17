from contextlib import asynccontextmanager
from datetime import UTC, date, datetime

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.database import get_db
from app.metrics import metrics_response, track_requests
from app.models import ImportRun, LegoSet, ReleaseEvent
from app.schemas import ImportStatusOut, SetOut, SetPage


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(title="Brickline API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().allowed_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.middleware("http")(track_requests)


@app.get("/api/health")
def health(session: Session = Depends(get_db)) -> dict[str, str]:
    session.execute(select(1))
    return {"status": "ok"}


@app.get("/api/sets", response_model=SetPage)
def list_sets(
    q: str | None = None,
    theme: list[str] = Query(default=[]),
    status: list[str] = Query(default=[]),
    event_type: str | None = Query(default=None, pattern="^(release|retirement)$"),
    date_from: date | None = None,
    date_to: date | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=250),
    session: Session = Depends(get_db),
) -> SetPage:
    statement = select(LegoSet).options(selectinload(LegoSet.events))
    count_statement = select(func.count()).select_from(LegoSet)
    filters = []
    if q:
        filters.append(or_(LegoSet.name.ilike(f"%{q}%"), LegoSet.set_number.ilike(f"%{q}%")))
    if theme:
        filters.append(LegoSet.theme.in_(theme))
    if status:
        filters.append(LegoSet.status.in_(status))
    if event_type or date_from or date_to:
        event_query = select(ReleaseEvent.set_number)
        if event_type:
            event_query = event_query.where(ReleaseEvent.event_type == event_type)
        if date_from:
            event_query = event_query.where(ReleaseEvent.event_date >= date_from)
        if date_to:
            event_query = event_query.where(ReleaseEvent.event_date <= date_to)
        filters.append(LegoSet.set_number.in_(event_query))
    if filters:
        statement = statement.where(*filters)
        count_statement = count_statement.where(*filters)

    total = session.scalar(count_statement) or 0
    items = session.scalars(
        statement.order_by(LegoSet.name).offset((page - 1) * page_size).limit(page_size)
    ).all()
    for item in items:
        item.events.sort(key=lambda event: event.event_date)
    return SetPage(items=items, total=total, page=page, page_size=page_size)


@app.get("/api/sets/{set_number}", response_model=SetOut)
def get_set(set_number: str, session: Session = Depends(get_db)) -> LegoSet:
    lego_set = session.scalar(
        select(LegoSet)
        .options(selectinload(LegoSet.events))
        .where(LegoSet.set_number == set_number)
    )
    if not lego_set:
        raise HTTPException(status_code=404, detail="set not found")
    lego_set.events.sort(key=lambda event: event.event_date)
    return lego_set


@app.get("/api/themes", response_model=list[str])
def themes(session: Session = Depends(get_db)) -> list[str]:
    return list(session.scalars(select(LegoSet.theme).distinct().order_by(LegoSet.theme)))


@app.get("/api/imports/status", response_model=ImportStatusOut)
def import_status(session: Session = Depends(get_db)) -> ImportStatusOut:
    latest = session.scalar(select(ImportRun).order_by(ImportRun.started_at.desc()).limit(1))
    success = session.scalar(
        select(ImportRun)
        .where(ImportRun.state == "succeeded")
        .order_by(ImportRun.finished_at.desc())
        .limit(1)
    )
    age = None
    if success and success.finished_at:
        finished = success.finished_at
        if finished.tzinfo is None:
            finished = finished.replace(tzinfo=UTC)
        age = (datetime.now(UTC) - finished).total_seconds()
    return ImportStatusOut(latest_run=latest, latest_success=success, data_age_seconds=age)


@app.get("/metrics", include_in_schema=False)
def metrics(session: Session = Depends(get_db)):
    return metrics_response(session)
