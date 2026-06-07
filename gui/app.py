"""
gui/app.py — RanBeam
=====================
QMainWindow — ties together particle selector, tabs, solver, and menus.
"""

from __future__ import annotations
import sys
import os

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
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPalette, QAction

from core.models import BeamState, PARTICLES
from core.physics import solve
from core.beam_io import save_state, load_state
from gui.tabs import (
    RelativisticTab, TransverseTab, LongitudinalTab,
    RingRFTab, RadiationTab, LuminosityTab,
)

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

from palette import (
    BG, PANEL, MANTLE, CRUST, BORDER, SURFACE2,
    ACCENT, ACCENT2, FG, FG_DIM, FG_LBL,
    SUCCESS, WARN, ERROR,
)

# ---------------------------------------------------------------------------
# Global stylesheet
# ---------------------------------------------------------------------------
APP_STYLE = f"""
QMainWindow {{
    background-color: {BG};
    color: {FG};
    font-family: "JetBrains Mono", "Fira Mono", "Consolas", monospace;
    font-size: 12px;
}}
QWidget {{
    color: {FG};
    font-family: "JetBrains Mono", "Fira Mono", "Consolas", monospace;
    font-size: 12px;
}}
QTabWidget::pane {{
    border: 1px solid {BORDER};
    background: {BG};
}}
QTabBar::tab {{
    background: {PANEL};
    color: {FG_LBL};
    border: 1px solid {BORDER};
    padding: 6px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
}}
QTabBar::tab:selected {{
    background: {ACCENT};
    color: {CRUST};
    font-weight: bold;
}}
QTabBar::tab:hover:!selected {{
    background: {SURFACE2};
    color: {ACCENT};
}}
QTabBar::tab:disabled {{
    background: {CRUST};
    color: {FG_DIM};
}}
QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 4px;
    margin-top: 16px;
    padding-top: 8px;
    background: {PANEL};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 8px;
    top: -2px;
    background: {ACCENT};
    color: {CRUST};
    font-size: 10px;
    font-weight: bold;
    letter-spacing: 1px;
    padding: 1px 8px;
    border-radius: 3px;
}}
QComboBox {{
    background: {MANTLE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 3px 8px;
    color: {FG};
}}
QComboBox:focus {{ border-color: {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{
    background: {PANEL};
    color: {FG};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT};
    selection-color: {CRUST};
    outline: none;
}}
QPushButton {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 4px 12px;
    color: {ACCENT};
    font-weight: 500;
}}
QPushButton:hover {{
    background: {SURFACE2};
    border-color: {ACCENT};
}}
QPushButton:pressed {{
    background: {BORDER};
}}
QPushButton:disabled {{
    color: {FG_DIM};
    border-color: {BORDER};
}}
QScrollBar:vertical {{
    background: {CRUST};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {SURFACE2};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{ background: {FG_LBL}; }}
QScrollBar:horizontal {{
    background: {CRUST};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {SURFACE2};
    border-radius: 4px;
    min-width: 20px;
}}
QScrollBar::add-line, QScrollBar::sub-line {{ background: none; border: none; }}
QStatusBar {{
    background: {CRUST};
    color: {FG_LBL};
    font-size: 11px;
}}
QMenuBar {{
    background: {CRUST};
    color: {FG_LBL};
    border-bottom: none;
}}
QMenuBar::item:selected {{
    background: {MANTLE};
    color: {ACCENT};
}}
QMenu {{
    background: {PANEL};
    border: 1px solid {BORDER};
    color: {FG};
}}
QMenu::item:selected {{
    background: {MANTLE};
    color: {ACCENT};
}}
QLineEdit {{
    background: {MANTLE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 2px 6px;
    color: {FG};
}}
QLineEdit:focus {{ border-color: {ACCENT}; border-left: 3px solid {ACCENT}; }}
QLabel {{ color: {FG}; background: transparent; }}
QCheckBox {{ color: {FG_LBL}; }}
QCheckBox::indicator {{
    width: 14px; height: 14px;
    border: 1px solid {BORDER}; border-radius: 3px;
    background: {MANTLE};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT2};
    border-color: {ACCENT};
}}
QScrollArea QWidget {{ background: transparent; color: {FG}; }}
"""


