"""
palette.py — RanBeam
=====================
Ported from RanOptics' core/themes.py (v2.2.1) so the two apps share one
visual identity. Supports 5 palettes x 2 modes (dark/light), switchable at
runtime via apply_theme(). Other modules must `import palette as _pal` and
read `_pal.X` at call time (never `from palette import X`) so they pick up
live theme switches — values are rebound onto this module's namespace by
_load(), not reassigned as new module objects.
"""

from __future__ import annotations
from PySide6.QtGui import QFont

# ── Theme palettes (identical values to RanOptics core/themes.py) ────────────
_DARK = dict(
    BG       = "#0e130f",
    MANTLE   = "#0a0e0b",
    CRUST    = "#0a0e0b",
    PANEL    = "#141b15",
    PANEL2   = "#1a221b",
    SURFACE2 = "#222e24",
    BORDER   = "#2a382c",
    FG       = "#e7eee8",
    FG_DIM   = "#95a797",
    FG_LBL   = "#65786a",
    ACCENT   = "#22e39c",
    ACCENTH  = "#4eecb3",
    ACCENT2  = "#f0c052",
    AINK     = "#05140c",
    ASOFT    = "rgba(34,227,156,.14)",
    COPPER   = "#ff9a4d",
    CSOFT    = "rgba(255,154,77,.15)",
    ERROR    = "#e0705f",
    WARN     = "#ff9a4d",
    RAN_CLR  = "#22e39c",
    SHADOW   = "0 8px 30px rgba(0,0,0,.45)",
)

_LIGHT = dict(
    BG       = "#e9efe7",
    MANTLE   = "#dde6db",
    CRUST    = "#dde6db",
    PANEL    = "#ffffff",
    PANEL2   = "#f4f8f3",
    SURFACE2 = "#e1e9df",
    BORDER   = "#cfdace",
    FG       = "#15201a",
    FG_DIM   = "#566656",
    FG_LBL   = "#859786",
    ACCENT   = "#05805a",
    ACCENTH  = "#046b4d",
    ACCENT2  = "#8a5d09",
    AINK     = "#ffffff",
    ASOFT    = "rgba(5,128,90,.11)",
    COPPER   = "#d9581b",
    CSOFT    = "rgba(217,88,27,.13)",
    ERROR    = "#c4503e",
    WARN     = "#d9581b",
    RAN_CLR  = "#05805a",
    SHADOW   = "0 8px 30px rgba(60,80,60,.16)",
)

_PETROL = dict(
    BG       = "#0b1618",   MANTLE   = "#081113",   CRUST    = "#081113",
    PANEL    = "#112124",   PANEL2   = "#16292d",   SURFACE2 = "#1c333a",
    BORDER   = "#1f3a3f",
    FG       = "#e2eff0",   FG_DIM   = "#8fa8ab",   FG_LBL   = "#64807f",
    ACCENT   = "#22e39c",   ACCENTH  = "#4fecb3",   ACCENT2  = "#ffcb5c",
    AINK     = "#04150d",
    ASOFT    = "rgba(34,227,156,.14)",
    COPPER   = "#ff8f6b",
    CSOFT    = "rgba(255,143,107,.15)",
    ERROR    = "#f4626d",   WARN     = "#ffcb5c",   RAN_CLR  = "#22e39c",
    SHADOW   = "0 8px 30px rgba(0,0,0,.45)",
)

_SULFUR = dict(
    BG       = "#0c1226",   MANTLE   = "#080d1c",   CRUST    = "#080d1c",
    PANEL    = "#131b33",   PANEL2   = "#18213d",   SURFACE2 = "#1f2a4a",
    BORDER   = "#223052",
    FG       = "#e3ebfa",   FG_DIM   = "#90a0c0",   FG_LBL   = "#66779c",
    ACCENT   = "#e8e14f",   ACCENTH  = "#f2ec7a",   ACCENT2  = "#5fb8d3",
    AINK     = "#1a1900",
    ASOFT    = "rgba(232,225,79,.14)",
    COPPER   = "#ff8f6b",
    CSOFT    = "rgba(255,143,107,.15)",
    ERROR    = "#ff6480",   WARN     = "#ffb454",   RAN_CLR  = "#e8e14f",
    SHADOW   = "0 8px 30px rgba(0,0,0,.45)",
)

