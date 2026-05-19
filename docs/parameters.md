# Parameters

Every parameter in RanBeam, its symbol, units, and which GUI tab it lives in.

---

## Relativistic / Kinematics tab

| Parameter | Symbol | Units | Notes |
|---|---|---|---|
| Particle species | — | — | Preset selector: e⁻, p, custom |
| Rest mass | m₀c² | MeV | From preset or user-entered |
| Charge | q | e | From preset or user-entered |
| Kinetic energy | KE | MeV | User input or derived |
| Total energy | E | MeV | KE + m₀c² |
| Lorentz factor | γ | — | E / m₀c² |
| Velocity ratio | β | — | √(1 − 1/γ²) |
| Momentum | p | MeV/c | γβm₀c |
| Magnetic rigidity | Bρ | T·m | p / q |

---

## Transverse Optics tab

| Parameter | Symbol | Units | Notes |
|---|---|---|---|
| Normalized emittance (x) | εₙˣ | μm | User input or derived |
| Normalized emittance (y) | εₙʸ | μm | User input or derived |
| Geometric emittance (x) | εˣ | μm | εₙ / βγ |
| Geometric emittance (y) | εʸ | μm | εₙ / βγ |
| Beta function at IP (x) | β*ˣ | m | User input |
| Beta function at IP (y) | β*ʸ | m | User input |
| RMS beam size (x) | σˣ | mm | √(εˣ · β*ˣ) |
| RMS beam size (y) | σʸ | mm | √(εʸ · β*ʸ) |
| RMS divergence (x) | σ′ˣ | μrad | √(εˣ / β*ˣ) |
| RMS divergence (y) | σ′ʸ | μrad | √(εʸ / β*ʸ) |
| Dispersion (x) | η | m | User input |
| Momentum spread | δ | — | User input |
| Total beam size (x) | σ_tot | mm | √(εˣ·β*ˣ + (η·δ)²) |

---

## Longitudinal tab

| Parameter | Symbol | Units | Notes |
|---|---|---|---|
| Longitudinal emittance | ε_L | eV·s | User input or derived |
| Longitudinal emittance | ε_L | eV·m | ε_L[eV·s] · βc |
| RMS bunch duration | σ_t | ps | User input or derived |
| RMS bunch length | σ_z | mm | σ_t · βc |
| Momentum spread | δ | — | Shared with transverse tab |

---

## Ring / RF tab

*Visible for circular machine types only.*

| Parameter | Symbol | Units | Notes |
|---|---|---|---|
| Circumference | C | m | User input |
| Revolution frequency | f₀ | MHz | βc / C |
| Harmonic number | h | — | User input |
| RF frequency | f_RF | MHz | h · f₀ |
| RF voltage | V_RF | MV | User input |
| Synchronous phase | φ_s | deg | User input |
| Momentum compaction | αc | — | User input |
| Slip factor | η | — | αc − 1/γ² |
| Transition gamma | γ_tr | — | 1/√αc |
| Synchrotron tune | Q_s | — | Derived from h, η, V_RF, φ_s |

---

## Synchrotron Radiation tab

*Visible for circular electron machines only.*

| Parameter | Symbol | Units | Notes |
|---|---|---|---|
| Bending radius | ρ | m | User input |
| Energy loss per turn | U₀ | keV | Cγ · E⁴/ρ |
| Critical photon energy | E_c | keV | 2.218 · E³/ρ |
| Horizontal damping time | τx | ms | 2E/(Jx·U₀) · T₀ |
| Vertical damping time | τy | ms | 2E/(Jy·U₀) · T₀ |
| Longitudinal damping time | τs | ms | 2E/(Js·U₀) · T₀ |
| Equilibrium energy spread | σ_E/E | — | √(Cq·γ²/Jz·ρ) |

Damping partition numbers Jx, Jy, Js default to 1, 1, 2 (isomagnetic ring).

---

## Luminosity tab

*Visible for collider machine type.*

| Parameter | Symbol | Units | Notes |
|---|---|---|---|
| Bunch population (beam 1) | N₁ | — | From loaded state or user input |
| Bunch population (beam 2) | N₂ | — | From loaded state or user input |
| Revolution frequency | f₀ | Hz | From ring parameters |
| RMS size x (at IP) | σx | μm | From transverse tab |
| RMS size y (at IP) | σy | μm | From transverse tab |
| Peak luminosity | L | cm⁻²s⁻¹ | Computed |
