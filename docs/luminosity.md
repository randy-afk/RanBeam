# Luminosity

RanBeam computes head-on luminosity for two colliding beams. Because the two beams are configured separately, the workflow uses the **save / load** feature to bring both beam states into the Luminosity tab simultaneously.

---

## Formula

$$
\mathcal{L} = \frac{N_1 \, N_2 \, f_0}{4\pi \, \sigma_x \, \sigma_y}
$$

where:

| Symbol | Description |
|---|---|
| N₁, N₂ | Bunch populations for beam 1 and beam 2 |
| f₀ | Revolution frequency (assumed equal for both beams in a storage ring) |
| σx, σy | RMS beam sizes at the IP, combined in quadrature if the two beams differ |

Units: L in cm⁻²s⁻¹.

---

## Workflow

### Step 1 — Configure Beam 1

1. Select machine type **Collider**.
2. Set particle species, energy, and all relevant optics parameters for Beam 1.
3. Go to **File → Save State** and save as `beam1.json`.

### Step 2 — Configure Beam 2

1. Change particle species and energy to Beam 2 values (the machine type stays as Collider).
2. Enter Beam 2 optics parameters.
3. Go to **File → Save State** and save as `beam2.json`.

### Step 3 — Compute luminosity

1. Go to the **Luminosity** tab.
2. Click **Load Beam 1** and open `beam1.json`.
3. Click **Load Beam 2** and open `beam2.json`.
4. The peak luminosity L is computed and displayed immediately.

!!! note "Beam size convention"
    σx and σy used in the luminosity formula are the geometric RMS sizes at the interaction point, computed from the geometric emittance and β* of each beam. For asymmetric colliders the sizes are combined assuming round or flat beam geometry as appropriate.

---

## Tips

- To scan luminosity vs. β*, lock all other parameters, then vary β* for one or both beams and re-save.
- The saved JSON files are plain text — you can edit bunch population N directly in any text editor if needed.
- For a symmetric collider (same beam on both sides), save once and load the same file as both Beam 1 and Beam 2.