_ULTRAVIOLET = dict(
    BG       = "#150d1f",   MANTLE   = "#100819",   CRUST    = "#100819",
    PANEL    = "#1e1329",   PANEL2   = "#251831",   SURFACE2 = "#2e1f3d",
    BORDER   = "#342244",
    FG       = "#ece4f5",   FG_DIM   = "#a795b8",   FG_LBL   = "#7a6a8a",
    ACCENT   = "#b8f24f",   ACCENTH  = "#c9f57a",   ACCENT2  = "#ff8fd0",
    AINK     = "#0d1400",
    ASOFT    = "rgba(184,242,79,.14)",
    COPPER   = "#6ec8ff",
    CSOFT    = "rgba(110,200,255,.15)",
    ERROR    = "#ff5c7a",   WARN     = "#ffb454",   RAN_CLR  = "#b8f24f",
    SHADOW   = "0 8px 30px rgba(0,0,0,.5)",
)

_OXBLOOD = dict(
    BG       = "#1a1012",   MANTLE   = "#140c0e",   CRUST    = "#140c0e",
    PANEL    = "#241619",   PANEL2   = "#2b1b1e",   SURFACE2 = "#362227",
    BORDER   = "#3d262a",
    FG       = "#f2e6e8",   FG_DIM   = "#b09499",   FG_LBL   = "#8a6d73",
    ACCENT   = "#4fe0b0",   ACCENTH  = "#7ae9c6",   ACCENT2  = "#dba45f",
    AINK     = "#05140f",
    ASOFT    = "rgba(79,224,176,.14)",
    COPPER   = "#ff9ea8",
    CSOFT    = "rgba(255,158,168,.15)",
    ERROR    = "#ff5c6a",   WARN     = "#dba45f",   RAN_CLR  = "#4fe0b0",
    SHADOW   = "0 8px 30px rgba(0,0,0,.45)",
)

_PETROL_LIGHT = dict(
    BG       = "#dfeef0",   MANTLE   = "#cbe4e6",   CRUST    = "#cbe4e6",
    PANEL    = "#f4fbfb",   PANEL2   = "#e9f5f6",   SURFACE2 = "#d3e9eb",
    BORDER   = "#a9cdd0",
    FG       = "#062225",   FG_DIM   = "#43676a",   FG_LBL   = "#71969a",
    ACCENT   = "#00795a",   ACCENTH  = "#005f47",   ACCENT2  = "#8a5f00",
    AINK     = "#ffffff",
    ASOFT    = "rgba(0,121,90,.13)",
    COPPER   = "#c04a22",
    CSOFT    = "rgba(192,74,34,.13)",
    ERROR    = "#c0392b",   WARN     = "#8a5f00",   RAN_CLR  = "#00795a",
    SHADOW   = "0 8px 30px rgba(20,60,62,.17)",
)

_SULFUR_LIGHT = dict(
    BG       = "#dbe6f7",   MANTLE   = "#c6d7ef",   CRUST    = "#c6d7ef",
    PANEL    = "#f4f8ff",   PANEL2   = "#e8eefb",   SURFACE2 = "#cfdcf3",
    BORDER   = "#a6bcdd",
    FG       = "#0f1730",   FG_DIM   = "#4a577a",   FG_LBL   = "#7784a6",
    ACCENT   = "#6b6000",   ACCENTH  = "#544c00",   ACCENT2  = "#1c6b85",
    AINK     = "#ffffff",
    ASOFT    = "rgba(107,96,0,.13)",
    COPPER   = "#c0512a",
    CSOFT    = "rgba(192,81,42,.13)",
    ERROR    = "#b3243c",   WARN     = "#8a6a00",   RAN_CLR  = "#6b6000",
    SHADOW   = "0 8px 30px rgba(30,45,90,.16)",
)

