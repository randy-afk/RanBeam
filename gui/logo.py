"""
logo.py — RanBeam
==================
Generates the RanBeam logo as PNG files using matplotlib.
No Qt dependency — pure matplotlib + numpy.

Outputs:
    logo_gui.png   — 140×45 px  (header banner in the GUI)
    logo_docs.png  — 420×140 px (MkDocs site, 3× scale)

Usage:
    python logo.py              # writes both files next to this script
    from logo import make_logo  # returns (gui_path, docs_path)

Design:
    A tight laser beam enters from the left, hits a circular target reticle
    at center, then many curved particle tracks scatter outward — like a
    collision event display. "RanBeam" text sits to the right.
"""

from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.colors as mcolors
from matplotlib.collections import LineCollection
from matplotlib.patheffects import withStroke

# ---------------------------------------------------------------------------
# Colour palette (matches RanBeam GUI)
# ---------------------------------------------------------------------------
BG      = "#163A2C"
BEAM    = "#fda769"
BEAM2   = "#fd8c3a"
FG      = "#EEF5F2"
FG_DIM  = "#8AB0A6"
TARGET  = "#fda769"
FLASH   = "#ffffff"

# Scatter track colours — cycle through blue, green, orange, white
TRACK_COLORS = [
    "#74c0fc",  # light blue
    "#69db7c",  # light green
    "#fda769",  # orange
    "#f2f2f7",  # white
]


def _curved_track(ax, x0, y0, angle_deg, length, curve, color, lw, alpha, zorder=3):
    """
    Draw a single fading curved scatter track starting at (x0, y0).
    Uses a quadratic Bezier curve — curve > 0 bends left of travel direction.
    """
    angle = np.radians(angle_deg)
    x1 = x0 + length * np.cos(angle)
    y1 = y0 + length * np.sin(angle)
    # Control point offset perpendicular to travel
    cx = (x0 + x1) / 2 - curve * np.sin(angle)
    cy = (y0 + y1) / 2 + curve * np.cos(angle)

    t = np.linspace(0, 1, 80)
    x = (1 - t)**2 * x0 + 2 * (1 - t) * t * cx + t**2 * x1
    y = (1 - t)**2 * y0 + 2 * (1 - t) * t * cy + t**2 * y1

    points = np.array([x, y]).T.reshape(-1, 1, 2)
    segs   = np.concatenate([points[:-1], points[1:]], axis=1)

    rgba = np.array(mcolors.to_rgba(color))
    colors_arr = np.tile(rgba, (len(segs), 1))
    colors_arr[:, 3] = np.linspace(alpha, 0.0, len(segs))

    lc = LineCollection(segs, linewidths=lw, zorder=zorder)
    lc.set_color(colors_arr)
    ax.add_collection(lc)


