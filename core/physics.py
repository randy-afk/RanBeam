"""
physics.py — RanBeam
=====================
Pure-Python dependency graph solver.
No Qt, no side effects — call solve() and get back results + conflicts.
"""

from __future__ import annotations
import math
from typing import Optional
from core.models import BeamState, C_LIGHT, E_CHARGE, MEV_TO_J

CONFLICT_TOL = 1e-4

# Classical proton radius (m)
R0_PROTON   = 1.534698e-18   # m  (r₀ = q²/4πε₀m₀c² scaled by charge)
R0_ELECTRON = 2.817940e-15   # m


# ---------------------------------------------------------------------------
# Physics formulas
# ---------------------------------------------------------------------------

def _gamma_from_E_total(E_total_MeV, m0_MeV):
    return E_total_MeV / m0_MeV

def _beta_from_gamma(gamma):
    if gamma < 1.0:
        raise ValueError(f"γ < 1 is unphysical (got {gamma:.6g})")
    return math.sqrt(1.0 - 1.0 / gamma**2)

def _E_total_from_KE(KE_MeV, m0_MeV):
    return KE_MeV + m0_MeV

def _KE_from_E_total(E_total_MeV, m0_MeV):
    return E_total_MeV - m0_MeV

def _p_from_E_total(E_total_MeV, m0_MeV):
    return math.sqrt(max(0.0, E_total_MeV**2 - m0_MeV**2))

def _E_total_from_p(p_MeV, m0_MeV):
    return math.sqrt(p_MeV**2 + m0_MeV**2)

def _Brho_from_p(p_MeV, q_e):
    return (p_MeV * MEV_TO_J / C_LIGHT) / (abs(q_e) * E_CHARGE)

def _p_from_Brho(Brho, q_e):
    return Brho * abs(q_e) * E_CHARGE * C_LIGHT / MEV_TO_J

def _eps_n_from_geo(eps_geo, beta, gamma):
    return beta * gamma * eps_geo

def _eps_geo_from_n(eps_n, beta, gamma):
    return eps_n / (beta * gamma)

def _sigma_from_eps_beta(eps_geo, beta_star):
    return math.sqrt(eps_geo * beta_star)

def _sigma_prime_from_eps_beta(eps_geo, beta_star):
    return math.sqrt(eps_geo / beta_star)

def _sigma_total(eps_geo, beta_star, eta, delta_p):
    return math.sqrt(eps_geo * beta_star + (eta * delta_p)**2)

def _eta_slip(alpha_c, gamma):
    return alpha_c - 1.0 / gamma**2

def _gamma_tr(alpha_c):
    return 1.0 / math.sqrt(alpha_c)

def _f_rev(C, beta):
    return beta * C_LIGHT / C

def _f_RF(f_rev, h):
    return h * f_rev

def _eps_L_eVm_from_eVs(eps_L_eVs, beta):
    return eps_L_eVs * beta * C_LIGHT

def _eps_L_eVs_from_eVm(eps_L_eVm, beta):
    return eps_L_eVm / (beta * C_LIGHT)

def _sigma_z_m_from_t(sigma_z_t, beta):
    return sigma_z_t * beta * C_LIGHT

def _sigma_z_t_from_m(sigma_z_m, beta):
    return sigma_z_m / (beta * C_LIGHT)

def _Qs(h, alpha_c, V_RF_MV, E_total_MeV, phi_s_deg, eta_slip):
    V_eV     = V_RF_MV * 1e6
    E_eV     = E_total_MeV * 1e6
    cos_phis = abs(math.cos(math.radians(phi_s_deg)))
    return math.sqrt(h * abs(eta_slip) * V_eV * cos_phis / (2 * math.pi * E_eV))

def _energy_acceptance(h, V_RF_MV, E_total_MeV, eta_slip, beta):
    """
    Momentum acceptance (half-height) of the RF bucket [dimensionless].
    Valid for stationary bucket (phi_s = 0).

    δ_max = sqrt( e*V / (pi*h*|eta|*E) ) * beta
          = beta * sqrt( eV / (pi*h*|eta|*E) )

    Reference: Wiedemann "PAP" eq. 9.68, Lee "AP" eq. 3.57.
    """
    try:
        V_eV = V_RF_MV * 1e6
        E_eV = E_total_MeV * 1e6
        return beta * math.sqrt(V_eV / (math.pi * h * abs(eta_slip) * E_eV))
    except Exception:
        return float("nan")