_ULTRAVIOLET_LIGHT = dict(
    BG       = "#f4e9fb",   MANTLE   = "#e9d8f4",   CRUST    = "#e9d8f4",
    PANEL    = "#fdfaff",   PANEL2   = "#f9f2fd",   SURFACE2 = "#eeddf8",
    BORDER   = "#d0b6e6",
    FG       = "#1d0f30",   FG_DIM   = "#5b4873",   FG_LBL   = "#8977a1",
    ACCENT   = "#6a2fa8",   ACCENTH  = "#52237f",   ACCENT2  = "#476d00",
    AINK     = "#ffffff",
    ASOFT    = "rgba(106,47,168,.12)",
    COPPER   = "#0f6fa8",
    CSOFT    = "rgba(15,111,168,.13)",
    ERROR    = "#c02a55",   WARN     = "#8a5a00",   RAN_CLR  = "#6a2fa8",
    SHADOW   = "0 8px 30px rgba(60,30,90,.17)",
)

_OXBLOOD_LIGHT = dict(
    BG       = "#f5e8ea",   MANTLE   = "#ebd5d9",   CRUST    = "#ebd5d9",
    PANEL    = "#fffbfc",   PANEL2   = "#f9eef0",   SURFACE2 = "#f0dbdf",
    BORDER   = "#d9b6bc",
    FG       = "#2a0f13",   FG_DIM   = "#6d484e",   FG_LBL   = "#987076",
    ACCENT   = "#00706f",   ACCENTH  = "#005555",   ACCENT2  = "#8a5a12",
    AINK     = "#ffffff",
    ASOFT    = "rgba(0,112,111,.13)",
    COPPER   = "#b03a4a",
    CSOFT    = "rgba(176,58,74,.13)",
    ERROR    = "#b3122b",   WARN     = "#8a5a12",   RAN_CLR  = "#00706f",
    SHADOW   = "0 8px 30px rgba(80,35,40,.16)",
)

THEMES = {
    "Petrol":        {"dark": _PETROL,      "light": _PETROL_LIGHT},
    "Classic Green": {"dark": _DARK,        "light": _LIGHT},
    "Sulfur Sea":    {"dark": _SULFUR,      "light": _SULFUR_LIGHT},
    "Ultraviolet":   {"dark": _ULTRAVIOLET, "light": _ULTRAVIOLET_LIGHT},
    "Oxblood":       {"dark": _OXBLOOD,     "light": _OXBLOOD_LIGHT},
}
DEFAULT_THEME = "Petrol"

_current_mode  = "dark"
_current_theme = DEFAULT_THEME


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def _load(palette: dict) -> None:
    """Inject palette into module globals, derive RanBeam-specific field-state
    colours from it, and rebuild every stylesheet string."""
    import sys
    m = sys.modules[__name__]
    for k, v in palette.items():
        setattr(m, k, v)

    # Legacy aliases kept alive for anything still referencing the old names.
    m.PEACH     = m.ACCENT
    m.HIGHLIGHT = m.WARN
    m.SUCCESS   = m.RAN_CLR

    # --- RanBeam field-state colours, derived from the active palette -----
    # "Computed" field: soft accent tint, accent-hover border, accent text.
    m.COLOR_COMPUTED  = m.ASOFT
    # "Conflict" field: same soft-tint idea, built from ERROR since no ESOFT
    # role exists in the base theme.
    m.COLOR_CONFLICT  = _hex_to_rgba(m.ERROR, 0.16)
    # "Locked" field: muted panel tone, distinct from interactive states.
    m.COLOR_LOCKED_BG = m.PANEL2
    m.COLOR_LOCKED_FG = m.FG_LBL
    m.COLOR_LOCK_ON   = m.ACCENT
    m.COLOR_LOCK_OFF  = m.SURFACE2

    _rebuild_stylesheets(m)


