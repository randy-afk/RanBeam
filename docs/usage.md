# Usage

## Workflow overview

1. Select a **particle type** from the preset dropdown (electron, proton, ion, or custom mass/charge).
2. Select a **machine type** to unlock the relevant parameter tabs.
3. Enter any known values into the fields. Order does not matter.
4. The solver propagates automatically — all computable quantities fill in immediately.
5. Optionally **lock** fields you want to hold fixed while exploring others.
6. **Save** the current state to JSON for later use or for luminosity calculations.

---

## The solver

The solver in `physics.py` implements a dependency graph over all beam parameters. Each parameter is a node; each physics relation is a directed edge. When you enter a value, the solver:

1. Marks the field as **user-specified**.
2. Traverses the graph to find all nodes reachable from the new value.
3. Computes each reachable node and writes the result back to the GUI.

If two user-specified values are mathematically inconsistent (e.g. β > 1, or a normalized emittance that contradicts the geometric emittance at the given energy), both fields are highlighted in **red** and a conflict message is shown in the status bar. No silent overrides — you always know when something is wrong.

---

## Locking fields

Click the **lock icon** on any field to pin its value. Locked fields are excluded from solver overwrites, so you can:

- Fix β* and explore how emittance affects beam size.
- Fix the beam size and back-calculate the required emittance.
- Fix U₀ and see which ring parameters would achieve it.

Unlock by clicking the icon again.

---

## Saving and loading states

Go to **File → Save State** to write the current beam state to a `.json` file. Go to **File → Load State** to restore a previously saved state.

The JSON format is human-readable and contains all parameter values plus the particle and machine type.

!!! tip "Two-beam luminosity"
    Save Beam 1, then configure Beam 2 and save it separately. See the [Luminosity](luminosity.md) page for how to compute head-on luminosity from two saved states.

---

## Conflict detection

Conflicts appear as:

- **Red field outlines** on the two conflicting inputs.
- A status bar message identifying which relation was violated.

To resolve: unlock one of the conflicting fields and let the solver recompute it, or clear the value and re-enter a consistent one.
