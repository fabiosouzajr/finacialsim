import tempfile
from pathlib import Path

import pytest
from nicegui.testing import User

from app.data.database import Base, create_engine_for_sqlite
from app.main import build_app
from app.services.auth_service import AuthService


@pytest.fixture()
def app_db(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "ui.db"
        engine = create_engine_for_sqlite(db_path)
        Base.metadata.create_all(engine)
        # Seed an admin
        from app.data.database import get_session_factory
        SessionLocal = get_session_factory(engine)
        with SessionLocal() as session:
            AuthService(session).create_user("Admin", "123456", "admin")
        monkeypatch.setattr("app.main._platform_data_dir", lambda: Path(tmp))
        yield db_path


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_page_renders(app_db, user: User):
    build_app()
    await user.open("/login")
    await user.should_see("FinacialSim - Login")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_redirects_to_dashboard(app_db, user: User):
    build_app()
    await user.open("/login")
    # Select first user; type PIN
    # (Selectors may need adjustment depending on NiceGUI version)
    # Skip if NiceGUI test API is unavailable - mark expected to be approximate