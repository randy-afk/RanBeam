# RanBeam

**Accelerator Beam Parameter Calculator**

RanBeam is a Python desktop application for computing relativistic beam parameters, optics quantities, synchrotron radiation properties, and luminosity — for any particle species and machine type.

Enter any combination of known values and the solver propagates through the full dependency graph to fill in everything else. Conflicts are flagged immediately.

---

![RanBeam GUI screenshot](assets/screenshot.png)

---

## What it does

- **Relativistic kinematics** — kinetic energy, total energy, momentum, Bρ, β, γ
- **Transverse optics** — normalized and geometric emittance, beam size σ, divergence σ′, total size with dispersion
- **Longitudinal parameters** — bunch length σ_z, bunch duration σ_t, longitudinal emittance
- **Ring / RF** — revolution frequency, RF frequency, slip factor η, transition γ, synchrotron tune Q_s
- **Synchrotron radiation** — energy loss per turn U₀, critical energy E_c, damping times, equilibrium energy spread (electrons)
- **Luminosity** — single-beam save/load for two-beam head-on luminosity calculation

## Quick start

```bash
pip install PySide6 matplotlib
python main.py
```

!!! tip "Solver philosophy"
    You are never required to enter values in a specific order. Fill in whatever you know — the solver figures out the rest. If two inputs conflict, a warning is shown and the offending fields are highlighted.

---

*Author: Randika Gamage — Jefferson Lab / BNL*
