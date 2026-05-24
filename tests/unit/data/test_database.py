import tempfile
from pathlib import Path

from app.data.database import create_engine_for_sqlite, get_session_factory


def test_create_engine_creates_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        engine = create_engine_for_sqlite(db_path)
        with engine.connect() as conn:
            conn.exec_driver_sql("SELECT 1")
        with engine.connect() as conn:
            mode = conn.exec_driver_sql("PRAGMA journal_mode").scalar()
            assert mode == "wal"
        engine.dispose()  # Windows: release file handle before temp dir cleanup


def test_session_factory_returns_callable() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        engine = create_engine_for_sqlite(db_path)
        SessionLocal = get_session_factory(engine)
        with SessionLocal() as session:
            assert session.execute(__import__("sqlalchemy").text("SELECT 1")).scalar() == 1
        engine.dispose()  # Windows: release file handle before temp dir cleanup
