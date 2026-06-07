"""
gui/tabs.py — RanBeam
======================
One QWidget subclass per tab.  Each tab:
  - owns a dict of LockableField widgets keyed by field_name
  - exposes get_values() → dict[str, float | None]
  - exposes push_state(BeamState, conflicts) to update displayed values
  - re-emits a any_changed signal when any field is edited
"""

from __future__ import annotations
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QComboBox, QCheckBox, QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Signal, Qt

from gui.fields import LockableField
from core.models import UNITS, LABELS, BeamState


# ---------------------------------------------------------------------------
# Helper: build a section group with fields
# ---------------------------------------------------------------------------
def _make_group(title: str, field_names: list[str]) -> tuple[QGroupBox, dict[str, LockableField]]:
    box    = QGroupBox(title)
    layout = QVBoxLayout(box)
    layout.setSpacing(4)
    layout.setContentsMargins(8, 12, 8, 8)
    fields: dict[str, LockableField] = {}
    for name in field_names:
        lbl  = LABELS.get(name, name)
        unit = UNITS.get(name, "")
        f    = LockableField(name, lbl, unit)
        layout.addWidget(f)
        fields[name] = f
    return box, fields


# ---------------------------------------------------------------------------
# Base class — common logic shared by all tabs
# ---------------------------------------------------------------------------
class _BaseTab(QWidget):
    any_changed = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._fields:      dict[str, LockableField] = {}
        self._user_fields: set[str] = set()

        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QFrame.NoFrame)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll_area)
        self._inner = QWidget()
        self._inner_layout = QVBoxLayout(self._inner)
        self._inner_layout.setSpacing(10)
        self._inner_layout.setContentsMargins(10, 10, 10, 10)
        self._scroll_area.setWidget(self._inner)

    def _register_group(self, box: QGroupBox, fields: dict[str, LockableField]) -> None:
        self._inner_layout.addWidget(box)
        for name, f in fields.items():
            self._fields[name] = f
            f.value_changed.connect(lambda n, t, _n=name: self._on_field_edited(_n, t))
            f.lock_toggled.connect(lambda _n, _l: self.any_changed.emit())

    def _on_field_edited(self, name: str, text: str) -> None:
        if text.strip():
            self._user_fields.add(name)
        else:
            self._user_fields.discard(name)
        self.any_changed.emit()

    def get_user_values(self) -> dict[str, float | None]:
        """Only fields the user has explicitly typed into."""
        return {
            name: self._fields[name].get_value()
            for name in self._user_fields
            if name in self._fields
        }

    def get_values(self) -> dict[str, float | None]:
        return {name: f.get_value() for name, f in self._fields.items()}

    def get_locked(self) -> set[str]:
        return {name for name, f in self._fields.items() if f.is_locked}

    def push_state(self, state: BeamState, conflicts: list[str]) -> None:
        conflict_fields = _parse_conflict_fields(conflicts)
        for name, f in self._fields.items():
            if name in self._user_fields or f.is_locked:
                f.set_conflict(name in conflict_fields)
                continue
            val = getattr(state, name, None)
            f.set_value(val, computed=(val is not None))
            f.set_conflict(name in conflict_fields)

    def clear_all(self) -> None:
        self._user_fields.clear()
        for f in self._fields.values():
            f.clear()


# ---------------------------------------------------------------------------
# Tab 1 — Relativistic
# ---------------------------------------------------------------------------
class RelativisticTab(_BaseTab):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        box, fields = _make_group("Relativistic Parameters", [
            "KE", "E_total", "E_rest",
            "momentum", "Brho",
            "beta", "gamma", "beta_gamma", "velocity",
        ])
        self._register_group(box, fields)
        self._inner_layout.addStretch()


# ---------------------------------------------------------------------------
# Tab 2 — Transverse
# ---------------------------------------------------------------------------
class TransverseTab(_BaseTab):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # --- x plane ---
        box_x, fields_x = _make_group("Horizontal (x) Plane", [
            "eps_geo_x", "eps_n_x",
        ])
        self._register_group(box_x, fields_x)

        box_xp, fields_xp = _make_group("Horizontal — Point of Interest (user-supplied Twiss)", [
            "beta_star_x", "alpha_star_x", "eta_x",
            "sigma_x", "sigma_prime_x", "sigma_x_total",
        ])
        self._register_group(box_xp, fields_xp)

        # --- y plane ---
        box_y, fields_y = _make_group("Vertical (y) Plane", [
            "eps_geo_y", "eps_n_y",
        ])
        self._register_group(box_y, fields_y)

        box_yp, fields_yp = _make_group("Vertical — Point of Interest (user-supplied Twiss)", [
            "beta_star_y", "alpha_star_y", "eta_y",
            "sigma_y", "sigma_prime_y", "sigma_y_total",
        ])
        self._register_group(box_yp, fields_yp)

        self._inner_layout.addStretch()


