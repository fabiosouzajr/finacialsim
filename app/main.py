"""FinacialSim entry point - boots NiceGUI in a pywebview window."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from loguru import logger
from nicegui import ui

from app.data.database import create_engine_for_sqlite
from app.ui.pages.amortizacao import build_amortizacao_page
from app.ui.pages.apis import build_apis_page
from app.ui.pages.cadastro import build_cadastro_page
from app.ui.pages.comparativo import build_comparativo_page
from app.ui.pages.configuracoes import build_configuracoes_page
from app.ui.pages.dashboard import build_dashboard_page
from app.ui.pages.docs import build_docs_page
from app.ui.pages.indicadores import build_indicadores_page
from app.ui.pages.logs import build_logs_page
from app.ui.pages.login import build_login_page
from app.ui.pages.simulacao import build_simulacao_page
from app.ui.theme import apply_global_styles
from app.utils.logger import setup_logging


def _platform_data_dir() -> Path:
    if sys.platform.startswith("win"):
        base = Path.home() / "AppData" / "Roaming" / "FinacialSim"
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support" / "FinacialSim"
    else:
        base = Path.home() / ".local" / "share" / "FinacialSim"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _run_migrations(db_path: Path) -> None:
    """Run alembic upgrade head on startup. Idempotent."""
    project_root = Path(__file__).resolve().parents[1]
    alembic_ini = project_root / "alembic.ini"
    if not alembic_ini.exists():
        logger.warning("alembic.ini not found - skipping migrations")
        return
    env = {"FINACIALSIM_DB_URL": f"sqlite:///{db_path}"}
    cmd = [sys.executable, "-m", "alembic", "-c", str(alembic_ini),
           "-x", f"db_url=sqlite:///{db_path}", "upgrade", "head"]
    result = subprocess.run(cmd, cwd=project_root, env={**os.environ, **env},
                            capture_output=True, text=True)
    if result.returncode != 0:
        logger.error(f"Alembic upgrade failed: {result.stderr}")
    else:
        logger.info("Migrations applied (alembic upgrade head)")


def build_app() -> None:
    data_dir = _platform_data_dir()
    setup_logging(data_dir / "logs")
    db_path = data_dir / "finacialsim.db"

    # Run migrations if DB is new or schema outdated
    _run_migrations(db_path)

    engine = create_engine_for_sqlite(db_path)
    apply_global_styles()

    build_login_page(engine)
    build_dashboard_page(engine)
    build_cadastro_page(engine)
    build_simulacao_page(engine)
    build_comparativo_page(engine)
    build_amortizacao_page(engine)
    build_indicadores_page(engine)
    build_configuracoes_page(engine)
    build_apis_page(engine)
    build_logs_page(engine)
    build_docs_page(engine)

    @ui.page("/")
    def root() -> None:
        ui.navigate.to("/login")


def main() -> None:
    import os  # noqa: F401 - used inside build_app via _run_migrations
    build_app()
    ui.run(
        title="FinacialSim",
        favicon="🚗",
        native=True,
        window_size=(1400, 900),
        storage_secret="finacialsim-secret-change-me",
        reload=False,
        show=False,
    )


# Make `os` available to _run_migrations (imported lazily above to avoid
# UnboundLocalError when invoked outside of main())
import os  # noqa: E402