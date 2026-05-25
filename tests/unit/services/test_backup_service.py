import tempfile
from pathlib import Path

import pytest

from app.data.database import Base, create_engine_for_sqlite
from app.services.backup_service import BackupService


def test_backup_now_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        db = tmp_path / "test.db"
        engine = create_engine_for_sqlite(db)
        Base.metadata.create_all(engine)
        engine.dispose()

        svc = BackupService(db_path=db, backup_dir=tmp_path / "backups")
        path = svc.backup_now()
        assert path.exists()
        backups = svc.list()
        assert len(backups) == 1
