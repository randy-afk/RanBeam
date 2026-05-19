# Physics Reference

All equations implemented in `physics.py`. Constants are defined in `models.py`.

---

## Relativistic kinematics

$$
E_\text{total} = KE + m_0 c^2
$$

$$
\gamma = \frac{E_\text{total}}{m_0 c^2}
$$

$$
\beta = \sqrt{1 - \frac{1}{\gamma^2}}
$$

$$
p = \gamma \beta m_0 c \quad [\text{MeV/c}]
$$

$$
B\rho = \frac{p}{q} \quad [\text{T·m}]
$$

---

## Transverse optics

**Normalized and geometric emittance:**

$$
\varepsilon_n = \beta\gamma \cdot \varepsilon_\text{geo}
$$

**RMS beam size at a focus:**

$$
\sigma = \sqrt{\varepsilon_\text{geo} \cdot \beta^*}
$$

**RMS angular divergence:**

$$
\sigma' = \sqrt{\frac{\varepsilon_\text{geo}}{\beta^*}}
$$

**Total beam size including dispersion:**

$$
\sigma_\text{total} = \sqrt{\varepsilon_\text{geo} \cdot \beta^* + (\eta \cdot \delta)^2}
$$

---

## Longitudinal

**Emittance unit conversion:**

$$
\varepsilon_L \,[\text{eV·m}] = \varepsilon_L \,[\text{eV·s}] \cdot \beta c
$$

**Bunch length from bunch duration:**

$$
\sigma_z \,[\text{m}] = \sigma_t \cdot \beta c
$$

---

## Ring / RF

**Revolution frequency:**

$$
f_0 = \frac{\beta c}{C}
$$

**RF frequency:**

$$
f_\text{RF} = h \cdot f_0
$$

**Slip factor:**

$$
\eta = \alpha_c - \frac{1}{\gamma^2}
$$

**Transition gamma:**

$$
\gamma_\text{tr} = \frac{1}{\sqrt{\alpha_c}}
$$

**Synchrotron tune:**

$$
Q_s = \sqrt{\frac{h \,|\eta|\, eV \,|\cos\varphi_s|}{2\pi E}}
$$

where V is the RF voltage in volts and E is the total beam energy in eV.

---

## Synchrotron radiation (electrons)

**Energy loss per turn** (isomagnetic approximation):

$$
U_0 \,[\text{keV}] = C_\gamma \cdot \frac{E^4 \,[\text{GeV}]}{\rho \,[\text{m}]}, \qquad C_\gamma = 8.85 \times 10^{-5} \,\text{m/GeV}^3
$$

**Critical photon energy:**

$$
E_c \,[\text{keV}] = 2.218 \cdot \frac{E^3 \,[\text{GeV}]}{\rho \,[\text{m}]}
$$

**Damping times:**

$$
\tau_x = \frac{2E}{J_x \, U_0} \cdot T_0, \qquad \tau_y = \frac{2E}{J_y \, U_0} \cdot T_0, \qquad \tau_s = \frac{2E}{J_s \, U_0} \cdot T_0
$$

where T₀ = 1/f₀ is the revolution period and Jx, Jy, Js are the damping partition numbers (default: 1, 1, 2).

**Equilibrium energy spread:**

$$
\frac{\sigma_E}{E} = \sqrt{\frac{C_q \gamma^2}{J_s \, \rho}}, \qquad C_q = 3.83 \times 10^{-13} \,\text{m}
$$

---

## Luminosity

**Head-on peak luminosity:**

$$
\mathcal{L} = \frac{N_1 \, N_2 \, f_0}{4\pi \, \sigma_x \, \sigma_y} \quad [\text{cm}^{-2}\text{s}^{-1}]
$$

Geometric reduction factors (hourglass, crossing angle) are not included; this is the ideal head-on limit.

---

## Physical constants used

| Constant | Symbol | Value |
|---|---|---|
| Speed of light | c | 299 792 458 m/s |
| Electron rest energy | m_e c² | 0.510 998 950 MeV |
| Proton rest energy | m_p c² | 938.272 046 MeV |
| Elementary charge | e | 1.602 176 634 × 10⁻¹⁹ C |
| SR constant | Cγ | 8.85 × 10⁻⁵ m/GeV³ |
| Quantum constant | Cq | 3.83 × 10⁻¹³ m |
