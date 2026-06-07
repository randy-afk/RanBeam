"""
core/formulas.py — RanBeam
===========================
Human-readable formula strings for every parameter field.
Used by the info button popup in the GUI.
"""

FORMULAS: dict[str, str] = {
    # --- Particle ---
    "mass_MeV":        "Rest mass m₀ — intrinsic property of the particle",
    "charge":          "Charge q in units of elementary charge e",

    # --- Relativistic ---
    "KE":              "KE = E_total − m₀c²",
    "E_total":         "E = KE + m₀c²  =  γ·m₀c²",
    "E_rest":          "E_rest = m₀c²  (rest energy, fixed by particle type)",
    "momentum":        "p = γβm₀c  =  √(E² − m₀²c⁴) / c",
    "Brho":            "Bρ = p / q  [T·m]  (magnetic rigidity)",
    "beta":            "β = v/c  =  √(1 − 1/γ²)  =  p·c / E",
    "gamma":           "γ = E / m₀c²  =  1 / √(1 − β²)",
    "beta_gamma":      "βγ = p / m₀c  =  β·γ",
    "velocity":        "v = β·c",

    # --- Transverse x ---
    "eps_geo_x":       "εₓ (geometric)  =  εₙₓ / βγ",
    "eps_n_x":         "εₙₓ (normalised)  =  βγ·εₓ",
    "beta_star_x":     "β*ₓ — Twiss beta function at point of interest (user-supplied)",
    "alpha_star_x":    "α*ₓ — Twiss alpha function at point of interest (user-supplied)",
    "eta_x":           "ηₓ — dispersion function at point of interest (user-supplied)",
    "sigma_x":         "σₓ = √(εₓ·β*ₓ)  [m]",
    "sigma_prime_x":   "σ′ₓ = √(εₓ / β*ₓ)  [rad]",
    "sigma_x_total":   "σₓ,tot = √(εₓ·β*ₓ + (ηₓ·δ)²)  (dispersive beam size)",

    # --- Transverse y ---
    "eps_geo_y":       "εᵧ (geometric)  =  εₙᵧ / βγ",
    "eps_n_y":         "εₙᵧ (normalised)  =  βγ·εᵧ",
    "beta_star_y":     "β*ᵧ — Twiss beta function at point of interest (user-supplied)",
    "alpha_star_y":    "α*ᵧ — Twiss alpha function at point of interest (user-supplied)",
    "eta_y":           "ηᵧ — dispersion function at point of interest (user-supplied)",
    "sigma_y":         "σᵧ = √(εᵧ·β*ᵧ)  [m]",
    "sigma_prime_y":   "σ′ᵧ = √(εᵧ / β*ᵧ)  [rad]",
    "sigma_y_total":   "σᵧ,tot = √(εᵧ·β*ᵧ + (ηᵧ·δ)²)  (dispersive beam size)",

    # --- Longitudinal ---
    "delta_p":         "δ = Δp/p  (fractional momentum spread)",
    "eps_L_eVs":       "εL [eV·s]  =  π·σz·σ_E/(β·c)  where σ_E = δ·E  (1σ phase-space area, (z,E) conjugate variables). Also: εL[eV·s] = εL[eV·m]/(β·c). Convention: 1σ ellipse area = π·σz·σE.",
    "eps_L_eVm":       "εL [eV·m]  =  εL [eV·s]·β·c  =  π·σz·σ_E  (same convention as eV·s, just multiplied by β·c)",
    "sigma_z_m":       "σz [m]  =  σt · β·c",
    "sigma_z_t":       "σt [s]  =  σz / (β·c)",

    # --- Ring / RF ---
    "circumference":   "C — ring circumference  [m]",
    "bending_radius":  "ρ — bending radius of dipoles  [m]",
    "alpha_c":         "αc — momentum compaction factor  =  1/γ²tr",
    "eta_slip":        "η = αc − 1/γ²  (slip factor)",
    "gamma_tr":        "γtr = 1/√αc  (transition gamma)",
    "f_rev":           "f₀ = β·c / C  (revolution frequency)",
    "harmonic":        "h — harmonic number  =  f_RF / f₀",
    "f_RF":            "f_RF = h·f₀  (RF frequency)",
    "V_RF":            "V_RF — peak RF voltage  [MV]",
    "phi_s":           "φs — synchronous phase  [deg]",
    "Q_s":             "Qs = √( h·|η|·eV·|cosφs| / (2π·E) )  (synchrotron tune)",
    "energy_accept":   "δ_max = β·√(eV/(π·h·|η|·E))  — momentum acceptance of the RF bucket (dimensionless, stationary bucket φs=0)",
    "bucket_area":     "A = (8/ω_RF)·√(eV·E·|η|·β²/(2π·h))  [eV·s]  — requires f_rev. Stationary bucket (φs=0). Ref: Wiedemann PAP eq.9.70",
    "N_ppb":           "N — particles per bunch",
    "bunching_factor": "Bf — bunching factor  =  σz / (C/h)  (0 < Bf ≤ 1)",
    "I_beam":          "I = N·q·f₀  (average beam current)  [A]",
    "delta_Qx_sc":     "ΔQx (space charge)  =  −N·r₀ / (4π·γ³·β²·εₓ·Bf)  — Laslett formula, round beam, single plane. r₀ = classical particle radius. Valid for space charge dominated regime.",
    "delta_Qy_sc":     "ΔQy (space charge)  =  −N·r₀ / (4π·γ³·β²·εᵧ·Bf)  — same as ΔQx but uses vertical emittance εᵧ.",

    # --- Radiation ---
    "U0":              "U₀ = Cγ·E⁴/ρ  [keV/turn]  (Cγ = 8.85×10⁻⁵ m/GeV³)",
    "E_crit":          "Ec = 2.218·E³/ρ  [keV]  (critical photon energy)",
    "tau_x":           "τx = 2E / (Jx·U₀·f₀)  [ms]  (horizontal damping time, Jx≈1)",
    "tau_y":           "τy = 2E / (Jy·U₀·f₀)  [ms]  (vertical damping time, Jy≈1)",
    "tau_z":           "τz = 2E / (Jz·U₀·f₀)  [ms]  (longitudinal damping time, Jz≈2)",
    "sigma_E_sr":      "σE = √(Cq·γ²/Jz·ρ)·E  [MeV]  (Cq = 3.83×10⁻¹³ m)",

    # --- Luminosity ---
    "N1":              "N₁ — particles per bunch, Beam 1",
    "N2":              "N₂ — particles per bunch, Beam 2",
    "luminosity":      "L = N₁N₂f₀ / (4π·σx·σy)  [cm⁻²s⁻¹]",
    "crossing_angle":  "θc — full crossing angle at IP  [mrad]",
}