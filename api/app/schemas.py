from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class EventOut(BaseModel):
    event_type: str
    event_date: date
    confidence: str
    source_name: str
    source_url: str

    model_config = ConfigDict(from_attributes=True)


class SetOut(BaseModel):
    set_number: str
    name: str
    theme: str
    piece_count: int | None
    image_url: str | None
    status: str
    events: list[EventOut]

    model_config = ConfigDict(from_attributes=True)


class SetPage(BaseModel):
    items: list[SetOut]
    total: int
    page: int
    page_size: int


class ImportRunOut(BaseModel):
    id: int
    source_name: str
    state: str
    started_at: datetime
    finished_at: datetime | None
    imported_count: int
    rejected_count: int
    error: str | None

    model_config = ConfigDict(from_attributes=True)


class ImportStatusOut(BaseModel):
    latest_run: ImportRunOut | None
    latest_success: ImportRunOut | None
    data_age_seconds: float | None
