# RanBeam

**Accelerator Beam Parameter Calculator**

> [!WARNING]
> RanBeam is under active development. Features may change and bugs may exist.
> Proceed at your own risk.
>


Auto-propagating dependency graph solver for accelerator physics parameters.
Enter any known quantities — everything derivable is computed automatically.
Conflicting inputs are flagged, not silently overridden.

---

## Features

- **Relativistic block**: KE, E_total, p, Bρ, β, γ, βγ, v
- **Transverse**: geometric and normalised emittance (x, y), beam size, divergence, total beam size with dispersion — all at a user-supplied Twiss point
- **Longitudinal**: momentum spread, emittance (eV·s or eV·m), bunch length (m and s)
- **Ring / RF** *(circular machines)*: circumference, bending radius, αc, slip factor, γtr, f_rev, h, f_RF, V_RF, φs, Qs, bucket area
- **Synchrotron radiation** *(electron rings)*: U₀, Ec, damping times τx/τy/τz, SR energy spread
- **Luminosity** *(collider mode)*: geometric + optional hourglass correction, crossing-angle reduction
- **Save / Load** beam states as JSON — load a saved state as Beam 2 for luminosity calculations
- **Lock fields** to fix a value and explore how others change

## Requirements

```
PySide6
```

## Usage

```bash
python main.py
```

## Project Structure

```
RanBeam/
├── main.py          # Entry point
├── models.py        # ParticlePreset, BeamState, units, labels
├── physics.py       # Dependency graph solver — pure Python, no Qt
├── io.py            # Save / load JSON
└── gui/
    ├── app.py       # QMainWindow, menus, solver wiring
    ├── fields.py    # LockableField widget
    └── tabs.py      # One class per tab
```

## Machine Types

| Type | Tabs unlocked |
|---|---|
| Linac / Single-pass | Relativistic, Transverse, Longitudinal |
| Circular — Protons/Ions | + Ring/RF |
| Circular — Electrons | + Radiation |
| Collider | + Luminosity |


> [!NOTE]
> **Author:** Randika Gamage — Jefferson Lab **Contact:** randika@jlab.org
> Support: *Good luck, I believe in you* 🫡