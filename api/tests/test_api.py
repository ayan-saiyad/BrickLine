from datetime import UTC, date, datetime

from app.models import ImportRun, LegoSet, ReleaseEvent


def test_list_sets_filters_and_returns_events(client, session):
    run = ImportRun(source_name="test", source_url="fixture", state="succeeded")
    session.add(run)
    session.flush()
    lego_set = LegoSet(set_number="100-1", name="Little House", theme="Ideas", status="available")
    lego_set.events.append(
        ReleaseEvent(
            event_type="release",
            event_date=date(2026, 1, 1),
            confidence="confirmed",
            source_name="Example",
            source_url="https://example.com",
            import_run_id=run.id,
        )
    )
    session.add(lego_set)
    session.commit()

    response = client.get("/api/sets", params={"q": "house", "theme": "Ideas"})

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["events"][0]["event_type"] == "release"


def test_health_and_metrics(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    metrics = client.get("/metrics")
    assert metrics.status_code == 200
    assert "brickline_http_requests_total" in metrics.text


def test_metrics_include_persisted_import_counts(client, session):
    session.add_all(
        [
            ImportRun(
                source_name="fixture",
                source_url="file.csv",
                state="succeeded",
                finished_at=datetime.now(UTC),
            ),
            ImportRun(source_name="fixture", source_url="missing.csv", state="failed"),
        ]
    )
    session.commit()

    metrics = client.get("/metrics").text

    assert 'brickline_import_successful_runs{source="fixture"} 1.0' in metrics
    assert 'brickline_import_failed_runs{source="fixture"} 1.0' in metrics


def test_bad_date_filter_is_rejected(client):
    response = client.get("/api/sets", params={"date_from": "next-week"})

    assert response.status_code == 422
