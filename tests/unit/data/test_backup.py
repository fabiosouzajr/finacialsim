import gzip
import tempfile
from pathlib import Path

from app.data.backup import backup_sqlite, list_backups, restore_sqlite
from app.data.database import Base, create_engine_for_sqlite


def test_backup_creates_gz_file() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        engine = create_engine_for_sqlite(db_path)
        Base.metadata.create_all(engine)
        engine.dispose()

        backup_dir = Path(tmp) / "backups"
        backup_file = backup_sqlite(db_path, backup_dir)
        assert backup_file.exists()
        assert backup_file.suffix == ".gz"
        with gzip.open(backup_file, "rb") as f:
            header = f.read(16)
        assert header.startswith(b"SQLite format 3")


def test_list_backups_returns_chronological() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        engine = create_engine_for_sqlite(db_path)
        Base.metadata.create_all(engine)
        engine.dispose()

        backup_dir = Path(tmp) / "backups"
        backup_sqlite(db_path, backup_dir)
        backup_sqlite(db_path, backup_dir)
        backups = list_backups(backup_dir)
        assert len(backups) == 2
        # Newest first
        assert backups[0].stat().st_mtime >= backups[1].stat().st_mtime


def test_restore_overwrites_target() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        engine = create_engine_for_sqlite(db_path)
        Base.metadata.create_all(engine)
        engine.dispose()
        original_size = db_path.stat().st_size

        backup_dir = Path(tmp) / "backups"
        backup_file = backup_sqlite(db_path, backup_dir)

        db_path.unlink()
        restore_sqlite(backup_file, db_path)
        assert db_path.exists()
        assert abs(db_path.stat().st_size - original_size) < 100