def _rebuild_stylesheets(m) -> None:
    BG=m.BG; MANTLE=m.MANTLE; CRUST=m.CRUST; PANEL=m.PANEL
    SURFACE2=m.SURFACE2; BORDER=m.BORDER
    FG=m.FG; FG_DIM=m.FG_DIM; FG_LBL=m.FG_LBL
    ACCENT=m.ACCENT; AINK=m.AINK; ERROR=m.ERROR

    m._ENTRY_SS = f"""
        QLineEdit {{
            background: {MANTLE}; border: 1px solid {BORDER};
            border-radius: 7px; color: {FG}; padding: 4px 8px;
            selection-background-color: {ACCENT}; selection-color: {AINK};
        }}
        QLineEdit:focus {{
            border-color: {ACCENT};
            border-left: 3px solid {ACCENT};
            background: {BG};
        }}
        QLineEdit[readOnly="true"] {{ color: {FG_DIM}; background: {PANEL}; }}
    """

    m._COMBO_SS = f"""
        QComboBox {{
            background: {MANTLE}; border: 1px solid {BORDER};
            border-radius: 7px; color: {FG}; padding: 3px 8px;
        }}
        QComboBox:focus {{ border-color: {ACCENT}; }}
        QComboBox::drop-down {{ border: none; width: 20px; }}
        QComboBox::down-arrow {{ width: 0; height: 0; }}
        QComboBox QAbstractItemView {{
            background: {PANEL}; color: {FG}; border: 1px solid {BORDER};
            border-radius: 6px; padding: 2px;
            selection-background-color: {ACCENT}; selection-color: {AINK};
            outline: none;
        }}
    """

    m._BTN_SS = f"""
        QPushButton {{
            background: {PANEL}; border: 1px solid {BORDER};
            border-radius: 7px; color: {ACCENT}; padding: 4px 10px;
            font-weight: 500;
        }}
        QPushButton:hover {{ background: {SURFACE2}; border-color: {ACCENT}; }}
        QPushButton:pressed {{ background: {BORDER}; }}
        QPushButton:disabled {{ color: {FG_DIM}; border-color: {BORDER}; background: {PANEL}; }}
    """

    m._CHK_SS = f"""
        QCheckBox {{ color: {FG}; spacing: 7px; }}
        QCheckBox::indicator {{
            width: 15px; height: 15px; border-radius: 4px;
            border: 1px solid {SURFACE2}; background: {MANTLE};
        }}
        QCheckBox::indicator:unchecked:hover {{ border-color: {ACCENT}; }}
        QCheckBox::indicator:checked {{
            background: {ACCENT}; border-color: {ACCENT}; image: none;
        }}
    """

    m._RB_SS = f"""
        QRadioButton {{ color: {FG}; spacing: 7px; }}
        QRadioButton::indicator {{
            width: 14px; height: 14px; border-radius: 7px;
            border: 1px solid {SURFACE2}; background: {MANTLE};
        }}
        QRadioButton::indicator:checked {{
            background: {ACCENT}; border-color: {ACCENT}; border-width: 3px;
        }}
    """

    m._TAB_SS = f"""
        QTabWidget::pane {{
            background: {PANEL}; border: 1px solid {BORDER};
            border-radius: 9px; top: -1px;
        }}
        QTabBar::tab {{
            background: {MANTLE}; color: {FG_LBL}; padding: 6px 16px;
            border: 1px solid {BORDER}; border-bottom: none; margin-right: 2px;
            border-top-left-radius: 7px; border-top-right-radius: 7px;
            font-weight: 500;
        }}
        QTabBar::tab:selected {{
            background: {PANEL}; color: {ACCENT};
            border-bottom-color: {PANEL};
        }}
        QTabBar::tab:hover:!selected {{ background: {SURFACE2}; color: {FG}; }}
        QTabBar::tab:disabled {{ background: {CRUST}; color: {FG_DIM}; }}
    """

    m._SCROLL_SS = f"""
        QScrollArea {{ border: none; background: transparent; }}
        QScrollBar:vertical {{
            background: {MANTLE}; width: 8px; margin: 0; border-radius: 4px;
        }}
        QScrollBar::handle:vertical {{
            background: {SURFACE2}; border-radius: 4px; min-height: 20px;
        }}
        QScrollBar::handle:vertical:hover {{ background: {ACCENT}; }}
        QScrollBar:horizontal {{
            background: {MANTLE}; height: 8px; margin: 0; border-radius: 4px;
        }}
        QScrollBar::handle:horizontal {{
            background: {SURFACE2}; border-radius: 4px; min-width: 20px;
        }}
        QScrollBar::add-line, QScrollBar::sub-line {{ background: none; border: none; }}
    """

    # Dialogs / message boxes / file dialogs. Applied at the QApplication
    # level so any QDialog subclass is themed without per-dialog styling —
    # see RanOptics core/themes.py for why this has to be re-applied whenever
    # the whole app stylesheet is replaced on a theme switch.
    m._DIALOG_SS = f"""
        QDialog {{ background-color: {BG}; color: {FG}; }}
        QDialog QLabel {{ color: {FG}; background: transparent; }}

        QMessageBox {{ background-color: {PANEL}; color: {FG}; }}
        QMessageBox QLabel {{ color: {FG}; background: transparent; }}
        QMessageBox QPushButton {{
            background: {SURFACE2}; color: {FG};
            border: 1px solid {BORDER}; border-radius: 6px;
            padding: 5px 16px; min-width: 72px;
        }}
        QMessageBox QPushButton:hover {{
            background: {PANEL}; border-color: {ACCENT}; color: {ACCENT};
        }}
        QMessageBox QPushButton:default {{ border-color: {ACCENT}; color: {ACCENT}; }}

        QFileDialog {{ background: {BG}; color: {FG}; }}
        QFileDialog QWidget {{ background: {BG}; color: {FG}; }}
        QFileDialog QListView, QFileDialog QTreeView {{
            background: {MANTLE}; color: {FG};
            border: 1px solid {BORDER}; border-radius: 4px;
        }}
        QFileDialog QListView::item:selected, QFileDialog QTreeView::item:selected {{
            background: {ACCENT}; color: {AINK};
        }}
        QFileDialog QLineEdit {{
            background: {MANTLE}; color: {FG};
            border: 1px solid {BORDER}; border-radius: 4px; padding: 4px;
        }}
        QFileDialog QPushButton {{
            background: {PANEL}; color: {FG};
            border: 1px solid {BORDER}; border-radius: 6px; padding: 4px 12px;
        }}
        QFileDialog QPushButton:hover {{ background: {SURFACE2}; }}
        QFileDialog QComboBox {{
            background: {MANTLE}; color: {FG};
            border: 1px solid {BORDER}; border-radius: 4px; padding: 4px;
        }}
        QFileDialog QComboBox QAbstractItemView {{ background: {PANEL}; color: {FG}; }}
        QFileDialog QLabel {{ color: {FG}; background: transparent; }}
        QFileDialog QHeaderView::section {{
            background: {PANEL}; color: {FG_DIM}; border: none; padding: 4px;
        }}
        QFileDialog QSplitter {{ background: {BG}; }}
        QFileDialog QSideBar, QFileDialog QSidebar {{ background: {MANTLE}; color: {FG}; }}
    """


