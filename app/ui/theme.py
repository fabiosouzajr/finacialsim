"""Cores, tipografia, espaçamentos da UI."""

from __future__ import annotations

# Paleta (configuravel em runtime via Configuracoes)
PRIMARY = "#1565C0"        # azul confiavel
SECONDARY = "#26A69A"
ACCENT = "#FFB300"
ERROR = "#D32F2F"
WARNING = "#FB8C00"
SUCCESS = "#43A047"
BG = "#F5F7FB"
SURFACE = "#FFFFFF"
TEXT = "#1A2233"
TEXT_MUTED = "#6B7785"

FONT_FAMILY = "Inter, 'Segoe UI', Roboto, Arial, sans-serif"

# Tailwind-like sizes
SIZE_XS = "0.75rem"
SIZE_SM = "0.875rem"
SIZE_BASE = "1rem"
SIZE_LG = "1.25rem"
SIZE_XL = "1.5rem"
SIZE_2XL = "2rem"

RADIUS = "0.5rem"


def apply_global_styles() -> None:
    """Call once at app startup to register CSS."""
    from nicegui import ui
    ui.add_head_html(f"""
    <style>
      :root {{
        --primary: {PRIMARY};
        --secondary: {SECONDARY};
        --accent: {ACCENT};
        --error: {ERROR};
        --warning: {WARNING};
        --success: {SUCCESS};
        --bg: {BG};
        --surface: {SURFACE};
        --text: {TEXT};
        --text-muted: {TEXT_MUTED};
      }}
      body {{ font-family: {FONT_FAMILY}; background: var(--bg); color: var(--text); }}
      .kpi-card {{ background: var(--surface); border-radius: {RADIUS}; padding: 1.25rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }}
      .kpi-value {{ font-size: {SIZE_2XL}; font-weight: 700; color: var(--primary); }}
      .kpi-label {{ font-size: {SIZE_SM}; color: var(--text-muted); }}
      .badge-warn {{ background: var(--warning); color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; }}
    </style>
    """)