def _bucket_area(h, V_RF_MV, E_total_MeV, eta_slip, beta, f_rev):
    """
    RF bucket area for a stationary bucket (phi_s = 0) [eV·s].

    A = (8 / omega_RF) * sqrt( eV * E * |eta| / (2*pi*h) ) * beta
      = (8 / (2*pi*h*f_rev)) * sqrt( eV * E * |eta| * beta^2 / (2*pi*h) )

    With V in eV, E in eV, f_rev in Hz. Result in eV·s.
    Reference: Wiedemann "PAP" eq. 9.70.
    """
    try:
        V_eV  = V_RF_MV * 1e6
        E_eV  = E_total_MeV * 1e6
        omega_RF = 2 * math.pi * h * f_rev
        return (8.0 / omega_RF) * math.sqrt(
            V_eV * E_eV * abs(eta_slip) * beta**2 / (2 * math.pi * h)
        )
    except Exception:
        return float("nan")

def _classical_radius(m0_MeV, q_e):
    """Classical particle radius r₀ = q²/(4πε₀ m₀c²) in metres."""
    k_e = 8.9875517923e9   # N·m²/C²
    m0_kg = m0_MeV * MEV_TO_J / C_LIGHT**2
    return k_e * (abs(q_e) * E_CHARGE)**2 / (m0_kg * C_LIGHT**2)

def _space_charge_tune_shift(N, r0, gamma, beta, eps_geo, bunching_factor):
    """
    ΔQ_sc = -N·r₀ / (4π·γ³·β²·ε_geo·Bf)
    Returns tune shift (negative, defocusing).
    """
    if bunching_factor <= 0 or eps_geo <= 0:
        return float("nan")
    return -N * r0 / (4 * math.pi * gamma**3 * beta**2 * eps_geo * bunching_factor)

def _beam_current(N, q_e, f_rev):
    """Average beam current I = N·q·f₀  [A]"""
    return N * abs(q_e) * E_CHARGE * f_rev

# --- Synchrotron radiation ---

def _U0_keV(E_total_MeV, rho_m):
    Cgamma = 8.85e-5
    E_GeV  = E_total_MeV / 1e3
    return Cgamma * E_GeV**4 / rho_m * 1e3

def _E_crit_keV(E_total_MeV, rho_m):
    E_GeV = E_total_MeV / 1e3
    return 2.218 * E_GeV**3 / rho_m

def _tau_ms(E_total_MeV, U0_keV, T0_s, J):
    U0_MeV = U0_keV / 1e3
    return 2.0 * E_total_MeV / (J * U0_MeV) * T0_s * 1e3

def _sigma_E_sr_MeV(E_total_MeV, rho_m):
    Cq  = 3.83e-13
    Jz  = 2.0
    m0  = 0.51099895
    gam = E_total_MeV / m0
    sigma_delta = math.sqrt(Cq * gam**2 / (Jz * rho_m))
    return sigma_delta * E_total_MeV

# --- Luminosity ---

def _luminosity(N1, N2, f_rev, sigma_x, sigma_y,
                crossing_angle_mrad=0.0, hourglass=False,
                sigma_z=0.0, beta_star_x=1.0):
    theta = math.radians(crossing_angle_mrad * 1e-3)
    if crossing_angle_mrad > 0 and sigma_x > 0:
        sigma_eff_x = math.sqrt(sigma_x**2 + (sigma_z * math.tan(theta / 2))**2)
    else:
        sigma_eff_x = sigma_x
    L = (N1 * N2 * f_rev) / (4 * math.pi * sigma_eff_x * sigma_y)
    if hourglass and sigma_z > 0 and beta_star_x > 0:
        r = sigma_z / beta_star_x
        H = math.sqrt(math.pi) * r / (math.erf(r) * (1 + r**2)) if r > 1e-10 else 1.0
        L *= H
    return L * 1e-4


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def _conflict(computed, supplied, name):
    if supplied is None:
        return None
    if abs(computed) > 1e-30:
        rel = abs(computed - supplied) / abs(computed)
    else:
        rel = abs(computed - supplied)
    if rel > CONFLICT_TOL:
        return (f"{name}: computed {computed:.6g} ≠ supplied {supplied:.6g} "
                f"(Δ = {rel*100:.3f}%)")
    return None


