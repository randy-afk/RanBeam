# Installation

!!! warning "Work in progress"
    RanBeam is under active development. Features may change and bugs may exist.
    Proceed at your own risk.
    
## Requirements

| Requirement | Version |
|---|---|
| Python | 3.10 or newer (3.13 recommended) |
| PySide6 | 6.x |
| matplotlib | 3.x |

No additional dependencies. All physics is pure Python.

## Install dependencies

```bash
pip install PySide6 matplotlib
```

## Get the code

Clone the repository:

```bash
git clone https://github.com/randy-afk/RanBeam.git
cd RanBeam
```

Or download a ZIP from the [GitHub releases page](https://github.com/randy-afk/RanBeam/releases).

## Run

```bash
python main.py
```

The GUI will open immediately. No configuration or data files are required.

## File overview

```
RanBeam/
├── main.py          # Entry point — run this
├── models.py        # BeamState dataclass, particle presets, unit/label dicts
├── physics.py       # Pure-Python dependency graph solver
├── beam_io.py       # Save / load beam states as JSON
└── gui/
    ├── app.py       # QMainWindow, menus, solver wiring
    ├── fields.py    # LockableField widget
    ├── tabs.py      # Tab classes (one per physics domain)
    ├── logo.py      # Matplotlib logo generator
    └── palette.py   # All UI colors — single source of truth
```

!!! note
    `palette.py` is the single source of truth for all GUI colors. Never hardcode color values elsewhere.
