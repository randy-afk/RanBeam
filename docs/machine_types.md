# Machine Types

RanBeam adapts its interface based on the selected machine type. Tabs and parameters that are not relevant to a given machine are hidden to keep the interface uncluttered.

---

## Linac

**Use for:** linear accelerators, transfer lines, injection beamlines, fixed-target beamlines.

**Tabs available:**

- Relativistic / Kinematics
- Transverse Optics
- Longitudinal

**Notes:** No ring parameters. No synchrotron radiation. RF voltage can still be entered for longitudinal matching, but there is no revolution frequency or harmonic number.

---

## Circular — Proton / Ion

**Use for:** proton synchrotrons, heavy ion rings, storage rings with protons or ions.

**Tabs available:**

- Relativistic / Kinematics
- Transverse Optics
- Longitudinal
- Ring / RF

**Notes:** Synchrotron radiation is negligible for heavy particles at typical energies and is not computed. If you need SR for very high energy protons, use the Circular Electron type and adjust the rest mass manually.

---

## Circular — Electron

**Use for:** electron storage rings, light sources, electron synchrotrons, electron cooling rings.

**Tabs available:**

- Relativistic / Kinematics
- Transverse Optics
- Longitudinal
- Ring / RF
- Synchrotron Radiation

**Notes:** The SR tab uses the isomagnetic approximation (uniform bending radius). Damping partition numbers default to Jx = 1, Jy = 1, Js = 2 and can be overridden.

---

## Collider

**Use for:** head-on colliders (lepton or hadron), two-beam luminosity studies.

**Tabs available:**

- Relativistic / Kinematics
- Transverse Optics
- Longitudinal
- Ring / RF
- Synchrotron Radiation *(electron beams only)*
- Luminosity

**Notes:** The Luminosity tab becomes active. Load two saved beam states (Beam 1 and Beam 2) to compute the peak luminosity. See [Luminosity](luminosity.md) for the workflow.

!!! tip "Mixed-species colliders"
    For an electron-ion collider (e.g. EIC), configure each beam separately with its own particle type, then save each state and load both into the Luminosity tab.
