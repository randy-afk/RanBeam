"""
tests/test_physics.py — RanBeam
=================================
Unit tests for the physics solver.
Known values cross-checked against PDG and accelerator physics textbooks.

Run with:
    pytest tests/test_physics.py -v
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
import pytest
from core.models import BeamState
from core.physics import solve

TOL = 1e-4   # relative tolerance for all checks


def rel_err(a, b):
    return abs(a - b) / abs(b) if abs(b) > 1e-30 else abs(a - b)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_state(**kwargs) -> BeamState:
    s = BeamState()
    for k, v in kwargs.items():
        setattr(s, k, v)
    return s


# ---------------------------------------------------------------------------
# 1. Relativistic block — Proton at 1 GeV kinetic energy
# ---------------------------------------------------------------------------

class TestRelativisticProton:
    """Proton KE = 1000 MeV → known values."""

    @pytest.fixture(autouse=True)
    def setup(self):
        m0 = 938.27208816   # MeV/c²
        s  = make_state(particle_name="Proton", mass_MeV=m0, charge=1.0, KE=1000.0)
        self.result, self.conflicts = solve(s)
        self.m0 = m0

    def test_no_conflicts(self):
        assert self.conflicts == []

    def test_E_total(self):
        assert rel_err(self.result.E_total, 1938.27208816) < TOL

    def test_gamma(self):
        expected = 1938.27208816 / 938.27208816
        assert rel_err(self.result.gamma, expected) < TOL

    def test_beta(self):
        g = self.result.gamma
        expected = math.sqrt(1 - 1/g**2)
        assert rel_err(self.result.beta, expected) < TOL

    def test_momentum(self):
        E = self.result.E_total
        p = math.sqrt(E**2 - self.m0**2)
        assert rel_err(self.result.momentum, p) < TOL

    def test_Brho(self):
        # Bρ = p [MeV/c] / (299.792458 [MeV/(T·m)])
        p = self.result.momentum
        expected = p / 299.792458
        assert rel_err(self.result.Brho, expected) < TOL

    def test_velocity(self):
        from core.models import C_LIGHT
        expected = self.result.beta * C_LIGHT
        assert rel_err(self.result.velocity, expected) < TOL

    def test_beta_gamma(self):
        expected = self.result.beta * self.result.gamma
        assert rel_err(self.result.beta_gamma, expected) < TOL

    def test_KE_roundtrip(self):
        assert rel_err(self.result.KE, 1000.0) < TOL


class TestRelativisticElectron:
    """Electron at 6 GeV (CEBAF-like)."""

    @pytest.fixture(autouse=True)
    def setup(self):
        m0 = 0.51099895
        s  = make_state(particle_name="Electron", mass_MeV=m0,
                        charge=-1.0, E_total=6000.0)
        self.result, self.conflicts = solve(s)
        self.m0 = m0

    def test_no_conflicts(self):
        assert self.conflicts == []

    def test_KE(self):
        assert rel_err(self.result.KE, 6000.0 - self.m0) < TOL

    def test_gamma(self):
        assert rel_err(self.result.gamma, 6000.0 / self.m0) < TOL

    def test_ultra_relativistic_beta(self):
        # At 6 GeV electron, β ≈ 1 - tiny correction
        assert self.result.beta > 0.9999999


class TestRelativisticFromBrho:
    """Enter Bρ, recover proton energy."""

    def test_Brho_to_momentum(self):
        m0 = 938.27208816
        # Proton at KE=1 GeV → Bρ known
        s1 = make_state(particle_name="Proton", mass_MeV=m0, charge=1.0, KE=1000.0)
        r1, _ = solve(s1)
        brho = r1.Brho

        # Now enter only Bρ
        s2 = make_state(particle_name="Proton", mass_MeV=m0, charge=1.0, Brho=brho)
        r2, conflicts = solve(s2)
        assert conflicts == []
        assert rel_err(r2.KE, 1000.0) < TOL

    def test_momentum_to_energy(self):
        m0 = 938.27208816
        s1 = make_state(particle_name="Proton", mass_MeV=m0, charge=1.0, KE=500.0)
        r1, _ = solve(s1)
        p = r1.momentum

        s2 = make_state(particle_name="Proton", mass_MeV=m0, charge=1.0, momentum=p)
        r2, conflicts = solve(s2)
        assert conflicts == []
        assert rel_err(r2.KE, 500.0) < TOL


# ---------------------------------------------------------------------------
# 2. Transverse block
# ---------------------------------------------------------------------------

class TestTransverseForwardSolve:
    """Enter εₙ + βγ → εgeo, then σ and σ'."""

    @pytest.fixture(autouse=True)
    def setup(self):
        m0 = 938.27208816
        s = make_state(
            particle_name="Proton", mass_MeV=m0, charge=1.0,
            KE=1000.0,
            eps_n_x=1e-6,    # 1 μm·rad normalised
            beta_star_x=10.0, # 10 m
        )
        self.result, self.conflicts = solve(s)

    def test_no_conflicts(self):
        assert self.conflicts == []

    def test_eps_geo(self):
        bg = self.result.beta_gamma
        expected = 1e-6 / bg
        assert rel_err(self.result.eps_geo_x, expected) < TOL

    def test_sigma(self):
        eg = self.result.eps_geo_x
        expected = math.sqrt(eg * 10.0)
        assert rel_err(self.result.sigma_x, expected) < TOL

    def test_sigma_prime(self):
        eg = self.result.eps_geo_x
        expected = math.sqrt(eg / 10.0)
        assert rel_err(self.result.sigma_prime_x, expected) < TOL