def apply_theme(name: str | None = None, mode: str | None = None) -> None:
    """Load a palette, selected by theme name and light/dark mode.

    Either argument may be omitted to keep the current value. Unknown names
    fall back to the default instead of raising, since this value may come
    from a user-editable settings file and must never stop the app starting.
    """
    import sys
    m = sys.modules[__name__]
    if name in ("dark", "light"):        # legacy: apply_theme('dark')
        name, mode = None, name
    name = name or getattr(m, "_current_theme", DEFAULT_THEME)
    mode = mode or getattr(m, "_current_mode", "dark")
    if name not in THEMES:
        name = DEFAULT_THEME
    if mode not in ("dark", "light"):
        mode = "dark"
    m._current_theme = name
    m._current_mode  = mode
    _load(THEMES[name][mode])


# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_MAIN  = QFont("IBM Plex Sans"); FONT_MAIN.setPointSize(11)
FONT_BOLD  = QFont("IBM Plex Sans"); FONT_BOLD.setPointSize(11); FONT_BOLD.setBold(True)
FONT_SMALL = QFont("IBM Plex Sans"); FONT_SMALL.setPointSize(9)
FONT_MONO  = QFont("IBM Plex Mono"); FONT_MONO.setPointSize(10)
FONT_HDR   = QFont("IBM Plex Sans"); FONT_HDR.setPointSize(18); FONT_HDR.setBold(True)
FONT_SEC   = QFont("IBM Plex Sans"); FONT_SEC.setPointSize(11); FONT_SEC.setBold(True)

# CSS font stack for stylesheet font-family declarations (quoted, comma list).
FONT_STACK_MONO = '"IBM Plex Mono", "JetBrains Mono", "Fira Mono", "Consolas", monospace'
FONT_STACK_SANS = '"IBM Plex Sans", "Segoe UI", sans-serif'

# ── Load default theme ────────────────────────────────────────────────────────
apply_theme(DEFAULT_THEME, "dark")