def _draw_logo(ax: plt.Axes, title_fontsize: float, sub_fontsize: float) -> None:
    ax.set_xlim(0, 11)
    ax.set_ylim(-1.1, 1.1)
    ax.set_aspect("auto")
    ax.axis("off")

    impact_x = 3.8
    impact_y = 0.0

    # --- Incoming laser beam ------------------------------------------------
    ax.plot([0.0, impact_x], [0, 0],
            color=BEAM, linewidth=6, alpha=0.08, solid_capstyle="round", zorder=1)
    ax.plot([0.0, impact_x], [0, 0],
            color=BEAM, linewidth=3, alpha=0.20, solid_capstyle="round", zorder=1)
    ax.plot([0.0, impact_x], [0, 0],
            color=BEAM2, linewidth=1.4, solid_capstyle="round", zorder=2)
    # Arrowhead
    ax.annotate("", xy=(impact_x - 0.05, 0), xytext=(impact_x - 0.9, 0),
                arrowprops=dict(arrowstyle="-|>", color=BEAM,
                                lw=1.2, mutation_scale=9),
                zorder=3)

    # --- Target cube --------------------------------------------------------
    s = 0.28   # half-size of cube face
    # Front face
    ax.add_patch(mpatches.FancyBboxPatch(
        (impact_x - s, impact_y - s), 2*s, 2*s,
        boxstyle="square,pad=0", linewidth=1.2,
        edgecolor=TARGET, facecolor=BEAM2, alpha=0.5, zorder=4,
    ))
    # Top face (parallelogram effect)
    offset = 0.12
    top_x = [impact_x - s, impact_x + s, impact_x + s + offset, impact_x - s + offset, impact_x - s]
    top_y = [impact_y + s, impact_y + s, impact_y + s + offset, impact_y + s + offset, impact_y + s]
    ax.fill(top_x, top_y, color=TARGET, alpha=0.35, zorder=4)
    ax.plot(top_x, top_y, color=TARGET, linewidth=1.0, alpha=0.7, zorder=4)
    # Right face
    right_x = [impact_x + s, impact_x + s + offset, impact_x + s + offset, impact_x + s, impact_x + s]
    right_y = [impact_y - s, impact_y - s + offset, impact_y + s + offset, impact_y + s, impact_y - s]
    ax.fill(right_x, right_y, color=BEAM, alpha=0.25, zorder=4)
    ax.plot(right_x, right_y, color=TARGET, linewidth=1.0, alpha=0.7, zorder=4)

    # --- Impact flash -------------------------------------------------------
    ax.plot(impact_x, impact_y, "o",
            color=BEAM, markersize=11, alpha=0.20, zorder=5, markeredgewidth=0)
    ax.plot(impact_x, impact_y, "o",
            color=FLASH, markersize=4.5, zorder=6, markeredgewidth=0)

    # --- Scatter tracks -----------------------------------------------------
    # (angle_deg, length, curve_strength, linewidth, alpha)
    tracks = [
        (  18,  5.8,  0.22, 1.1, 0.82),
        ( -18,  5.8, -0.22, 1.1, 0.82),
        (  38,  5.2,  0.38, 1.0, 0.75),
        ( -38,  5.2, -0.38, 1.0, 0.75),
        (  60,  4.5,  0.42, 0.9, 0.68),
        ( -60,  4.5, -0.42, 0.9, 0.68),
        (  82,  3.6,  0.30, 0.8, 0.62),
        ( -82,  3.6, -0.30, 0.8, 0.62),
        ( 105,  3.0,  0.18, 0.8, 0.55),
        (-105,  3.0, -0.18, 0.8, 0.55),
        ( 128,  3.4, -0.25, 0.9, 0.58),
        (-128,  3.4,  0.25, 0.9, 0.58),
        ( 152,  4.2, -0.30, 1.0, 0.65),
        (-152,  4.2,  0.30, 1.0, 0.65),
        ( 170,  4.8, -0.12, 1.0, 0.70),
        (-170,  4.8,  0.12, 1.0, 0.70),
    ]

    for i, (angle, length, curve, lw, alpha) in enumerate(tracks):
        color = TRACK_COLORS[i % len(TRACK_COLORS)]
        _curved_track(ax, impact_x, impact_y, angle, length, curve,
                      color=color, lw=lw, alpha=alpha, zorder=3)

    # --- Text ---------------------------------------------------------------
    # Draw "Ran" then measure its rendered width to place "Beam" tight after it.
    text_x = 5.3

    t_ran = ax.text(text_x, 0.13, "Ran",
                    color=FG, fontsize=title_fontsize,
                    fontweight="bold", va="center", ha="left",
                    fontfamily="monospace",
                    path_effects=[withStroke(linewidth=2, foreground=BG)],
                    zorder=10)

    # Force a draw so we can measure the bounding box
    fig = ax.get_figure()
    fig.canvas.draw()
    try:
        renderer = fig.canvas.get_renderer()
        bb = t_ran.get_window_extent(renderer=renderer)
        # Convert pixel width back to data coordinates
        x0_disp, _ = ax.transData.transform((text_x, 0))
        beam_x_disp = x0_disp + bb.width
        beam_x, _ = ax.transData.inverted().transform((beam_x_disp, 0))
    except Exception:
        # Fallback: monospace chars are ~0.6× fontsize in points, scale to data
        beam_x = text_x + 3 * (title_fontsize * 0.085)

    ax.text(beam_x, 0.13, "Beam",
            color=BEAM, fontsize=title_fontsize,
            fontweight="bold", va="center", ha="left",
            fontfamily="monospace",
            path_effects=[withStroke(linewidth=2, foreground=BG)],
            zorder=10)

    ax.text(text_x, -0.42,
            "Beam Parameter Calculator",
            color=FG, fontsize=sub_fontsize * 1.2,
            va="center", ha="left", fontfamily="monospace",
            path_effects=[withStroke(linewidth=1.5, foreground=BG)],
            zorder=10)


def make_logo(
    out_dir: str | None = None,
    gui_name:  str = "logo_gui.png",
    docs_name: str = "logo_docs.png",
) -> tuple[str, str]:
    """
    Generate both logo sizes.

    Parameters
    ----------
    out_dir : str, optional
        Output directory. Defaults to the directory containing this file
        (i.e. gui/ when logo.py lives there).

    Returns
    -------
    (gui_path, docs_path) : tuple of absolute paths
    """
    if out_dir is None:
        out_dir = os.path.dirname(os.path.abspath(__file__))

    results = []
    for (w_px, h_px, fname, title_fs, sub_fs) in [
        (420, 100, gui_name,  16.0, 8.0),   # GUI header — larger and more legible
        (420, 140, docs_name, 9.5, 4.8),    # MkDocs
    ]:
        dpi   = 100
        fig, ax = plt.subplots(figsize=(w_px / dpi, h_px / dpi), dpi=dpi)
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(BG)
        _draw_logo(ax, title_fontsize=title_fs, sub_fontsize=sub_fs)
        path = os.path.join(out_dir, fname)
        fig.savefig(path, dpi=dpi, transparent=True)
        plt.close(fig)
        results.append(os.path.abspath(path))

    return results[0], results[1]


if __name__ == "__main__":
    gui_path, docs_path = make_logo()
    print(f"GUI  logo → {gui_path}")
    print(f"Docs logo → {docs_path}")