class TestTransverseReverseSolve:
    """Enter σ + β* → εgeo → εₙ."""

    def test_sigma_betastar_to_eps(self):
        m0 = 938.27208816
        sigma = 1e-3   # 1 mm
        beta_star = 5.0
        eps_geo_expected = sigma**2 / beta_star

        s = make_state(
            particle_name="Proton", mass_MeV=m0, charge=1.0,
            KE=1000.0,
            sigma_x=sigma,
            beta_star_x=beta_star,
        )
        r, conflicts = solve(s)
        assert conflicts == []
        assert rel_err(r.eps_geo_x, eps_geo_expected) < TOL
        # Also check eps_n derived
        bg = r.beta_gamma
        assert rel_err(r.eps_n_x, eps_geo_expected * bg) < TOL


class TestDispersiveBeamSize:
    """σ_total includes dispersion term."""

    def test_total_beam_size(self):
        m0 = 938.27208816
        eps_geo = 1e-9
        beta_star = 1.0
        eta = 0.5
        delta = 1e-3

        s = make_state(
            particle_name="Proton", mass_MeV=m0, charge=1.0,
            KE=1000.0,
            eps_geo_x=eps_geo, beta_star_x=beta_star,
            eta_x=eta, delta_p=delta,
        )
        r, _ = solve(s)
        expected = math.sqrt(eps_geo * beta_star + (eta * delta)**2)
        assert rel_err(r.sigma_x_total, expected) < TOL


# ---------------------------------------------------------------------------
# 3. Longitudinal block
# ---------------------------------------------------------------------------

class TestLongitudinal:
    """eV·s ↔ eV·m conversion and bunch length."""

    def test_eps_L_conversion(self):
        from core.models import C_LIGHT
        m0 = 938.27208816
        s = make_state(
            particle_name="Proton", mass_MeV=m0, charge=1.0,
            KE=1000.0, eps_L_eVs=1e-3,
        )
        r, conflicts = solve(s)
        assert conflicts == []
        expected_eVm = 1e-3 * r.beta * C_LIGHT
        assert rel_err(r.eps_L_eVm, expected_eVm) < TOL

    def test_bunch_length_conversion(self):
        from core.models import C_LIGHT
        m0 = 938.27208816
        sigma_t = 1e-9   # 1 ns
        s = make_state(
            particle_name="Proton", mass_MeV=m0, charge=1.0,
            KE=1000.0, sigma_z_t=sigma_t,
        )
        r, conflicts = solve(s)
        assert conflicts == []
        expected_m = sigma_t * r.beta * C_LIGHT
        assert rel_err(r.sigma_z_m, expected_m) < TOL


# ---------------------------------------------------------------------------
# 4. Ring / RF block
# ---------------------------------------------------------------------------

