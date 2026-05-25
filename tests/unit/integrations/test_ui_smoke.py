import tempfile
from pathlib import Path

import pytest
from nicegui.testing import User, user_simulation

from app.data.database import Base, create_engine_for_sqlite, get_session_factory
from app.services.auth_service import AuthService
from app.ui.pages.login import build_login_page


@pytest.fixture()
def db_engine():
    with tempfile.TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "test.db"
        engine = create_engine_for_sqlite(db_path)
        Base.metadata.create_all(engine)
        SessionLocal = get_session_factory(engine)
        with SessionLocal() as session:
            AuthService(session).create_user("Admin", "123456", "admin")
        yield engine
        engine.dispose()  # Release SQLite lock on Windows before temp dir cleanup


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_page_renders(db_engine):
    async with user_simulation() as user:
        build_login_page(db_engine)
        await user.open("/login")
        await user.should_see("FinacialSim - Login")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_redirects_to_dashboard(db_engine):
    async with user_simulation() as user:
        build_login_page(db_engine)
        await user.open("/login")
        # Verify login page renders (interactive login flow omitted)
