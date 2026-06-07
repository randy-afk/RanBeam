"""
gui/fields.py — RanBeam
========================
LockableField: a single-row widget containing:
  - a label (parameter name)
  - a QLineEdit (editable value)
  - a unit label (read-only)
  - a lock toggle button

Colour states:
  - Normal       : default palette
  - Computed     : subtle teal tint  (field was filled in by the solver)
  - Conflict     : red background     (solver computed a value inconsistent with input)
  - Locked       : grey background    (user has pinned this value)
"""

from __future__ import annotations
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QMenu, QApplication, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QEvent
from PySide6.QtGui import QColor, QPalette


from core.formulas import FORMULAS
from palette import (
    BG, PANEL, MANTLE, BORDER, SURFACE2,
    ACCENT, ACCENT2, FG, FG_DIM, FG_LBL,
    SUCCESS, WARN, ERROR,
    COLOR_COMPUTED, COLOR_CONFLICT,
    COLOR_LOCKED_BG, COLOR_LOCKED_FG, COLOR_LOCK_ON, COLOR_LOCK_OFF,
)


class LockableField(QWidget):
    """
    One parameter row.

    Signals
    -------
    value_changed(field_name: str, text: str)
        Emitted whenever the user edits the text.
    lock_toggled(field_name: str, locked: bool)
        Emitted when the lock button is toggled.
    """

    value_changed  = Signal(str, str)
    lock_toggled   = Signal(str, bool)

    def __init__(
        self,
        field_name: str,
        label:      str,
        unit:       str,
        parent:     QWidget | None = None,
    ):
        super().__init__(parent)
        self.field_name = field_name
        self._locked    = False
        self._conflict  = False
        self._computed  = False

        # --- Layout ---
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(6)

        # Label (fixed width so columns align)
        self._label = QLabel(label)
        self._label.setFixedWidth(240)
        self._label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self._label.setStyleSheet(f"color: {FG_LBL}; font-size: 12px;")
        layout.addWidget(self._label)

        # Value entry
        self._edit = QLineEdit()
        self._edit.setFixedWidth(160)
        self._edit.setPlaceholderText("—")
        self._edit.setAlignment(Qt.AlignRight)
        self._edit.setStyleSheet(self._edit_style())
        self._edit.textEdited.connect(self._on_text_edited)
        layout.addWidget(self._edit)

        # Unit label
        self._unit = QLabel(unit if unit else "")
        self._unit.setFixedWidth(80)
        self._unit.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self._unit.setStyleSheet(f"color: {FG_DIM}; font-size: 11px;")
        layout.addWidget(self._unit)

        # Info button
        self._info_btn = QPushButton("i")
        self._info_btn.setFixedSize(24, 24)
        self._info_btn.setToolTip("Show formula")
        self._info_btn.setStyleSheet(
            f"QPushButton {{ background: {PANEL}; border: 1px solid {ACCENT};"
            f" border-radius: 4px; color: {ACCENT}; font-size: 11px; font-weight: bold; }}"
            f"QPushButton:hover {{ background: {ACCENT}; color: {BG}; }}"
        )
        self._info_btn.clicked.connect(self._on_info_clicked)
        layout.addWidget(self._info_btn)

        # Lock button
        self._lock_btn = QPushButton("🔓")
        self._lock_btn.setFixedSize(32, 28)
        self._lock_btn.setCheckable(True)
        self._lock_btn.setToolTip("Lock this value")
        self._lock_btn.setStyleSheet(self._lock_style())
        self._lock_btn.clicked.connect(self._on_lock_clicked)
        layout.addWidget(self._lock_btn)

        layout.addStretch()

        # Right-click context menu on the edit field
        self._edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self._edit.customContextMenuRequested.connect(self._on_context_menu)

        # Keyboard navigation — Enter/Return moves to next field
        self._edit.returnPressed.connect(self._on_return_pressed)

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def set_value(self, value: float | None, computed: bool = False) -> None:
        """
        Push a value into the field.
        If computed=True, apply the 'computed' colour state.
        Does nothing if the field is locked.
        """
        if self._locked:
            return
        self._computed = computed
        if value is None:
            self._edit.setText("")
        else:
            # Choose a sensible number of significant figures
            self._edit.setText(_format_value(value))
        self._edit.setStyleSheet(self._edit_style())

    def get_value(self) -> float | None:
        """Return the current float value, or None if empty / invalid."""
        text = self._edit.text().strip()
        if not text:
            return None
        try:
            return float(text)
        except ValueError:
            return None

    def set_conflict(self, conflict: bool) -> None:
        self._conflict = conflict
        self._edit.setStyleSheet(self._edit_style())

    def set_locked(self, locked: bool) -> None:
        self._locked = locked
        self._lock_btn.setChecked(locked)
        self._lock_btn.setText("🔒" if locked else "🔓")
        self._lock_btn.setStyleSheet(self._lock_style())
        self._edit.setReadOnly(locked)
        self._edit.setStyleSheet(self._edit_style())

    def clear(self) -> None:
        """Clear the field value (respects lock)."""
        if self._locked:
            return
        self._computed = False
        self._conflict = False
        self._edit.clear()
        self._edit.setStyleSheet(self._edit_style())

    @property
    def is_locked(self) -> bool:
        return self._locked

    # -----------------------------------------------------------------------
    # Internal slots
    # -----------------------------------------------------------------------

    def _on_text_edited(self, text: str) -> None:
        # User is typing — clear computed/conflict states
        self._computed = False
        self._conflict = False
        self._edit.setStyleSheet(self._edit_style())
        self.value_changed.emit(self.field_name, text)

    def _on_lock_clicked(self, checked: bool) -> None:
        self._locked = checked
        self._lock_btn.setText("🔒" if checked else "🔓")
        self._lock_btn.setStyleSheet(self._lock_style())
        self._edit.setReadOnly(checked)
        self._edit.setStyleSheet(self._edit_style())
        self.lock_toggled.emit(self.field_name, checked)

    def _on_info_clicked(self) -> None:
        formula = FORMULAS.get(self.field_name, "No formula available.")
        label   = self._label.text().strip()
        msg = QMessageBox(self.window())
        msg.setWindowTitle(f"Formula — {label}")
        msg.setText(formula)
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet(
            f"QMessageBox {{ background: {PANEL}; color: {FG}; }}"
            f"QLabel {{ color: {FG}; font-size: 12px; }}"
            f"QPushButton {{ background: {ACCENT}; color: {BG}; border-radius: 4px; padding: 4px 12px; }}"
        )
        msg.exec()

    def _on_context_menu(self, pos) -> None:
        menu = QMenu(self)
        menu.setStyleSheet(
            f"QMenu {{ background: {PANEL}; color: {FG}; border: 1px solid {BORDER}; }}"
            f"QMenu::item:selected {{ background: {ACCENT}; color: {BG}; }}"
        )
        copy_val = menu.addAction("Copy value")
        copy_with_unit = menu.addAction("Copy value with unit")
        menu.addSeparator()
        clear_act = menu.addAction("Clear field")

        action = menu.exec(self._edit.mapToGlobal(pos))
        if action == copy_val:
            txt = self._edit.text().strip()
            if txt:
                QApplication.clipboard().setText(txt)
        elif action == copy_with_unit:
            txt  = self._edit.text().strip()
            unit = self._unit.text().strip()
            if txt:
                QApplication.clipboard().setText(f"{txt} {unit}".strip())
        elif action == clear_act:
            self.clear()

    def _on_return_pressed(self) -> None:
        """Move focus to the next field in the tab order."""
        self._edit.focusNextChild()

    # -----------------------------------------------------------------------
    # Style helpers
    # -----------------------------------------------------------------------

    def _edit_style(self) -> str:
        if self._locked:
            return (
                f"QLineEdit {{ background: {COLOR_LOCKED_BG}; color: {COLOR_LOCKED_FG};"
                f" border: 1px solid {BORDER}; border-radius: 4px; padding: 2px 6px; }}"
            )
        if self._conflict:
            return (
                f"QLineEdit {{ background: {COLOR_CONFLICT}; color: {ERROR};"
                f" border: 1px solid {ERROR}; border-radius: 4px; padding: 2px 6px; }}"
            )
        if self._computed:
            return (
                f"QLineEdit {{ background: {COLOR_COMPUTED}; color: {ACCENT};"
                f" border: 1px solid {ACCENT2}; border-radius: 4px; padding: 2px 6px; }}"
            )
        # Normal — user-entered
        return (
            f"QLineEdit {{ background: {MANTLE}; color: {FG};"
            f" border: 1px solid {BORDER}; border-radius: 4px; padding: 2px 6px; }}"
            f"QLineEdit:focus {{ border: 1px solid {ACCENT}; border-left: 3px solid {ACCENT}; }}"
        )

    def _lock_style(self) -> str:
        if self._locked:
            return (
                f"QPushButton {{ background: {COLOR_LOCK_ON}; border: 1px solid {COLOR_LOCK_ON};"
                f" border-radius: 4px; color: {BG}; font-size: 10px; font-weight: bold; }}"
                f"QPushButton:hover {{ background: {ACCENT2}; }}"
            )
        return (
            f"QPushButton {{ background: transparent; border: 1px solid {BORDER};"
            f" border-radius: 4px; color: {FG_LBL}; font-size: 10px; }}"
            f"QPushButton:hover {{ background: {SURFACE2}; border-color: {ACCENT}; color: {ACCENT}; }}"
        )


# ---------------------------------------------------------------------------
# Formatting helper
# ---------------------------------------------------------------------------
def _format_value(v: float) -> str:
    """
    Format a float for display in a parameter field.
    Accepts and produces scientific notation (e.g. 4e-09, 1.23e+08).
    """
    if v == 0.0:
        return "0"
    abs_v = abs(v)
    if abs_v < 1e-3 or abs_v >= 1e6:
        # Scientific notation, 6 significant figures, clean up trailing zeros
        s = f"{v:.5e}"
        # e.g. "1.23000e-09" → "1.23e-09"
        mantissa, exp = s.split("e")
        mantissa = mantissa.rstrip("0").rstrip(".")
        exp_i = int(exp)
        return f"{mantissa}e{exp_i:+03d}" if exp_i != 0 else mantissa
    return f"{v:.8g}"