# ---------------------------------------------------------------------------
# Main solver
# ---------------------------------------------------------------------------

def solve(state: BeamState) -> tuple[BeamState, list[str]]:
    s = BeamState(**{f: getattr(state, f) for f in state.__dataclass_fields__})
    s.locked = set(state.locked)
    conflicts: list[str] = []

    def set_field(name, value):
        if name in s.locked:
            return
        existing = getattr(s, name)
        if existing is not None:
            msg = _conflict(value, existing, name)
            if msg:
                conflicts.append(msg)
            return
        setattr(s, name, value)

    m0 = s.mass_MeV
    q  = s.charge

    # ------------------------------------------------------------------
    # Pass 1 — rest energy
    # ------------------------------------------------------------------
    s.E_rest = m0

    # ------------------------------------------------------------------
    # Pass 2 — Relativistic block (8 iterations for full chain resolution)
    # ------------------------------------------------------------------
    for _ in range(8):
        if s.KE is not None and s.E_total is None:
            set_field("E_total", _E_total_from_KE(s.KE, m0))
        if s.E_total is not None and s.KE is None:
            set_field("KE", _KE_from_E_total(s.E_total, m0))

        if s.E_total is not None and s.gamma is None:
            set_field("gamma", _gamma_from_E_total(s.E_total, m0))
        if s.gamma is not None and s.beta is None:
            try:
                set_field("beta", _beta_from_gamma(s.gamma))
            except ValueError as e:
                conflicts.append(str(e))

        if s.gamma is not None and s.E_total is None:
            set_field("E_total", s.gamma * m0)
        if s.beta is not None and s.gamma is not None and s.beta_gamma is None:
            set_field("beta_gamma", s.beta * s.gamma)

        if s.beta_gamma is not None and s.gamma is None:
            set_field("gamma", math.sqrt(1 + s.beta_gamma**2))
        if s.beta_gamma is not None and s.beta is None and s.gamma is not None:
            set_field("beta", s.beta_gamma / s.gamma)

        # beta → gamma (missing reverse path)
        if s.beta is not None and s.gamma is None:
            if 0 < s.beta < 1:
                set_field("gamma", 1.0 / math.sqrt(1.0 - s.beta**2))
            elif s.beta >= 1:
                conflicts.append(f"beta: β ≥ 1 is unphysical (got {s.beta:.6g})")

        if s.E_total is not None and s.momentum is None:
            set_field("momentum", _p_from_E_total(s.E_total, m0))
        if s.momentum is not None and s.E_total is None:
            set_field("E_total", _E_total_from_p(s.momentum, m0))

        if s.momentum is not None and s.Brho is None:
            set_field("Brho", _Brho_from_p(s.momentum, q))
        if s.Brho is not None and s.momentum is None:
            set_field("momentum", _p_from_Brho(s.Brho, q))

        if s.beta is not None and s.velocity is None:
            set_field("velocity", s.beta * C_LIGHT)
        if s.velocity is not None and s.beta is None:
            set_field("beta", s.velocity / C_LIGHT)

    # ------------------------------------------------------------------
    # Pass 3 — Transverse x (6 iterations to resolve all reverse chains)
    # ------------------------------------------------------------------
    for _ in range(6):
        b  = s.beta
        g  = s.gamma

        # geo ↔ normalised
        if b is not None and g is not None:
            if s.eps_geo_x is not None and s.eps_n_x is None:
                set_field("eps_n_x", _eps_n_from_geo(s.eps_geo_x, b, g))
            if s.eps_n_x is not None and s.eps_geo_x is None:
                set_field("eps_geo_x", _eps_geo_from_n(s.eps_n_x, b, g))

        # sigma + beta_star → eps_geo (reverse solve)
        if s.sigma_x is not None and s.beta_star_x is not None and s.eps_geo_x is None:
            set_field("eps_geo_x", s.sigma_x**2 / s.beta_star_x)

        # sigma_prime + beta_star → eps_geo (reverse solve)
        if s.sigma_prime_x is not None and s.beta_star_x is not None and s.eps_geo_x is None:
            set_field("eps_geo_x", s.sigma_prime_x**2 * s.beta_star_x)

        # eps_geo + beta_star → sigma, sigma_prime
        if s.eps_geo_x is not None and s.beta_star_x is not None:
            if s.sigma_x is None:
                set_field("sigma_x", _sigma_from_eps_beta(s.eps_geo_x, s.beta_star_x))
            if s.sigma_prime_x is None:
                set_field("sigma_prime_x", _sigma_prime_from_eps_beta(s.eps_geo_x, s.beta_star_x))

        # total beam size with dispersion
        if (s.eps_geo_x is not None and s.beta_star_x is not None
                and s.eta_x is not None and s.delta_p is not None
                and s.sigma_x_total is None):
            set_field("sigma_x_total",
                      _sigma_total(s.eps_geo_x, s.beta_star_x, s.eta_x, s.delta_p))

        # reverse: sigma_x_total → eps_geo_x (if eta and delta known)
        if (s.sigma_x_total is not None and s.beta_star_x is not None
                and s.eta_x is not None and s.delta_p is not None
                and s.eps_geo_x is None):
            disp_term = (s.eta_x * s.delta_p)**2
            val = (s.sigma_x_total**2 - disp_term) / s.beta_star_x
            if val > 0:
                set_field("eps_geo_x", val)

    # ------------------------------------------------------------------
    # Pass 4 — Transverse y
    # ------------------------------------------------------------------
    for _ in range(6):
        b = s.beta
        g = s.gamma

        if b is not None and g is not None:
            if s.eps_geo_y is not None and s.eps_n_y is None:
                set_field("eps_n_y", _eps_n_from_geo(s.eps_geo_y, b, g))
            if s.eps_n_y is not None and s.eps_geo_y is None:
                set_field("eps_geo_y", _eps_geo_from_n(s.eps_n_y, b, g))

        if s.sigma_y is not None and s.beta_star_y is not None and s.eps_geo_y is None:
            set_field("eps_geo_y", s.sigma_y**2 / s.beta_star_y)

        if s.sigma_prime_y is not None and s.beta_star_y is not None and s.eps_geo_y is None:
            set_field("eps_geo_y", s.sigma_prime_y**2 * s.beta_star_y)

        if s.eps_geo_y is not None and s.beta_star_y is not None:
            if s.sigma_y is None:
                set_field("sigma_y", _sigma_from_eps_beta(s.eps_geo_y, s.beta_star_y))
            if s.sigma_prime_y is None:
                set_field("sigma_prime_y", _sigma_prime_from_eps_beta(s.eps_geo_y, s.beta_star_y))

        if (s.eps_geo_y is not None and s.beta_star_y is not None
                and s.eta_y is not None and s.delta_p is not None
                and s.sigma_y_total is None):
            set_field("sigma_y_total",
                      _sigma_total(s.eps_geo_y, s.beta_star_y, s.eta_y, s.delta_p))

        if (s.sigma_y_total is not None and s.beta_star_y is not None
                and s.eta_y is not None and s.delta_p is not None
                and s.eps_geo_y is None):
            disp_term = (s.eta_y * s.delta_p)**2
            val = (s.sigma_y_total**2 - disp_term) / s.beta_star_y
            if val > 0:
                set_field("eps_geo_y", val)

    # ------------------------------------------------------------------
    # Pass 5 — Longitudinal
    # ------------------------------------------------------------------
    if s.beta is not None:
        if s.eps_L_eVs is not None and s.eps_L_eVm is None:
            set_field("eps_L_eVm", _eps_L_eVm_from_eVs(s.eps_L_eVs, s.beta))
        if s.eps_L_eVm is not None and s.eps_L_eVs is None:
            set_field("eps_L_eVs", _eps_L_eVs_from_eVm(s.eps_L_eVm, s.beta))
        if s.sigma_z_m is not None and s.sigma_z_t is None:
            set_field("sigma_z_t", _sigma_z_t_from_m(s.sigma_z_m, s.beta))
        if s.sigma_z_t is not None and s.sigma_z_m is None:
            set_field("sigma_z_m", _sigma_z_m_from_t(s.sigma_z_t, s.beta))

        # eL [eV*s] = pi * sigma_z [m] * delta_p * E [eV] / (beta*c)
        if (s.sigma_z_m is not None and s.delta_p is not None
                and s.E_total is not None and s.eps_L_eVs is None):
            E_eV = s.E_total * 1e6
            set_field("eps_L_eVs",
                      math.pi * s.sigma_z_m * s.delta_p * E_eV / (s.beta * C_LIGHT))

        # Reverse: sigma_z from eL + delta + E
        if (s.eps_L_eVs is not None and s.delta_p is not None
                and s.E_total is not None and s.sigma_z_m is None):
            E_eV = s.E_total * 1e6
            set_field("sigma_z_m",
                      s.eps_L_eVs * s.beta * C_LIGHT / (math.pi * s.delta_p * E_eV))

        # Reverse: delta from eL + sigma_z + E
        if (s.eps_L_eVs is not None and s.sigma_z_m is not None
                and s.E_total is not None and s.delta_p is None):
            E_eV = s.E_total * 1e6
            set_field("delta_p",
                      s.eps_L_eVs * s.beta * C_LIGHT / (math.pi * s.sigma_z_m * E_eV))

        # Second pass on unit conversions — catches eps_L computed above
        if s.eps_L_eVs is not None and s.eps_L_eVm is None:
            set_field("eps_L_eVm", _eps_L_eVm_from_eVs(s.eps_L_eVs, s.beta))
        if s.eps_L_eVm is not None and s.eps_L_eVs is None:
            set_field("eps_L_eVs", _eps_L_eVs_from_eVm(s.eps_L_eVm, s.beta))
        # Second pass on bunch length conversions
        if s.sigma_z_m is not None and s.sigma_z_t is None:
            set_field("sigma_z_t", _sigma_z_t_from_m(s.sigma_z_m, s.beta))
        if s.sigma_z_t is not None and s.sigma_z_m is None:
            set_field("sigma_z_m", _sigma_z_m_from_t(s.sigma_z_t, s.beta))

    # ------------------------------------------------------------------
    # Pass 6 — Ring / RF
    # ------------------------------------------------------------------
    circ = s.machine_type in ("circular_proton", "circular_electron", "collider")

    if circ:
        if s.alpha_c is not None:
            if s.gamma_tr is None:
                set_field("gamma_tr", _gamma_tr(s.alpha_c))
            if s.gamma is not None and s.eta_slip is None:
                set_field("eta_slip", _eta_slip(s.alpha_c, s.gamma))
        if s.gamma_tr is not None and s.alpha_c is None:
            ac = 1.0 / s.gamma_tr**2
            set_field("alpha_c", ac)
            if s.gamma is not None and s.eta_slip is None:
                set_field("eta_slip", _eta_slip(ac, s.gamma))

        if s.circumference is not None and s.beta is not None and s.f_rev is None:
            set_field("f_rev", _f_rev(s.circumference, s.beta))
        if s.f_rev is not None and s.beta is not None and s.circumference is None:
            set_field("circumference", s.beta * C_LIGHT / s.f_rev)

        if s.f_rev is not None and s.harmonic is not None and s.f_RF is None:
            set_field("f_RF", _f_RF(s.f_rev, s.harmonic))
        if s.f_RF is not None and s.f_rev is not None and s.harmonic is None:
            set_field("harmonic", round(s.f_RF / s.f_rev))

        if (s.harmonic is not None and s.alpha_c is not None
                and s.V_RF is not None and s.E_total is not None
                and s.phi_s is not None and s.eta_slip is not None
                and s.Q_s is None):
            try:
                set_field("Q_s", _Qs(s.harmonic, s.alpha_c, s.V_RF,
                                     s.E_total, s.phi_s, s.eta_slip))
            except Exception as e:
                conflicts.append(f"Q_s: {e}")

        if (s.harmonic is not None and s.V_RF is not None
                and s.E_total is not None and s.eta_slip is not None
                and s.beta is not None):
            # Energy acceptance (no f_rev needed)
            if s.energy_accept is None:
                try:
                    set_field("energy_accept",
                              _energy_acceptance(s.harmonic, s.V_RF, s.E_total,
                                                 s.eta_slip, s.beta))
                except Exception as e:
                    conflicts.append(f"energy_accept: {e}")
            # Bucket area (needs f_rev)
            if s.bucket_area is None and s.f_rev is not None:
                try:
                    set_field("bucket_area",
                              _bucket_area(s.harmonic, s.V_RF, s.E_total,
                                           s.eta_slip, s.beta, s.f_rev))
                except Exception as e:
                    conflicts.append(f"bucket_area: {e}")

        # Beam current
        if s.N_ppb is not None and s.f_rev is not None and s.I_beam is None:
            set_field("I_beam", _beam_current(s.N_ppb, q, s.f_rev))
        if s.I_beam is not None and s.f_rev is not None and s.N_ppb is None:
            set_field("N_ppb", s.I_beam / (abs(q) * E_CHARGE * s.f_rev))

        # Space charge tune shift
        if (s.N_ppb is not None and s.beta is not None and s.gamma is not None
                and s.bunching_factor is not None):
            r0 = _classical_radius(m0, q)
            if s.eps_geo_x is not None and s.delta_Qx_sc is None:
                try:
                    set_field("delta_Qx_sc",
                              _space_charge_tune_shift(s.N_ppb, r0, s.gamma,
                                                       s.beta, s.eps_geo_x,
                                                       s.bunching_factor))
                except Exception as e:
                    conflicts.append(f"ΔQx_sc: {e}")
            if s.eps_geo_y is not None and s.delta_Qy_sc is None:
                try:
                    set_field("delta_Qy_sc",
                              _space_charge_tune_shift(s.N_ppb, r0, s.gamma,
                                                       s.beta, s.eps_geo_y,
                                                       s.bunching_factor))
                except Exception as e:
                    conflicts.append(f"ΔQy_sc: {e}")

    # ------------------------------------------------------------------
    # Pass 7 — Synchrotron radiation (electron rings only)
    # ------------------------------------------------------------------
    if s.machine_type == "circular_electron":
        rho = s.bending_radius
        E   = s.E_total

        if rho is not None and E is not None:
            if s.U0 is None:
                set_field("U0", _U0_keV(E, rho))
            if s.E_crit is None:
                set_field("E_crit", _E_crit_keV(E, rho))
            if s.sigma_E_sr is None:
                try:
                    set_field("sigma_E_sr", _sigma_E_sr_MeV(E, rho))
                except Exception as e:
                    conflicts.append(f"sigma_E_sr: {e}")

        if s.U0 is not None and s.f_rev is not None and s.E_total is not None:
            T0 = 1.0 / s.f_rev
            if s.tau_x is None:
                set_field("tau_x", _tau_ms(s.E_total, s.U0, T0, J=1.0))
            if s.tau_y is None:
                set_field("tau_y", _tau_ms(s.E_total, s.U0, T0, J=1.0))
            if s.tau_z is None:
                set_field("tau_z", _tau_ms(s.E_total, s.U0, T0, J=2.0))

    # ------------------------------------------------------------------
    # Pass 8 — Luminosity
    # ------------------------------------------------------------------
    if s.machine_type == "collider":
        if (s.N1 is not None and s.N2 is not None
                and s.f_rev is not None
                and s.sigma_x is not None and s.sigma_y is not None
                and s.luminosity is None):
            try:
                set_field("luminosity",
                          _luminosity(
                              s.N1, s.N2, s.f_rev,
                              s.sigma_x, s.sigma_y,
                              crossing_angle_mrad=s.crossing_angle or 0.0,
                              hourglass=s.hourglass,
                              sigma_z=s.sigma_z_m or 0.0,
                              beta_star_x=s.beta_star_x or 1.0,
                          ))
            except Exception as e:
                conflicts.append(f"Luminosity: {e}")

    # Deduplicate conflict messages while preserving order
    seen = set()
    unique_conflicts = []
    for c in conflicts:
        if c not in seen:
            seen.add(c)
            unique_conflicts.append(c)
    return s, unique_conflicts