# ---------------------------------------------------------------------------
# Tab 3 — Longitudinal
# ---------------------------------------------------------------------------
class LongitudinalTab(_BaseTab):
    # Signal carrying the selected unit string ("eVs" or "eVm")
    unit_changed = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Unit selector for longitudinal emittance
        unit_row = QWidget()
        unit_layout = QHBoxLayout(unit_row)
        unit_layout.setContentsMargins(8, 4, 8, 0)
        unit_layout.addWidget(QLabel("Longitudinal emittance unit:"))
        self._eps_L_combo = QComboBox()
        self._eps_L_combo.addItems(["eV·s", "eV·m"])
        self._eps_L_combo.setFixedWidth(100)
        self._eps_L_combo.currentIndexChanged.connect(self._on_unit_changed)
        unit_layout.addWidget(self._eps_L_combo)
        unit_layout.addStretch()
        self._inner_layout.addWidget(unit_row)

        box, fields = _make_group("Longitudinal Parameters", [
            "delta_p",
            "eps_L_eVs", "eps_L_eVm",
            "sigma_z_m", "sigma_z_t",
        ])
        self._register_group(box, fields)
        self._inner_layout.addStretch()
        self._update_eps_visibility("eVs")

    def _on_unit_changed(self, idx: int) -> None:
        unit = "eVs" if idx == 0 else "eVm"
        self._update_eps_visibility(unit)
        self.unit_changed.emit(unit)

    def _update_eps_visibility(self, unit: str) -> None:
        show_eVs = (unit == "eVs")
        if "eps_L_eVs" in self._fields:
            self._fields["eps_L_eVs"].setVisible(show_eVs)
        if "eps_L_eVm" in self._fields:
            self._fields["eps_L_eVm"].setVisible(not show_eVs)

    def push_state(self, state: BeamState, conflicts: list[str]) -> None:
        super().push_state(state, conflicts)
        # Keep combo in sync with state
        idx = 0 if state.eps_L_unit == "eVs" else 1
        self._eps_L_combo.blockSignals(True)
        self._eps_L_combo.setCurrentIndex(idx)
        self._eps_L_combo.blockSignals(False)
        self._update_eps_visibility(state.eps_L_unit)


# ---------------------------------------------------------------------------
# Tab 4 — Ring / RF
# ---------------------------------------------------------------------------
class RingRFTab(_BaseTab):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        box_ring, fields_ring = _make_group("Ring Parameters", [
            "circumference", "bending_radius",
            "alpha_c", "eta_slip", "gamma_tr",
            "f_rev",
        ])
        self._register_group(box_ring, fields_ring)

        box_rf, fields_rf = _make_group("RF Parameters", [
            "harmonic", "f_RF",
            "V_RF", "phi_s",
            "Q_s", "energy_accept", "bucket_area",
        ])
        self._register_group(box_rf, fields_rf)

        box_sc, fields_sc = _make_group("Space Charge", [
            "N_ppb", "bunching_factor", "I_beam",
            "delta_Qx_sc", "delta_Qy_sc",
        ])
        self._register_group(box_sc, fields_sc)
        self._inner_layout.addStretch()


# ---------------------------------------------------------------------------
# Tab 5 — Radiation  (electron rings only)
# ---------------------------------------------------------------------------
class RadiationTab(_BaseTab):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        note = QLabel(
            "ℹ  Requires: bending radius ρ (Ring/RF tab), total energy, and revolution frequency."
        )
        note.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")
        note.setWordWrap(True)
        self._inner_layout.addWidget(note)

        box, fields = _make_group("Synchrotron Radiation", [
            "U0", "E_crit",
            "tau_x", "tau_y", "tau_z",
            "sigma_E_sr",
        ])
        self._register_group(box, fields)
        self._inner_layout.addStretch()


# ---------------------------------------------------------------------------
# Tab 6 — Luminosity  (collider mode only)
# ---------------------------------------------------------------------------
class LuminosityTab(_BaseTab):
    hourglass_changed = Signal(bool)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Hourglass toggle
        hg_row = QWidget()
        hg_layout = QHBoxLayout(hg_row)
        hg_layout.setContentsMargins(8, 4, 8, 0)
        self._hg_check = QCheckBox("Apply hourglass correction factor H")
        self._hg_check.setStyleSheet("color: #aaa;")
        self._hg_check.stateChanged.connect(
            lambda s: self.hourglass_changed.emit(bool(s))
        )
        hg_layout.addWidget(self._hg_check)
        hg_layout.addStretch()
        self._inner_layout.addWidget(hg_row)

        note = QLabel(
            "ℹ  Beam 1 parameters come from the Relativistic and Transverse tabs.\n"
            "   Enter Beam 2 parameters below.  Save/Load buttons in the toolbar\n"
            "   let you export the current state and reload it as Beam 2."
        )
        note.setStyleSheet("color: #888; font-style: italic; font-size: 11px;")
        note.setWordWrap(True)
        self._inner_layout.addWidget(note)

        box_b1, fields_b1 = _make_group("Beam 1", [
            "N1",
        ])
        self._register_group(box_b1, fields_b1)

        box_b2, fields_b2 = _make_group("Beam 2", [
            "N2", "eps_geo_x2", "eps_geo_y2", "sigma_z_m2",
        ])
        self._register_group(box_b2, fields_b2)

        box_coll, fields_coll = _make_group("Collision Parameters", [
            "crossing_angle",
        ])
        self._register_group(box_coll, fields_coll)

        box_lumi, fields_lumi = _make_group("Result", [
            "luminosity",
        ])
        self._register_group(box_lumi, fields_lumi)
        self._inner_layout.addStretch()

    def push_state(self, state: BeamState, conflicts: list[str]) -> None:
        super().push_state(state, conflicts)
        self._hg_check.blockSignals(True)
        self._hg_check.setChecked(state.hourglass)
        self._hg_check.blockSignals(False)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------
def _parse_conflict_fields(conflicts: list[str]) -> set[str]:
    """Extract field names from conflict message strings."""
    fields = set()
    for msg in conflicts:
        if ":" in msg:
            fields.add(msg.split(":")[0].strip())
    return fields


def _derived_fields(state: BeamState) -> set[str]:
    """
    Fields that are always derived (never user-input).
    Used to decide computed vs user colouring.
    Right now just E_rest, but could expand.
    """
    return {"E_rest"}