# ---------------------------------------------------------------------------
# Header banner
# ---------------------------------------------------------------------------
class _Header(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedHeight(90)
        self.setStyleSheet(f"background: {CRUST};")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 16, 8)

        # PNG logo
        logo_path = os.path.join(_HERE, "logo_gui.png")
        if os.path.exists(logo_path):
            from PySide6.QtGui import QPixmap
            pix = QPixmap(logo_path)
            logo_lbl = QLabel()
            logo_lbl.setPixmap(pix.scaled(380, 72, Qt.KeepAspectRatio,
                                          Qt.SmoothTransformation))
            logo_lbl.setStyleSheet("background: transparent;")
            layout.addWidget(logo_lbl)
        else:
            name_row = QWidget()
            name_row.setStyleSheet("background: transparent;")
            name_layout = QHBoxLayout(name_row)
            name_layout.setContentsMargins(0, 0, 0, 0)
            name_layout.setSpacing(0)
            ran_lbl = QLabel("Ran")
            ran_lbl.setStyleSheet(f"color: {FG}; font-size: 28px; font-weight: bold; font-family: 'JetBrains Mono', monospace; background: transparent;")
            beam_lbl = QLabel("Beam")
            beam_lbl.setStyleSheet(f"color: {ACCENT}; font-size: 28px; font-weight: bold; font-family: 'JetBrains Mono', monospace; background: transparent;")
            name_layout.addWidget(ran_lbl)
            name_layout.addWidget(beam_lbl)
            layout.addWidget(name_row)

        layout.addStretch()

        # Author / support
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)

        author_lbl = QLabel("Author: Randika Gamage (randika@jlab.org)")
        author_lbl.setStyleSheet(f"color: {FG_LBL}; font-size: 13px; background: transparent;")
        author_lbl.setAlignment(Qt.AlignRight)

        support_lbl = QLabel("Support: Good luck, I believe in you")
        support_lbl.setStyleSheet(f"color: {FG_DIM}; font-size: 12px; font-style: italic; background: transparent;")
        support_lbl.setAlignment(Qt.AlignRight)

        info_layout.addStretch()
        info_layout.addWidget(author_lbl)
        info_layout.addWidget(support_lbl)
        info_layout.addStretch()
        layout.addLayout(info_layout)


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
        self._custom_mass_label.setStyleSheet(f"color: {FG_LBL};")
        layout.addWidget(self._custom_mass_label)
        self.custom_mass = QLineEdit("938.272")
        self.custom_mass.setFixedWidth(110)
        layout.addWidget(self.custom_mass)

        self._custom_q_label = QLabel("Charge (e):")
        self._custom_q_label.setStyleSheet(f"color: {FG_LBL};")
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
        self.resize(900, 780)
        self._state    = BeamState()
        self._inhibit  = False
        self._build_ui()
        self._build_menus()
        self._connect_signals()
        self._update_state_from_particle()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(_Header())

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
        self._conflict_label.setStyleSheet(f"color: {ERROR}; font-size: 11px;")
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
        self._full_container.setStyleSheet(f"background: {BG};")
        self._full_grid = QGridLayout(self._full_container)
        self._full_grid.setContentsMargins(10, 10, 10, 10)
        self._full_grid.setSpacing(10)

        # Pre-build the frames (without widgets yet — added on toggle)
        self._full_frames = []
        positions = [(0,0),(0,1),(0,2),(1,0),(1,1),(1,2)]
        for i, (row, col) in enumerate(positions):
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame.setStyleSheet(
                f"QFrame {{ border: 1px solid {BORDER}; border-radius: 6px;"
                f" background: {PANEL}; }}"
            )
            fl = QVBoxLayout(frame)
            fl.setContentsMargins(0, 0, 0, 0)
            fl.setSpacing(0)

            title_bar = QLabel(TAB_NAMES[i])
            title_bar.setStyleSheet(
                f"QLabel {{ background: {ACCENT}; color: {CRUST}; font-weight: bold;"
                f" font-size: 11px; padding: 4px 10px; border-radius: 4px 4px 0 0;"
                f" border: none; }}"
            )
            fl.addWidget(title_bar)
            # Placeholder — tab widget added on toggle
            self._full_frames.append((frame, fl))
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
            for i, (tab, (frame, fl)) in enumerate(
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
            for i, (tab, (frame, fl)) in enumerate(
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
                self.resize(900, 780)
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

        self._solve_timer = QTimer()
        self._solve_timer.setSingleShot(True)
        self._solve_timer.setInterval(150)
        self._solve_timer.timeout.connect(self._do_solve)

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
        dlg.setStyleSheet(
            f"QDialog {{ background: {PANEL}; }}"
            f"QLabel {{ color: {FG}; font-size: 12px; }}"
            f"QPushButton {{ background: {MANTLE}; border: 1px solid {BORDER};"
            f" border-radius: 6px; padding: 6px 16px; color: {ACCENT}; }}"
            f"QPushButton:hover {{ background: {SURFACE2}; }}"
        )
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
        btn_cancel.setStyleSheet(
            f"QPushButton {{ background: {MANTLE}; border: 1px solid {BORDER};"
            f" border-radius: 6px; padding: 6px 16px; color: {FG_LBL}; }}"
        )
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
            "<b>RanBeam v1.0</b><br>"
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

    palette = QPalette()
    palette.setColor(QPalette.Window,          QColor("#0F2219"))
    palette.setColor(QPalette.WindowText,      QColor(FG))
    palette.setColor(QPalette.Base,            QColor(MANTLE))
    palette.setColor(QPalette.AlternateBase,   QColor(PANEL))
    palette.setColor(QPalette.Text,            QColor(FG))
    palette.setColor(QPalette.Button,          QColor(CRUST))
    palette.setColor(QPalette.ButtonText,      QColor(FG))
    palette.setColor(QPalette.Dark,            QColor(CRUST))
    palette.setColor(QPalette.Mid,             QColor(CRUST))
    palette.setColor(QPalette.Shadow,          QColor(CRUST))
    palette.setColor(QPalette.Highlight,       QColor(ACCENT))
    palette.setColor(QPalette.HighlightedText, QColor(CRUST))
    palette.setColor(QPalette.ToolTipBase,     QColor(PANEL))
    palette.setColor(QPalette.ToolTipText,     QColor(FG))
    app.setPalette(palette)
    app.setStyleSheet(APP_STYLE)

    logo_path = os.path.join(_HERE, "logo_gui.png")
    if not os.path.exists(logo_path):
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "logo", os.path.join(_HERE, "logo.py")
            )
            logo_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(logo_mod)
            logo_mod.make_logo(out_dir=_HERE)
        except Exception:
            pass

    win = RanBeamWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch()
