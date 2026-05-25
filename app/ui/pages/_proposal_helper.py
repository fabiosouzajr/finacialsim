"""Helper to generate PDF from a simulation in UI context."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from nicegui import ui

from app.services.proposal_service import ProposalService


def generate_and_open_pdf(session, simulation_id: int, user_id: int,
                          data_dir: Path) -> Path | None:
    proposal = ProposalService(session).create(simulation_id, gerado_por=user_id)
    out_dir = data_dir / "propostas"
    out_path = out_dir / f"{proposal.codigo}.pdf"
    ProposalService(session).render_pdf(
        proposal.id, out_path,
        loja={"nome": "FinacialSim Loja"},
        vendedor={"nome": "Vendedor"},
    )
    _open_in_default_viewer(out_path)
    ui.notify(f"PDF gerado: {out_path.name}", type="positive")
    return out_path


def _open_in_default_viewer(path: Path) -> None:
    if sys.platform.startswith("win"):
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)
    else:
        subprocess.run(["xdg-open", str(path)], check=False)
