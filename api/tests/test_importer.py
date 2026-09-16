from sqlalchemy import func, select

from app.importer import ImportValidationError, run_import
from app.models import ImportRun, LegoSet, ReleaseEvent, SetChange

CSV = (
    "set_number,name,theme,piece_count,image_url,release_date,retirement_date,"
    "status,date_confidence,source_url,source_name\n"
    "100-1,Test Set,Ideas,100,,2026-01-01,2027-01-01,available,confirmed,"
    "https://example.com/set,Example\n"
)


def test_import_is_idempotent(db_engine, session, tmp_path):
    source = tmp_path / "sets.csv"
    source.write_text(CSV)

    run_import(db_engine, str(source), "test")
    run_import(db_engine, str(source), "test")
    session.expire_all()

    assert session.scalar(select(func.count()).select_from(LegoSet)) == 1
    assert session.scalar(select(func.count()).select_from(ReleaseEvent)) == 2
    assert session.scalar(select(func.count()).select_from(SetChange)) == 1
    assert session.scalar(select(func.count()).select_from(ImportRun)) == 2


def test_bad_file_keeps_existing_data(db_engine, session, tmp_path):
    source = tmp_path / "sets.csv"
    source.write_text(CSV)
    run_import(db_engine, str(source), "test")
    source.write_text(CSV.replace("confirmed", "maybe"))

    try:
        run_import(db_engine, str(source), "test")
    except ImportValidationError:
        pass

    session.expire_all()
    assert session.scalar(select(func.count()).select_from(LegoSet)) == 1
    failed = session.scalar(
        select(ImportRun).where(ImportRun.state == "failed").order_by(ImportRun.id.desc())
    )
    assert failed.rejected_count == 1
