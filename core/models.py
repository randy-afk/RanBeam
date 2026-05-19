"""
models.py — RanBeam
====================
Particle presets, unit definitions, and the BeamState dataclass.
No Qt imports here — pure Python.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import json


# ---------------------------------------------------------------------------
# Physical constants (SI)
# ---------------------------------------------------------------------------
C_LIGHT   = 2.99792458e8          # m/s
E_CHARGE  = 1.602176634e-19       # C
EV_TO_J   = E_CHARGE              # 1 eV in Joules
MEV_TO_J  = 1e6 * EV_TO_J
GEV_TO_J  = 1e9 * EV_TO_J


# ---------------------------------------------------------------------------
# Particle presets  (mass in MeV/c², charge in units of e)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ParticlePreset:
    name:        str
    mass_MeV:    float   # rest mass in MeV/c²
    charge:      float   # in units of elementary charge e


PARTICLES: dict[str, ParticlePreset] = {
    "Electron": ParticlePreset("Electron", mass_MeV=0.51099895,   charge=-1.0),
    "Positron": ParticlePreset("Positron", mass_MeV=0.51099895,   charge=+1.0),
    "Proton":   ParticlePreset("Proton",   mass_MeV=938.27208816, charge=+1.0),
    "Antiproton": ParticlePreset("Antiproton", mass_MeV=938.27208816, charge=-1.0),
    "Deuteron": ParticlePreset("Deuteron", mass_MeV=1875.61294,   charge=+1.0),
    "Gold ion (Au79+)": ParticlePreset("Gold ion (Au79+)", mass_MeV=183_473.0, charge=+79.0),
    "Lead ion (Pb82+)": ParticlePreset("Lead ion (Pb82+)", mass_MeV=193_729.0, charge=+82.0),
    "Custom":   ParticlePreset("Custom",   mass_MeV=938.27208816, charge=+1.0),
}


# ---------------------------------------------------------------------------
# Unit labels for every field (shown next to the input box)
# ---------------------------------------------------------------------------
UNITS: dict[str, str] = {
    # --- Particle ---
    "mass_MeV":        "MeV/c²",
    "charge":          "e",
    # --- Relativistic ---
    "KE":              "MeV",
    "E_total":         "MeV",
    "E_rest":          "MeV",
    "momentum":        "MeV/c",
    "Brho":            "T·m",
    "beta":            "",          # dimensionless
    "gamma":           "",          # dimensionless
    "beta_gamma":      "",          # dimensionless
    "velocity":        "m/s",
    # --- Transverse (x) ---
    "eps_geo_x":       "m·rad",
    "eps_n_x":         "m·rad",
    "beta_star_x":     "m",
    "alpha_star_x":    "",
    "eta_x":           "m",
    "sigma_x":         "m",
    "sigma_prime_x":   "rad",
    "sigma_x_total":   "m",
    # --- Transverse (y) ---
    "eps_geo_y":       "m·rad",
    "eps_n_y":         "m·rad",
    "beta_star_y":     "m",
    "alpha_star_y":    "",
    "eta_y":           "m",
    "sigma_y":         "m",
    "sigma_prime_y":   "rad",
    "sigma_y_total":   "m",
    # --- Longitudinal ---
    "delta_p":         "",          # Δp/p, dimensionless
    "eps_L_eVs":       "eV·s",
    "eps_L_eVm":       "eV·m",
    "sigma_z_m":       "m",
    "sigma_z_t":       "s",
    # --- Ring / RF ---
    "circumference":   "m",
    "bending_radius":  "m",
    "alpha_c":         "",
    "eta_slip":        "",
    "gamma_tr":        "",
    "f_rev":           "Hz",
    "harmonic":        "",          # integer
    "f_RF":            "Hz",
    "V_RF":            "MV",
    "phi_s":           "deg",
    "Q_s":             "",
    "bucket_area":     "eV·s",
    # --- Radiation (electrons) ---
    "U0":              "keV",
    "E_crit":          "keV",
    "tau_x":           "ms",
    "tau_y":           "ms",
    "tau_z":           "ms",
    "sigma_E_sr":      "MeV",
    # --- Luminosity ---
    "N1":              "particles",
    "N2":              "particles",
    "luminosity":      "cm⁻²s⁻¹",
    "crossing_angle":  "mrad",
}


# ---------------------------------------------------------------------------
# Human-readable labels for every field
# ---------------------------------------------------------------------------
LABELS: dict[str, str] = {
    # Particle
    "mass_MeV":        "Rest mass  m₀",
    "charge":          "Charge  q",
    # Relativistic
    "KE":              "Kinetic energy  KE",
    "E_total":         "Total energy  E",
    "E_rest":          "Rest energy  m₀c²",
    "momentum":        "Momentum  p",
    "Brho":            "Magnetic rigidity  Bρ",
    "beta":            "Velocity ratio  β",
    "gamma":           "Lorentz factor  γ",
    "beta_gamma":      "βγ",
    "velocity":        "Velocity  v",
    # Transverse x
    "eps_geo_x":       "Geometric emittance  εₓ",
    "eps_n_x":         "Normalised emittance  εₙₓ",
    "beta_star_x":     "Beta function  β*ₓ",
    "alpha_star_x":    "Alpha function  α*ₓ",
    "eta_x":           "Dispersion  ηₓ",
    "sigma_x":         "Beam size  σₓ",
    "sigma_prime_x":   "Divergence  σ′ₓ",
    "sigma_x_total":   "Total beam size  σₓ,tot",
    # Transverse y
    "eps_geo_y":       "Geometric emittance  εᵧ",
    "eps_n_y":         "Normalised emittance  εₙᵧ",
    "beta_star_y":     "Beta function  β*ᵧ",
    "alpha_star_y":    "Alpha function  α*ᵧ",
    "eta_y":           "Dispersion  ηᵧ",
    "sigma_y":         "Beam size  σᵧ",
    "sigma_prime_y":   "Divergence  σ′ᵧ",
    "sigma_y_total":   "Total beam size  σᵧ,tot",
    # Longitudinal
    "delta_p":         "Momentum spread  δ = Δp/p",
    "eps_L_eVs":       "Long. emittance  εL",
    "eps_L_eVm":       "Long. emittance  εL",
    "sigma_z_m":       "Bunch length  σz",
    "sigma_z_t":       "Bunch length  σt",
    # Ring / RF
    "circumference":   "Circumference  C",
    "bending_radius":  "Bending radius  ρ",
    "alpha_c":         "Momentum compaction  αc",
    "eta_slip":        "Slip factor  η",
    "gamma_tr":        "Transition gamma  γtr",
    "f_rev":           "Revolution freq.  f₀",
    "harmonic":        "Harmonic number  h",
    "f_RF":            "RF frequency  fRF",
    "V_RF":            "RF voltage  VRF",
    "phi_s":           "Synchronous phase  φs",
    "Q_s":             "Synchrotron tune  Qs",
    "bucket_area":     "RF bucket area",
    # Radiation
    "U0":              "Energy loss/turn  U₀",
    "E_crit":          "Critical photon energy  Ec",
    "tau_x":           "Horizontal damping time  τx",
    "tau_y":           "Vertical damping time  τy",
    "tau_z":           "Longitudinal damping time  τz",
    "sigma_E_sr":      "SR energy spread  σE",
    # Luminosity
    "N1":              "Particles / bunch  N₁",
    "N2":              "Particles / bunch  N₂",
    "luminosity":      "Luminosity  ℒ",
    "crossing_angle":  "Crossing angle  θc",
}


# ---------------------------------------------------------------------------
# BeamState — the complete set of parameters as Optional floats
# ---------------------------------------------------------------------------
@dataclass
class BeamState:
    """Holds every calculable beam parameter. None = unknown/not yet set."""

    # Particle identity
    particle_name: str   = "Proton"
    mass_MeV:      float = 938.27208816
    charge:        float = 1.0

    # Machine type
    machine_type: str = "linac"  # "linac" | "circular_proton" | "circular_electron" | "collider"

    # Longitudinal emittance display unit
    eps_L_unit: str = "eVs"   # "eVs" or "eVm"

    # Hourglass correction enabled
    hourglass: bool = False

    # --- Relativistic ---
    KE:         Optional[float] = None
    E_total:    Optional[float] = None
    E_rest:     Optional[float] = None
    momentum:   Optional[float] = None
    Brho:       Optional[float] = None
    beta:       Optional[float] = None
    gamma:      Optional[float] = None
    beta_gamma: Optional[float] = None
    velocity:   Optional[float] = None

    # --- Transverse x ---
    eps_geo_x:      Optional[float] = None
    eps_n_x:        Optional[float] = None
    beta_star_x:    Optional[float] = None
    alpha_star_x:   Optional[float] = None
    eta_x:          Optional[float] = None
    sigma_x:        Optional[float] = None
    sigma_prime_x:  Optional[float] = None
    sigma_x_total:  Optional[float] = None

    # --- Transverse y ---
    eps_geo_y:      Optional[float] = None
    eps_n_y:        Optional[float] = None
    beta_star_y:    Optional[float] = None
    alpha_star_y:   Optional[float] = None
    eta_y:          Optional[float] = None
    sigma_y:        Optional[float] = None
    sigma_prime_y:  Optional[float] = None
    sigma_y_total:  Optional[float] = None

    # --- Longitudinal ---
    delta_p:     Optional[float] = None
    eps_L_eVs:   Optional[float] = None
    eps_L_eVm:   Optional[float] = None
    sigma_z_m:   Optional[float] = None
    sigma_z_t:   Optional[float] = None

    # --- Ring / RF ---
    circumference:  Optional[float] = None
    bending_radius: Optional[float] = None
    alpha_c:        Optional[float] = None
    eta_slip:       Optional[float] = None
    gamma_tr:       Optional[float] = None
    f_rev:          Optional[float] = None
    harmonic:       Optional[float] = None
    f_RF:           Optional[float] = None
    V_RF:           Optional[float] = None
    phi_s:          Optional[float] = None
    Q_s:            Optional[float] = None
    bucket_area:    Optional[float] = None

    # --- Radiation ---
    U0:         Optional[float] = None
    E_crit:     Optional[float] = None
    tau_x:      Optional[float] = None
    tau_y:      Optional[float] = None
    tau_z:      Optional[float] = None
    sigma_E_sr: Optional[float] = None

    # --- Luminosity (beam 2 values stored flat) ---
    N1:             Optional[float] = None
    N2:             Optional[float] = None
    eps_geo_x2:     Optional[float] = None
    eps_geo_y2:     Optional[float] = None
    sigma_z_m2:     Optional[float] = None
    crossing_angle: Optional[float] = None
    luminosity:     Optional[float] = None

    # --- Locked fields (set of field names the user has pinned) ---
    locked: set = field(default_factory=set)

    # -----------------------------------------------------------------------
    def to_dict(self) -> dict:
        d = asdict(self)
        d["locked"] = list(self.locked)   # sets aren't JSON-serialisable
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "BeamState":
        d = dict(d)
        d["locked"] = set(d.get("locked", []))
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})

    def save(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> "BeamState":
        with open(path) as f:
            return cls.from_dict(json.load(f))
