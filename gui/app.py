"""
gui/app.py — RanBeam
=====================
QMainWindow — ties together particle selector, tabs, solver, and menus.
"""

from __future__ import annotations
import sys
import os
import json
from pathlib import Path

# Ensure project root is on sys.path when run from any directory
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QPushButton, QTabWidget, QStatusBar,
    QFileDialog, QMessageBox, QDoubleSpinBox, QFrame, QSizePolicy,
    QLineEdit, QGridLayout, QStackedWidget, QScrollArea,
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor, QPalette, QAction, QPixmap

from core.models import BeamState, PARTICLES
from core.physics import solve
from core.beam_io import save_state, load_state
from gui.tabs import (
    RelativisticTab, TransverseTab, LongitudinalTab,
    RingRFTab, RadiationTab, LuminosityTab,
)
import palette as _pal

RANBEAM_VERSION = "2.0.0"

# ---------------------------------------------------------------------------
# Machine type definitions
# ---------------------------------------------------------------------------
MACHINE_TYPES = {
    "Linac / Single-pass":       "linac",
    "Circular — Protons / Ions": "circular_proton",
    "Circular — Electrons":      "circular_electron",
    "Collider":                  "collider",
}

TAB_VISIBILITY = {
    "linac":              [True,  True,  True,  False, False, False],
    "circular_proton":    [True,  True,  True,  True,  False, False],
    "circular_electron":  [True,  True,  True,  True,  True,  False],
    "collider":           [True,  True,  True,  True,  True,  True ],
}

TAB_NAMES = [
    "Relativistic",
    "Transverse",
    "Longitudinal",
    "Ring / RF",
    "Radiation",
    "Luminosity",
]

# ---------------------------------------------------------------------------
# Settings persistence — remembers the chosen theme/mode across runs
# ---------------------------------------------------------------------------
_SETTINGS_FILE = Path.home() / ".ranbeam_settings.json"


