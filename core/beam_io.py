"""
io.py — RanBeam
================
Save and load BeamState to/from JSON files.
Thin wrapper around BeamState.save() / BeamState.load()
with user-facing error handling.
"""

from __future__ import annotations
import json
from pathlib import Path
from core.models import BeamState


def save_state(state: BeamState, path: str) -> None:
    """Save BeamState to a JSON file."""
    state.save(path)


def load_state(path: str) -> BeamState:
    """Load BeamState from a JSON file. Raises ValueError on bad file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if p.suffix.lower() != ".json":
        raise ValueError(f"Expected a .json file, got: {path}")
    try:
        return BeamState.load(path)
    except (json.JSONDecodeError, TypeError, KeyError) as e:
        raise ValueError(f"Could not parse beam state file: {e}") from e
