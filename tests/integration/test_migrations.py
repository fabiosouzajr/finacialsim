import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.mark.integration
def test_alembic_upgrade_and_seed() -> None:
    """Run alembic upgrade head against a temp DB and verify seed data."""
    alembic = Path(sys.executable).parent / "alembic"
    with tempfile.TemporaryDirectory() as tmp:
        db_file = Path(tmp) / "test.db"

        result = subprocess.run(
            [str(alembic), "-x", f"db_url=sqlite:///{db_file}", "upgrade", "head"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        assert db_file.exists()

        conn = sqlite3.connect(str(db_file))
        count_users = conn.execute("SELECT COUNT(*) FROM users WHERE nome='Admin'").fetchone()[0]
        count_rules = conn.execute("SELECT COUNT(*) FROM business_rules").fetchone()[0]
        conn.close()
        assert count_users == 1
        assert count_rules >= 10