def _read_settings() -> dict:
    try:
        data = json.loads(_SETTINGS_FILE.read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_settings() -> None:
    data = {
        "app_theme": _pal._current_theme,
        "app_mode":  _pal._current_mode,
    }
    try:
        _SETTINGS_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass   # never block the GUI on a settings write


# ---------------------------------------------------------------------------
# Global stylesheet — rebuilt fresh from the live palette on every theme
# switch (see RanBeamWindow._switch_theme). Never bind these colours to
# local names at import time — always read _pal.X at call time.
# ---------------------------------------------------------------------------
def _build_app_style() -> str:
    p = _pal
    return f"""
QMainWindow {{
    background-color: {p.BG};
    color: {p.FG};
    font-family: {p.FONT_STACK_MONO};
    font-size: 12px;
}}
QWidget {{
    color: {p.FG};
    font-family: {p.FONT_STACK_MONO};
    font-size: 12px;
}}
{p._TAB_SS}
QGroupBox {{
    border: 1px solid {p.BORDER};
    border-radius: 6px;
    margin-top: 16px;
    padding-top: 8px;
    background: {p.PANEL};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    top: -2px;
    background: {p.ACCENT2};
    color: {p.AINK};
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
    padding: 1px 8px;
    border-radius: 3px;
}}
{p._COMBO_SS}
{p._BTN_SS}
{p._SCROLL_SS}
QScrollBar:horizontal {{
    background: {p.MANTLE}; height: 8px; margin: 0; border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {p.SURFACE2}; border-radius: 4px; min-width: 20px;
}}
QStatusBar {{
    background: {p.MANTLE};
    color: {p.FG_DIM};
    border-top: 1px solid {p.BORDER};
    font-size: 11px;
}}
QMenuBar {{
    background: {p.CRUST};
    color: {p.FG_LBL};
    border-bottom: 1px solid {p.BORDER};
}}
QMenuBar::item {{ padding: 4px 10px; border-radius: 4px; }}
QMenuBar::item:selected {{
    background: {p.SURFACE2};
    color: {p.ACCENT};
}}
QMenu {{
    background: {p.PANEL};
    border: 1px solid {p.BORDER};
    border-radius: 8px;
    color: {p.FG};
    padding: 4px;
}}
QMenu::item {{ padding: 5px 20px; border-radius: 4px; }}
QMenu::item:selected {{
    background: {p.SURFACE2};
    color: {p.ACCENT};
}}
{p._ENTRY_SS}
QLabel {{ color: {p.FG}; background: transparent; }}
{p._CHK_SS}
QScrollArea QWidget {{ background: transparent; color: {p.FG}; }}
""" + p._DIALOG_SS


def _build_qpalette() -> QPalette:
    p = _pal
    pal = QPalette()
    pal.setColor(QPalette.Window,          QColor(p.BG))
    pal.setColor(QPalette.WindowText,      QColor(p.FG))
    pal.setColor(QPalette.Base,            QColor(p.MANTLE))
    pal.setColor(QPalette.AlternateBase,   QColor(p.PANEL))
    pal.setColor(QPalette.Text,            QColor(p.FG))
    pal.setColor(QPalette.Button,          QColor(p.CRUST))
    pal.setColor(QPalette.ButtonText,      QColor(p.FG))
    pal.setColor(QPalette.Dark,            QColor(p.CRUST))
    pal.setColor(QPalette.Mid,             QColor(p.CRUST))
    pal.setColor(QPalette.Shadow,          QColor(p.CRUST))
    pal.setColor(QPalette.Highlight,       QColor(p.ACCENT))
    pal.setColor(QPalette.HighlightedText, QColor(p.AINK))
    pal.setColor(QPalette.ToolTipBase,     QColor(p.PANEL))
    pal.setColor(QPalette.ToolTipText,     QColor(p.FG))
    return pal


# ---------------------------------------------------------------------------
# Header banner — logo, author/support, and the theme mode/palette switcher
# ---------------------------------------------------------------------------
class _Header(QWidget):
    mode_changed  = Signal(str)   # "light" | "dark"
    theme_changed = Signal(str)   # theme name, e.g. "Petrol"

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedHeight(96)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 16, 8)

        logo_col = QWidget()
        logo_col.setStyleSheet("background: transparent;")
        lc = QVBoxLayout(logo_col)
        lc.setContentsMargins(0, 0, 0, 0)
        lc.setSpacing(2)

        self._logo_lbl = QLabel()
        self._logo_lbl.setStyleSheet("background: transparent;")
        lc.addWidget(self._logo_lbl)
        self._reload_logo()

        self._version_lbl = QLabel(f"v{RANBEAM_VERSION}")
        self._version_lbl.setAlignment(Qt.AlignCenter)
        ver_row = QWidget()
        ver_row.setStyleSheet("background: transparent;")
        vr = QHBoxLayout(ver_row)
        vr.setContentsMargins(0, 0, 0, 0)
        vr.addWidget(self._version_lbl)
        vr.addStretch()
        lc.addWidget(ver_row)

        layout.addWidget(logo_col)
        layout.addStretch()

        # Author / support
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)

        self._author_lbl = QLabel("Author: Randika Gamage (randika@jlab.org)")
        self._author_lbl.setAlignment(Qt.AlignRight)

        self._support_lbl = QLabel("Support: Good luck, I believe in you")
        self._support_lbl.setAlignment(Qt.AlignRight)

        info_layout.addWidget(self._author_lbl)
        info_layout.addWidget(self._support_lbl)

        # Theme mode toggle + palette picker
        self._tog_widget = QWidget()
        tl = QHBoxLayout(self._tog_widget)
        tl.setContentsMargins(3, 3, 3, 3)
        tl.setSpacing(2)

        self._btn_light = QPushButton("☀ Light")
        self._btn_light.setFixedHeight(24)
        self._btn_light.setCheckable(True)
        self._btn_dark = QPushButton("☾ Dark")
        self._btn_dark.setFixedHeight(24)
        self._btn_dark.setCheckable(True)
        self._btn_light.clicked.connect(lambda: self.mode_changed.emit("light"))
        self._btn_dark.clicked.connect(lambda: self.mode_changed.emit("dark"))
        tl.addWidget(self._btn_light)
        tl.addWidget(self._btn_dark)

        self._theme_dd = QComboBox()
        self._theme_dd.setFixedHeight(24)
        self._theme_dd.addItems(list(_pal.THEMES.keys()))
        self._theme_dd.currentTextChanged.connect(self.theme_changed.emit)
        tl.addWidget(self._theme_dd)

        tog_row = QWidget()
        tr = QHBoxLayout(tog_row)
        tr.setContentsMargins(0, 0, 0, 0)
        tr.addStretch()
        tr.addWidget(self._tog_widget)

        info_layout.addWidget(tog_row)
        layout.addLayout(info_layout)

        self.refresh_theme()

    def _reload_logo(self) -> None:
        logo_path = os.path.join(_HERE, "logo_gui.png")
        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            self._logo_lbl.setPixmap(
                pix.scaled(340, 76, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
        else:
            self._logo_lbl.setText("RanBeam")

    def refresh_theme(self) -> None:
        """Re-apply header-specific inline styles and the switcher's own
        checked/unchecked state after a theme switch (also called once at
        construction)."""
        p = _pal
        self.setStyleSheet(f"background: {p.PANEL}; border-bottom: 1px solid {p.BORDER};")
        self._author_lbl.setStyleSheet(f"color: {p.FG_DIM}; font-size: 13px; background: transparent;")
        self._support_lbl.setStyleSheet(f"color: {p.FG_DIM}; font-size: 12px; font-style: italic; background: transparent;")
        self._version_lbl.setStyleSheet(
            f"color: {p.FG_DIM}; background: {p.MANTLE}; border: 1px solid {p.BORDER};"
            f" border-radius: 4px; padding: 1px 6px; font-size: 10px;"
            f" font-family: {p.FONT_STACK_MONO};"
        )
        self._tog_widget.setStyleSheet(
            f"background: {p.MANTLE}; border: 1px solid {p.BORDER}; border-radius: 8px;"
        )
        toggle_ss = f"""
            QPushButton {{
                background: transparent; border: 1px solid transparent;
                border-radius: 6px; color: {p.FG_DIM}; padding: 3px 10px; font-size: 11px;
            }}
            QPushButton:checked {{
                background: {p.ASOFT}; border-color: {p.ACCENT}; color: {p.ACCENT};
            }}
            QPushButton:hover:!checked {{ background: {p.SURFACE2}; color: {p.FG}; }}
        """
        self._btn_light.setStyleSheet(toggle_ss)
        self._btn_dark.setStyleSheet(toggle_ss)
        self._btn_light.blockSignals(True)
        self._btn_dark.blockSignals(True)
        self._btn_light.setChecked(p._current_mode == "light")
        self._btn_dark.setChecked(p._current_mode == "dark")
        self._btn_light.blockSignals(False)
        self._btn_dark.blockSignals(False)

        self._theme_dd.setStyleSheet(f"""
            QComboBox {{
                background: transparent; border: 1px solid transparent;
                border-radius: 6px; color: {p.FG_DIM}; padding: 3px 8px; font-size: 11px;
            }}
            QComboBox:hover {{ background: {p.SURFACE2}; color: {p.FG}; }}
            QComboBox::drop-down {{ border: none; width: 14px; }}
            QComboBox::down-arrow {{ width: 0; height: 0; }}
            QComboBox QAbstractItemView {{
                background: {p.PANEL}; color: {p.FG};
                border: 1px solid {p.BORDER}; border-radius: 6px; padding: 2px;
                selection-background-color: {p.ACCENT}; selection-color: {p.AINK};
                outline: none;
            }}
        """)
        self._theme_dd.blockSignals(True)
        self._theme_dd.setCurrentText(p._current_theme)
        self._theme_dd.blockSignals(False)

        self._reload_logo()


# ---------------------------------------------------------------------------
# Particle selector row
# ---------------------------------------------------------------------------
class _ParticleSelector(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.setSpacing(12)

        layout.addWidget(QLabel("Particle:"))
        self.particle_combo = QComboBox()
        self.particle_combo.addItems(list(PARTICLES.keys()))
        self.particle_combo.setCurrentText("Proton")
        self.particle_combo.setFixedWidth(180)
        layout.addWidget(self.particle_combo)

        self._custom_mass_label = QLabel("Mass (MeV/c²):")
        layout.addWidget(self._custom_mass_label)
        self.custom_mass = QLineEdit("938.272")
        self.custom_mass.setFixedWidth(110)
        layout.addWidget(self.custom_mass)

        self._custom_q_label = QLabel("Charge (e):")
        layout.addWidget(self._custom_q_label)
        self.custom_charge = QLineEdit("1")
        self.custom_charge.setFixedWidth(70)
        layout.addWidget(self.custom_charge)

        layout.addSpacing(24)
        layout.addWidget(QLabel("Machine:"))
        self.machine_combo = QComboBox()
        self.machine_combo.addItems(list(MACHINE_TYPES.keys()))
        self.machine_combo.setFixedWidth(220)
        layout.addWidget(self.machine_combo)

        layout.addStretch()

        self._toggle_custom(self.particle_combo.currentText())
        self.particle_combo.currentTextChanged.connect(self._toggle_custom)
        self.refresh_theme()

    def refresh_theme(self) -> None:
        c = f"color: {_pal.FG_LBL};"
        self._custom_mass_label.setStyleSheet(c)
        self._custom_q_label.setStyleSheet(c)

    def _toggle_custom(self, name: str) -> None:
        is_custom = (name == "Custom")
        for w in [self._custom_mass_label, self.custom_mass,
                  self._custom_q_label, self.custom_charge]:
            w.setVisible(is_custom)

    def get_particle_params(self) -> tuple[str, float, float]:
        name = self.particle_combo.currentText()
        if name == "Custom":
            try:
                mass = float(self.custom_mass.text())
            except ValueError:
                mass = 938.272
            try:
                charge = float(self.custom_charge.text())
            except ValueError:
                charge = 1.0
        else:
            p = PARTICLES[name]
            mass   = p.mass_MeV
            charge = p.charge
        return name, mass, charge

    def get_machine_type(self) -> str:
        return MACHINE_TYPES[self.machine_combo.currentText()]


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
class RanBeamWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RanBeam — Beam Parameter Calculator")
        self.resize(900, 820)
        self._state    = BeamState()
        self._inhibit  = False
        self._build_ui()
        self._build_menus()
        self._connect_signals()
        self._update_state_from_particle()
        self._restyle()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._header = _Header()
        root.addWidget(self._header)

        self._selector = _ParticleSelector()
        root.addWidget(self._selector)

        # Toolbar
        toolbar = QWidget()
        toolbar.setStyleSheet("background: transparent;")
        tl = QHBoxLayout(toolbar)
        tl.setContentsMargins(12, 4, 12, 4)
        tl.setSpacing(8)

        self._btn_clear   = QPushButton("✕  Clear All")
        self._btn_save    = QPushButton("💾  Save State")
        self._btn_load    = QPushButton("📂  Load State")
        self._btn_load_b2 = QPushButton("📂  Load as Beam 2")

        for btn in [self._btn_clear, self._btn_save,
                    self._btn_load, self._btn_load_b2]:
            btn.setFixedHeight(28)
            tl.addWidget(btn)

        tl.addStretch()

        # View toggle button
        self._btn_toggle_view = QPushButton("⊞  Full View")
        self._btn_toggle_view.setFixedHeight(28)
        self._btn_toggle_view.setCheckable(True)
        self._btn_toggle_view.setToolTip("Toggle between tabbed and full-page view")
        tl.addWidget(self._btn_toggle_view)

        root.addWidget(toolbar)

        # Create tab widgets once — shared between both views
        self._tab_widgets = [
            RelativisticTab(),
            TransverseTab(),
            LongitudinalTab(),
            RingRFTab(),
            RadiationTab(),
            LuminosityTab(),
        ]

        # --- Tabbed view ---
        self._tabs = QTabWidget()
        for name, tab in zip(TAB_NAMES, self._tab_widgets):
            self._tabs.addTab(tab, name)

        # --- Full view ---
        self._full_view = self._build_full_view()

        # Stacked widget to switch between the two
        self._view_stack = QStackedWidget()
        self._view_stack.addWidget(self._tabs)       # index 0 — tabbed
        self._view_stack.addWidget(self._full_view)  # index 1 — full

        root.addWidget(self._view_stack)

        # Status bar
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Ready.")

        self._conflict_label = QLabel("")
        self._status.addPermanentWidget(self._conflict_label)

    def _build_full_view(self) -> QScrollArea:
        """
        Build the full-page grid view (3 cols x 2 rows).
        Does NOT reparent the tab widgets — they stay in self._tabs.
        On toggle, we reparent them between the two containers.
        """
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self._full_container = QWidget()
        self._full_grid = QGridLayout(self._full_container)
        self._full_grid.setContentsMargins(10, 10, 10, 10)
        self._full_grid.setSpacing(10)

        # Pre-build the frames (without widgets yet — added on toggle)
        self._full_frames = []
        positions = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)]
        for i, (row, col) in enumerate(positions):
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            fl = QVBoxLayout(frame)
            fl.setContentsMargins(0, 0, 0, 0)
            fl.setSpacing(0)

            title_bar = QLabel(TAB_NAMES[i])
            fl.addWidget(title_bar)
            # Placeholder — tab widget added on toggle
            self._full_frames.append((frame, fl, title_bar))
            self._full_grid.addWidget(frame, row, col)

        for col in range(3):
            self._full_grid.setColumnStretch(col, 1)
        for row in range(2):
            self._full_grid.setRowStretch(row, 1)

        scroll.setWidget(self._full_container)
        return scroll

    def _toggle_view(self, checked: bool) -> None:
        """Switch between tabbed and full view, reparenting tab widgets."""
        if checked:
            # Save current size before expanding
            self._saved_size = self.size()
            # Move tab widgets from QTabWidget into full view frames
            for i, (tab, (frame, fl, title_bar)) in enumerate(
                    zip(self._tab_widgets, self._full_frames)):
                self._tabs.removeTab(0)
                fl.addWidget(tab)
                tab.show()

            self._view_stack.setCurrentIndex(1)
            self._btn_toggle_view.setText("☰  Tab View")
            # Only resize if not already maximized/large
            if self.width() < 1200:
                self.resize(1400, 900)
        else:
            # Move tab widgets back into QTabWidget
            for i, (tab, (frame, fl, title_bar)) in enumerate(
                    zip(self._tab_widgets, self._full_frames)):
                fl.removeWidget(tab)
                self._tabs.addTab(tab, TAB_NAMES[i])
                tab.show()

            self._view_stack.setCurrentIndex(0)
            self._btn_toggle_view.setText("⊞  Full View")
            # Restore saved size if available, otherwise default
            if hasattr(self, '_saved_size'):
                self.resize(self._saved_size)
            else:
                self.resize(900, 820)
            # Re-apply machine visibility
            self._on_machine_changed("")

    def _build_menus(self) -> None:
        mb = self.menuBar()

        file_menu = mb.addMenu("File")
        act_save = QAction("Save State…", self)
        act_save.setShortcut("Ctrl+S")
        act_save.triggered.connect(self._on_save)
        file_menu.addAction(act_save)

        act_load = QAction("Load State…", self)
        act_load.setShortcut("Ctrl+O")
        act_load.triggered.connect(self._on_load)
        file_menu.addAction(act_load)

        file_menu.addSeparator()
        act_quit = QAction("Quit", self)
        act_quit.setShortcut("Ctrl+Q")
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

        edit_menu = mb.addMenu("Edit")
        act_clear = QAction("Clear All Fields", self)
        act_clear.setShortcut("Ctrl+Del")
        act_clear.triggered.connect(self._on_clear)
        edit_menu.addAction(act_clear)

        help_menu = mb.addMenu("Help")
        act_about = QAction("About RanBeam", self)
        act_about.triggered.connect(self._on_about)
        help_menu.addAction(act_about)

    def _connect_signals(self) -> None:
        self._selector.particle_combo.currentTextChanged.connect(
            lambda _: self._update_state_from_particle()
        )
        self._selector.custom_mass.textEdited.connect(
            lambda _: self._update_state_from_particle()
        )
        self._selector.custom_charge.textEdited.connect(
            lambda _: self._update_state_from_particle()
        )
        self._selector.machine_combo.currentTextChanged.connect(
            self._on_machine_changed
        )

        for tab in self._tab_widgets:
            tab.any_changed.connect(self._schedule_solve)

        self._tab_widgets[2].unit_changed.connect(self._on_eps_L_unit_changed)
        self._tab_widgets[5].hourglass_changed.connect(self._on_hourglass_changed)

        self._btn_toggle_view.clicked.connect(self._toggle_view)
        self._btn_clear.clicked.connect(self._on_clear)
        self._btn_save.clicked.connect(self._on_save)
        self._btn_load.clicked.connect(self._on_load)
        self._btn_load_b2.clicked.connect(self._on_load_beam2)

        self._header.mode_changed.connect(lambda m: self._switch_theme(mode=m))
        self._header.theme_changed.connect(lambda t: self._switch_theme(theme=t))

        self._solve_timer = QTimer()
        self._solve_timer.setSingleShot(True)
        self._solve_timer.setInterval(150)
        self._solve_timer.timeout.connect(self._do_solve)

    # -----------------------------------------------------------------------
    # Theming
    # -----------------------------------------------------------------------

    def _switch_theme(self, mode: str | None = None, theme: str | None = None) -> None:
        """Apply a new theme/mode, persist it, and restyle every widget."""
        _pal.apply_theme(theme, mode)
        _save_settings()
        app = QApplication.instance()
        app.setPalette(_build_qpalette())
        app.setStyleSheet(_build_app_style())
        try:
            import logo
            logo.make_logo(out_dir=_HERE, gui_only=True)
        except Exception:
            pass
        self._restyle()

    def _restyle(self) -> None:
        """Re-apply every inline (per-widget) stylesheet using live theme
        values. Widgets styled only via the global QApplication stylesheet
        (QGroupBox, QPushButton, QComboBox, …) update automatically when
        that stylesheet is replaced and don't need to be touched here."""
        self._header.refresh_theme()
        self._selector.refresh_theme()
        for tab in self._tab_widgets:
            tab.refresh_theme()

        p = _pal
        self._conflict_label.setStyleSheet(f"color: {p.ERROR}; font-size: 11px;")

        if hasattr(self, "_full_container"):
            self._full_container.setStyleSheet(f"background: {p.BG};")
        for frame, fl, title_bar in getattr(self, "_full_frames", []):
            frame.setStyleSheet(
                f"QFrame {{ border: 1px solid {p.BORDER}; border-radius: 6px;"
                f" background: {p.PANEL}; }}"
            )
            title_bar.setStyleSheet(
                f"QLabel {{ background: {p.ACCENT2}; color: {p.AINK}; font-weight: bold;"
                f" font-size: 11px; padding: 4px 10px; border-radius: 4px 4px 0 0;"
                f" border: none; }}"
            )

    def _schedule_solve(self) -> None:
        if not self._inhibit:
            self._solve_timer.start()

    def _do_solve(self) -> None:
        if self._inhibit:
            return
        self._inhibit = True
        try:
            self._collect_inputs()
            new_state, conflicts = solve(self._state)
            self._state = new_state
            self._push_to_ui(conflicts)
        except Exception as e:
            self._status.showMessage(f"Solver error: {e}")
        finally:
            self._inhibit = False

    def _collect_inputs(self) -> None:
        name, mass, charge = self._selector.get_particle_params()
        self._state.particle_name = name
        self._state.mass_MeV      = mass
        self._state.charge        = charge
        self._state.machine_type  = self._selector.get_machine_type()

        locked = set()
        for tab in self._tab_widgets:
            locked |= tab.get_locked()
        self._state.locked = locked

        # Collect user-typed values from _user_fields tracking
        user_vals: dict[str, float | None] = {}
        for tab in self._tab_widgets:
            user_vals.update(tab.get_user_values())

        # Also sweep all fields directly — catches values typed after reparenting
        # Only add to user_vals if the field widget is NOT in computed state
        # This prevents computed fields from being locked in as user inputs
        for tab in self._tab_widgets:
            for field_name, field_widget in tab._fields.items():
                if field_name in locked:
                    continue
                # Only read from widget if already tracked as user-typed
                # OR if the field has a non-computed value (user typed it)
                if field_name in tab._user_fields:
                    val = field_widget.get_value()
                    if val is not None:
                        user_vals[field_name] = val

        for tab in self._tab_widgets:
            for field_name in tab._fields:
                if field_name in locked:
                    continue
                if field_name in user_vals:
                    setattr(self._state, field_name, user_vals[field_name])
                else:
                    setattr(self._state, field_name, None)

        # If circumference is entered but machine is linac, prompt to switch
        if (user_vals.get("circumference") is not None
                and self._state.machine_type == "linac"):
            self._prompt_circular_switch()

    def _prompt_circular_switch(self) -> None:
        """Ask user if they want to switch to a circular machine type."""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        dlg = QDialog(self)
        dlg.setWindowTitle("Switch Machine Type?")
        dlg.setFixedSize(520, 120)
        # Global QApplication stylesheet (_pal._DIALOG_SS) themes QDialog/
        # QLabel/QPushButton automatically — no per-dialog styling needed.
        layout = QVBoxLayout(dlg)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)

        lbl = QLabel("Circumference entered — this looks like a circular machine.\nSwitch machine type?")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        btn_row = QHBoxLayout()
        btn_proton   = QPushButton("Circular — Protons/Ions")
        btn_electron = QPushButton("Circular — Electrons")
        btn_collider = QPushButton("Collider")
        btn_cancel   = QPushButton("Keep Linac")
        for btn in [btn_proton, btn_electron, btn_collider, btn_cancel]:
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

        def switch(mtype):
            rev_machine = {v: k for k, v in MACHINE_TYPES.items()}
            self._selector.machine_combo.setCurrentText(rev_machine[mtype])
            dlg.accept()

        btn_proton.clicked.connect(lambda: switch("circular_proton"))
        btn_electron.clicked.connect(lambda: switch("circular_electron"))
        btn_collider.clicked.connect(lambda: switch("collider"))
        btn_cancel.clicked.connect(dlg.reject)

        dlg.exec()

    def _push_to_ui(self, conflicts: list[str]) -> None:
        for tab in self._tab_widgets:
            tab.push_state(self._state, conflicts)

        if conflicts:
            self._conflict_label.setText(f"⚠  {len(conflicts)} conflict(s)")
            self._status.showMessage(conflicts[0])
        else:
            self._conflict_label.setText("")
            self._status.showMessage("Solved.")

    def _update_state_from_particle(self) -> None:
        name, mass, charge = self._selector.get_particle_params()
        self._state.particle_name = name
        self._state.mass_MeV      = mass
        self._state.charge        = charge
        self._state.E_rest        = mass
        self._do_solve()

    def _on_machine_changed(self, _text: str) -> None:
        machine = self._selector.get_machine_type()
        self._state.machine_type = machine
        visibility = TAB_VISIBILITY[machine]
        for i, (tab, visible) in enumerate(zip(self._tab_widgets, visibility)):
            self._tabs.setTabEnabled(i, visible)
            tab.setEnabled(visible)
        self._do_solve()

    def _on_eps_L_unit_changed(self, unit: str) -> None:
        self._state.eps_L_unit = unit
        self._do_solve()

    def _on_hourglass_changed(self, enabled: bool) -> None:
        self._state.hourglass = enabled
        self._do_solve()

    def _on_clear(self) -> None:
        name   = self._state.particle_name
        mass   = self._state.mass_MeV
        charge = self._state.charge
        mtype  = self._state.machine_type
        self._state = BeamState(
            particle_name=name, mass_MeV=mass, charge=charge, machine_type=mtype
        )
        self._inhibit = True
        try:
            for tab in self._tab_widgets:
                tab.clear_all()
        finally:
            self._inhibit = False
        self._do_solve()
        self._status.showMessage("Cleared.")

    def _on_save(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Beam State", "", "RanBeam JSON (*.json)"
        )
        if not path:
            return
        if not path.endswith(".json"):
            path += ".json"
        self._collect_inputs()
        try:
            save_state(self._state, path)
            self._status.showMessage(f"Saved → {path}")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))

    def _on_load(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Beam State", "", "RanBeam JSON (*.json)"
        )
        if not path:
            return
        try:
            loaded = load_state(path)
            self._state = loaded
            self._selector.particle_combo.blockSignals(True)
            self._selector.machine_combo.blockSignals(True)
            if loaded.particle_name in PARTICLES:
                self._selector.particle_combo.setCurrentText(loaded.particle_name)
            rev_machine = {v: k for k, v in MACHINE_TYPES.items()}
            if loaded.machine_type in rev_machine:
                self._selector.machine_combo.setCurrentText(rev_machine[loaded.machine_type])
            self._selector.particle_combo.blockSignals(False)
            self._selector.machine_combo.blockSignals(False)
            self._on_machine_changed("")
            self._push_to_ui([])
            self._status.showMessage(f"Loaded ← {path}")
        except Exception as e:
            QMessageBox.critical(self, "Load Error", str(e))

    def _on_load_beam2(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Beam 2 State", "", "RanBeam JSON (*.json)"
        )
        if not path:
            return
        try:
            loaded = load_state(path)
            self._state.N2          = loaded.N1 or loaded.N2
            self._state.eps_geo_x2  = loaded.eps_geo_x
            self._state.eps_geo_y2  = loaded.eps_geo_y
            self._state.sigma_z_m2  = loaded.sigma_z_m
            self._do_solve()
            self._status.showMessage(f"Beam 2 loaded ← {path}")
        except Exception as e:
            QMessageBox.critical(self, "Load Beam 2 Error", str(e))

    def _on_about(self) -> None:
        QMessageBox.about(
            self,
            "About RanBeam",
            f"<b>RanBeam v{RANBEAM_VERSION}</b><br>"
            "Accelerator Beam Parameter Calculator<br><br>"
            "Auto-propagating dependency graph solver.<br>"
            "Enter any known quantities — everything derivable is computed automatically.<br>"
            "Conflicting inputs are flagged, not silently overridden.<br><br>"
            "<i>Randy Afkarian / JLab–BNL</i>",
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def launch() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyle("Fusion")

    settings = _read_settings()
    _pal.apply_theme(settings.get("app_theme"), settings.get("app_mode"))

    app.setPalette(_build_qpalette())
    app.setStyleSheet(_build_app_style())

    # Regenerate the GUI logo variant so it always matches the theme/mode
    # just loaded from settings — a cached PNG from a previous theme would
    # otherwise clash with the freshly-applied palette.
    docs_logo_path = os.path.join(_HERE, "logo_docs.png")
    try:
        import logo
        logo.make_logo(out_dir=_HERE, gui_only=os.path.exists(docs_logo_path))
    except Exception:
        pass

    win = RanBeamWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch()
