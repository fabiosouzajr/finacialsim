import tempfile
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite, get_session_factory


@pytest.fixture()
def session():
    with tempfile.TemporaryDirectory() as tmp:
        engine = create_engine_for_sqlite(Path(tmp) / "test.db")
        Base.metadata.create_all(engine)
        SessionLocal = get_session_factory(engine)
        with SessionLocal() as s:
            yield s
        engine.dispose()  # Windows: release file handle before temp dir cleanup
