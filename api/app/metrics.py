import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ImportRun

REQUESTS = Counter(
    "brickline_http_requests_total",
    "HTTP requests handled by the API",
    ["method", "route", "status"],
)
LATENCY = Histogram(
    "brickline_http_request_duration_seconds",
    "API request latency",
    ["method", "route"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5),
)
IMPORT_SUCCESS = Gauge(
    "brickline_import_last_success_unixtime",
    "Time of the latest successful import",
    ["source"],
)
IMPORT_FAILURES = Gauge(
    "brickline_import_failed_runs",
    "Persisted count of failed import runs",
    ["source"],
)
IMPORT_REJECTED = Gauge(
    "brickline_import_last_rejected_records",
    "Rejected records in the latest import run",
    ["source"],
)


async def track_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    started = time.perf_counter()
    response = await call_next(request)
    route = request.scope.get("route")
    route_name = getattr(route, "path", "unmatched")
    REQUESTS.labels(request.method, route_name, response.status_code).inc()
    LATENCY.labels(request.method, route_name).observe(time.perf_counter() - started)
    return response


def metrics_response(session: Session) -> Response:
    sources = session.scalars(select(ImportRun.source_name).distinct()).all()
    for source in sources:
        last_success = session.scalar(
            select(ImportRun)
            .where(ImportRun.source_name == source, ImportRun.state == "succeeded")
            .order_by(ImportRun.finished_at.desc())
            .limit(1)
        )
        latest = session.scalar(
            select(ImportRun)
            .where(ImportRun.source_name == source)
            .order_by(ImportRun.started_at.desc())
            .limit(1)
        )
        failures = session.scalar(
            select(func.count())
            .select_from(ImportRun)
            .where(ImportRun.source_name == source, ImportRun.state == "failed")
        )
        if last_success and last_success.finished_at:
            IMPORT_SUCCESS.labels(source).set(last_success.finished_at.timestamp())
        IMPORT_FAILURES.labels(source).set(failures or 0)
        IMPORT_REJECTED.labels(source).set(latest.rejected_count if latest else 0)
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