class TestRingRF:
    """Revolution frequency and RF derived quantities."""

    @pytest.fixture(autouse=True)
    def setup(self):
        m0 = 938.27208816
        s = make_state(
            particle_name="Proton", mass_MeV=m0, charge=1.0,
            machine_type="circular_proton",
            KE=1000.0,
            circumference=6911.0,  # ~RHIC circumference
            harmonic=360,
            alpha_c=8.5e-4,
        )
        self.result, self.conflicts = solve(s)

    def test_no_conflicts(self):
        assert self.conflicts == []

    def test_f_rev(self):
        from core.models import C_LIGHT
        expected = self.result.beta * C_LIGHT / 6911.0
        assert rel_err(self.result.f_rev, expected) < TOL

    def test_f_RF(self):
        expected = 360 * self.result.f_rev
        assert rel_err(self.result.f_RF, expected) < TOL

    def test_gamma_tr(self):
        expected = 1.0 / math.sqrt(8.5e-4)
        assert rel_err(self.result.gamma_tr, expected) < TOL

    def test_eta_slip(self):
        g = self.result.gamma
        expected = 8.5e-4 - 1.0/g**2
        assert rel_err(self.result.eta_slip, expected) < TOL

    def test_circumference_reverse(self):
        """Enter f_rev → get circumference back."""
        from core.models import C_LIGHT
        m0 = 938.27208816
        f0 = self.result.f_rev
        s = make_state(
            particle_name="Proton", mass_MeV=m0, charge=1.0,
            machine_type="circular_proton",
            KE=1000.0, f_rev=f0,
        )
        r, _ = solve(s)
        assert rel_err(r.circumference, 6911.0) < TOL


# ---------------------------------------------------------------------------
# 5. Synchrotron radiation block
# ---------------------------------------------------------------------------

class TestSynchrotronRadiation:
    """6 GeV electron ring, ρ = 10 m."""

    @pytest.fixture(autouse=True)
    def setup(self):
        m0 = 0.51099895
        s = make_state(
            particle_name="Electron", mass_MeV=m0, charge=-1.0,
            machine_type="circular_electron",
            E_total=6000.0,
            bending_radius=10.0,
            circumference=500.0,
        )
        self.result, self.conflicts = solve(s)

    def test_no_conflicts(self):
        assert self.conflicts == []

    def test_U0(self):
        # U0 = 8.85e-5 * (6)^4 / 10 * 1e3 keV
        E_GeV = 6.0
        expected = 8.85e-5 * E_GeV**4 / 10.0 * 1e3
        assert rel_err(self.result.U0, expected) < TOL

    def test_E_crit(self):
        E_GeV = 6.0
        expected = 2.218 * E_GeV**3 / 10.0
        assert rel_err(self.result.E_crit, expected) < TOL

    def test_sigma_E_sr(self):
        assert self.result.sigma_E_sr is not None
        assert self.result.sigma_E_sr > 0

    def test_damping_times_positive(self):
        assert self.result.tau_x > 0
        assert self.result.tau_y > 0
        assert self.result.tau_z > 0

    def test_tau_z_half_tau_x(self):
        # Jz = 2*Jx so τz ≈ τx/2
        assert rel_err(self.result.tau_z, self.result.tau_x / 2.0) < TOL


# ---------------------------------------------------------------------------
# 6. Conflict detection
# ---------------------------------------------------------------------------

class TestConflictDetection:
    """Entering inconsistent values should produce conflict messages."""

    def test_KE_and_E_total_inconsistent(self):
        m0 = 938.27208816
        s = make_state(
            particle_name="Proton", mass_MeV=m0, charge=1.0,
            KE=1000.0,
            E_total=500.0,   # wrong — should be 1938.27
        )
        _, conflicts = solve(s)
        assert len(conflicts) > 0

    def test_consistent_inputs_no_conflict(self):
        m0 = 938.27208816
        s = make_state(
            particle_name="Proton", mass_MeV=m0, charge=1.0,
            KE=1000.0,
            E_total=1938.27208816,   # correct
        )
        _, conflicts = solve(s)
        assert conflicts == []
