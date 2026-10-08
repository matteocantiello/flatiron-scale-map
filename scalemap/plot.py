"""Render the Flatiron scale map.

``render(layout)`` builds a Matplotlib ``Figure`` for one layout from
``scalemap.layouts`` and returns it together with a small diagnostics dict.
It uses the object-oriented API (no pyplot), so it is safe to call from
scripts, notebooks and tests without touching global state.

Drawing order, back to front:

1. major gridlines (allowed half only, covered elsewhere by the field)
2. the excluded field below t = L/c, a flat warm gray
3. the CCM methods band along the bottom
4. region washes, largest area first
5. region outlines, all after all washes, so every edge stays crisp
6. the t = L/c line, labels and the legend
"""

from __future__ import annotations

import warnings

import numpy as np
from matplotlib import rc_context
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.colors import to_rgba
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Rectangle
from matplotlib.ticker import NullLocator

from . import fonts
from .data import LOG10_C, Center, load_centers, load_extensions, load_landmarks
from .layouts import LAYOUTS

# Plot window in log10 units.
XMIN, XMAX, YMIN, YMAX = -14, 28, -20, 19
BAND_TOP = -19.0  # top of the CCM methods band

# Neutral palette. Center hues come from data/centers.toml.
BG = "#FFFFFF"       # page
INK = "#1b1b19"      # titles, axis labels
BODY = "#2e2d2a"     # legend names
SUB = "#64635e"      # subtitle
MUTED = "#8a8882"    # landmarks, footnote
GRID = "#efeeea"     # major gridlines
FIELD = "#f7f6f2"    # excluded half, t < L/c
AXIS = "#3b3a37"     # left and bottom spines, ticks
FRAME = "#c9c7c0"    # top and right spines (reference axes)
LINE = "#3b3a37"     # t = L/c

TITLE = "Scales of interest across the Flatiron Institute"
SUBTITLE = "Characteristic length and time of the systems each center studies"
FOOTNOTE = "Regions are envelopes of each center’s core range, clipped at t = L/c."
CCM_CAPTION = "CCM  —  methods used at every scale"


def _rc() -> dict:
    return {
        "font.family": fonts.SANS,
        "mathtext.fontset": "custom",
        "mathtext.rm": fonts.SANS,
        "mathtext.it": f"{fonts.SERIF}:italic",
        "mathtext.bf": f"{fonts.SANS}:bold",
        "axes.unicode_minus": True,
        "pdf.fonttype": 42,  # embed TrueType so text stays editable in the PDF
        "xtick.direction": "out",
        "ytick.direction": "out",
    }


def render(layout: str | dict = "slide", *, centers: list[Center] | None = None,
           landmarks: dict | None = None, extensions: bool = False):
    """Build the figure for one layout.

    Parameters
    ----------
    layout : name in ``scalemap.layouts.LAYOUTS`` or a layout dict
    centers, landmarks : override the data read from ``data/``
    extensions : also draw the edge cases from ``data/extensions.toml`` as
        dashed outlines

    Returns
    -------
    (Figure, dict) where the dict holds diagnostics, for example
    ``legend_clear``: whether the legend lies fully below the t = L/c line.
    """
    cfg = LAYOUTS[layout] if isinstance(layout, str) else layout
    centers = centers or load_centers()
    landmarks = landmarks or load_landmarks()
    fonts.register()
    with rc_context(_rc()):
        return _draw(cfg, centers, landmarks, load_extensions() if extensions else [])


def _draw(cfg, centers, landmarks, extensions):
    W, H = cfg["size"]
    fs, lw = cfg["fs"], cfg["lw"]
    fig = Figure(figsize=(W, H), dpi=cfg["dpi"], facecolor=BG)
    FigureCanvasAgg(fig)
    L, R, B, T = cfg["margins"]
    ax = fig.add_axes([L / W, B / H, 1 - (L + R) / W, 1 - (B + T) / H], facecolor=BG)
    ax.set_xlim(XMIN, XMAX)
    ax.set_ylim(YMIN, YMAX)
    ax.set_axisbelow(True)
    by_id = {c.id: c for c in centers}
    regions = [c for c in centers if c.is_region]
    methods = [c for c in centers if not c.is_region]

    _axes(ax, fs, lw)
    _landmarks(ax, landmarks, fs, lw)

    # excluded half: a quiet field that also hides the grid there
    ax.add_patch(Polygon([(YMIN + LOG10_C, YMIN), (XMAX, YMIN), (XMAX, YMAX), (YMAX + LOG10_C, YMAX)],
                         closed=True, facecolor=FIELD, edgecolor="none", zorder=0.8))

    for m in methods:  # one methods band (CCM)
        ax.axhspan(YMIN, BAND_TOP, color=m.color, alpha=m.wash_alpha, lw=0, zorder=1)
        ax.plot([XMIN, XMAX], [BAND_TOP] * 2, color=m.color, lw=lw * 0.9, zorder=1.5,
                solid_capstyle="butt")
        yb = ax.transData.transform((0, BAND_TOP))[1] + fs["ccm"] * 0.45 * fig.dpi / 72
        ax.text(cfg["ccm_x"], ax.transData.inverted().transform((0, yb))[1], CCM_CAPTION,
                ha="left", va="baseline", fontsize=fs["ccm"], color=m.label_color, zorder=6)

    # washes, largest first, then every outline on top
    back_to_front = sorted(regions, key=lambda c: c.area, reverse=True)
    for i, c in enumerate(back_to_front):
        ax.add_patch(Polygon(c.polygon, closed=True, facecolor=c.color, alpha=c.wash_alpha,
                             lw=0, zorder=2 + i * 0.01))
    for i, c in enumerate(back_to_front):
        ax.add_patch(Polygon(c.polygon, closed=True, facecolor="none", edgecolor=c.color,
                             lw=lw * 1.15, joinstyle="miter", zorder=3 + i * 0.01))
    for e in extensions:
        ax.add_patch(Polygon(e.polygon, closed=True, facecolor="none", edgecolor=by_id[e.center].color,
                             lw=lw * 1.0, ls=(0, (4, 3)), zorder=3.5))

    _light_line(fig, ax, cfg, fs, lw)
    _region_labels(ax, cfg, by_id, fs, lw)
    _title_block(fig, ax, cfg, fs)
    diag = _legend(fig, ax, cfg, centers)
    return fig, diag


# --------------------------------------------------------------------------- pieces


def _axes(ax, fs, lw):
    xt, yt = np.arange(-12, 25, 4), np.arange(-20, 16, 5)
    ax.set_xticks(xt)
    ax.set_yticks(yt)
    ax.set_xticks(np.arange(XMIN, XMAX + 1), minor=True)  # one tick per decade
    ax.set_yticks(np.arange(YMIN, YMAX + 1), minor=True)
    ax.set_xticklabels([rf"$10^{{{v}}}$" for v in xt])
    ax.set_yticklabels([rf"$10^{{{v}}}$" for v in yt])
    ax.tick_params(which="major", length=fs["tick"] * 0.42, width=lw * 0.8, color=AXIS,
                   labelsize=fs["tick"], labelcolor=AXIS, pad=fs["tick"] * 0.42)
    ax.tick_params(which="minor", length=fs["tick"] * 0.22, width=lw * 0.6, color=AXIS)
    ax.grid(True, which="major", color=GRID, lw=lw * 0.8, zorder=0)
    for s in ("left", "bottom"):
        ax.spines[s].set(color=AXIS, linewidth=lw * 0.8)
    for s in ("top", "right"):
        ax.spines[s].set(color=FRAME, linewidth=lw * 0.7)
    pad = fs["axlabel"] * 0.55
    ax.set_xlabel("Characteristic length  [m]", fontsize=fs["axlabel"], color=INK, labelpad=pad)
    ax.set_ylabel("Characteristic time  [s]", fontsize=fs["axlabel"], color=INK, labelpad=pad)


def _landmarks(ax, landmarks, fs, lw):
    style = dict(fontsize=fs["land"], color=MUTED, family=fonts.SERIF, style="italic",
                 linespacing=0.95)
    top = ax.secondary_xaxis("top")
    top.set_xticks([m.log10 for m in landmarks["length"]])
    top.set_xticklabels([m.label for m in landmarks["length"]], **style)
    top.xaxis.set_minor_locator(NullLocator())
    top.tick_params(length=fs["tick"] * 0.32, width=lw * 0.6, color=FRAME, pad=fs["land"] * 0.25)
    top.spines["top"].set(color=FRAME, linewidth=lw * 0.7)
    right = ax.secondary_yaxis("right")
    right.set_yticks([m.log10 for m in landmarks["time"]])
    right.set_yticklabels([m.label for m in landmarks["time"]], **style)
    right.yaxis.set_minor_locator(NullLocator())
    right.tick_params(length=fs["tick"] * 0.32, width=lw * 0.6, color=FRAME, pad=fs["land"] * 0.35)
    right.spines["right"].set(color=FRAME, linewidth=lw * 0.7)


def _light_line(fig, ax, cfg, fs, lw):
    ax.plot([YMIN + LOG10_C, YMAX + LOG10_C], [YMIN, YMAX], color=LINE, lw=lw * 1.05,
            zorder=4, solid_capstyle="butt")
    # label rotated to the line's on-screen slope, offset perpendicular to it
    p0 = ax.transData.transform((0, -LOG10_C))
    p1 = ax.transData.transform((10, 10 - LOG10_C))
    d = (p1 - p0) / np.hypot(*(p1 - p0))
    normal = np.array([-d[1], d[0]])
    x = cfg["tlc_x"]
    at = ax.transData.transform((x, x - LOG10_C)) + normal * fs["tlc"] * 0.62 * fig.dpi / 72
    fx, fy = fig.transFigure.inverted().transform(at)
    fig.text(fx, fy, "t = L/c", rotation=np.degrees(np.arctan2(d[1], d[0])),
             rotation_mode="anchor", ha="center", va="center", fontsize=fs["tlc"],
             family=fonts.SERIF, style="italic", color=LINE, zorder=7)


def _region_labels(ax, cfg, by_id, fs, lw):
    for cid, (x, y) in cfg["labels"].items():
        ax.text(x, y, cid, color=by_id[cid].label_color, fontsize=fs["region"],
                fontweight="bold", ha="center", va="center", zorder=8)
    # CCQ is too small for an inside label: set it to the left of its region
    q = by_id["CCQ"]
    qx, qy = cfg["ccq_label"]
    x_edge = q.length[0]
    ax.text(qx, qy, "CCQ", color=q.label_color, ha="right", va="center", fontsize=fs["region"],
            fontweight="bold", zorder=8, bbox=dict(fc=BG, ec="none", pad=fs["region"] * 0.08))
    if cfg["ccq_leader"] is not None:
        ax.plot([qx + cfg["ccq_leader"], x_edge], [qy, qy], color=q.label_color, lw=lw * 0.8,
                zorder=8, solid_capstyle="butt")
        ax.plot([x_edge], [qy], marker="o", ms=fs["region"] * 0.17, color=q.label_color,
                mec=BG, mew=lw * 0.8, zorder=9)


def _title_block(fig, ax, cfg, fs):
    W, H = cfg["size"]
    fig.canvas.draw()  # resolve the y-label position first
    x = ax.yaxis.label.get_window_extent(fig.canvas.get_renderer()).x0 / fig.bbox.width
    if cfg.get("title"):
        fig.text(x, 1 - cfg["ty"] / H, TITLE, fontsize=fs["title"], family=fonts.SERIF,
                 color=INK, ha="left", va="baseline")
        fig.text(x, 1 - cfg["sy"] / H, SUBTITLE, fontsize=fs["sub"], color=SUB,
                 ha="left", va="baseline")
    if cfg.get("foot"):
        fig.text(x, cfg["fy"] / H, FOOTNOTE, fontsize=fs["foot"], color=MUTED,
                 ha="left", va="baseline")


def _legend(fig, ax, cfg, centers) -> dict:
    """A typeset legend in the empty lower-right half.

    Three columns (swatch, acronym, name), right-aligned to the axes and
    resting just above the CCM band. Text widths are measured, so the block
    adapts to any font or name length. Returns diagnostics.
    """
    fs, lw = cfg["fs"], cfg["lw"]
    size = fs["legend"]
    r = fig.canvas.get_renderer()
    px = fig.dpi / 72.0
    FW, FH = fig.bbox.width, fig.bbox.height
    name_of = (lambda c: c.name) if cfg["names"] == "full" else (lambda c: c.short_name)
    regions = [c for c in centers if c.is_region]
    methods = [c for c in centers if not c.is_region]
    rows = [("region", c, c.id, name_of(c)) for c in regions]
    rows += [("band", m, m.id, name_of(m)) for m in methods]
    rows += [("line", None, "t = L/c", "light-crossing time")]
    group_break = len(regions)

    acr_kw = dict(fontsize=size, fontweight="bold")
    tlc_kw = dict(fontsize=size * 1.1, family=fonts.SERIF, style="italic")
    name_kw = dict(fontsize=size)

    def width(s, **kw):
        t = fig.text(0, 0, s, **kw)
        w = t.get_window_extent(r).width
        t.remove()
        return w

    w_acr = max([width(a, **acr_kw) for k, _, a, _ in rows if k != "line"] + [width("t = L/c", **tlc_kw)])
    w_name = max(width(n, **name_kw) for *_, n in rows)

    sw = size * 0.95 * px                   # swatch side
    g1, g2 = size * 0.75 * px, size * 0.9 * px  # column gaps
    pitch = size * 1.72 * px                # row pitch
    gap = size * 0.75 * px                  # extra space before CCM
    pad = size * 1.0 * px
    w = sw + g1 + w_acr + g2 + w_name
    h = (len(rows) - 1) * pitch + gap + sw

    right = ax.get_window_extent(r).x1 - cfg["legend_right"] * px
    bottom = ax.transData.transform((0, BAND_TOP))[1] + pad + cfg["legend_floor"] * px
    left, top = right - w, bottom + h

    cx, cy = ax.transData.inverted().transform((left - pad, top + pad))
    clear = bool(cy < cx - LOG10_C - 0.8)
    if not clear:
        warnings.warn(f"{cfg['name']}: legend reaches above the t = L/c line; "
                      "shorten names or adjust legend_right / legend_floor")

    x_acr, x_name = left + sw + g1, left + sw + g1 + w_acr + g2
    y = top - sw / 2
    for i, (kind, c, acr, name) in enumerate(rows):
        if i == group_break:
            y -= gap
        base = (y - size * 0.36 * px) / FH  # baseline that centers caps on the swatch
        if kind == "region":
            fig.add_artist(Rectangle((left / FW, (y - sw / 2) / FH), sw / FW, sw / FH,
                                     transform=fig.transFigure, fc=to_rgba(c.color, c.wash_alpha),
                                     ec=c.color, lw=lw * 1.15, zorder=6))
            fig.text(x_acr / FW, base, acr, color=c.label_color, va="baseline", zorder=6, **acr_kw)
        elif kind == "band":
            bh = sw * 0.62
            fig.add_artist(Rectangle((left / FW, (y - bh / 2) / FH), sw / FW, bh / FH,
                                     transform=fig.transFigure, fc=to_rgba(c.color, c.wash_alpha),
                                     ec="none", zorder=6))
            fig.add_artist(Line2D([left / FW, (left + sw) / FW], [(y + bh / 2) / FH] * 2,
                                  transform=fig.transFigure, color=c.color, lw=lw * 0.9,
                                  zorder=6, solid_capstyle="butt"))
            fig.text(x_acr / FW, base, acr, color=c.label_color, va="baseline", zorder=6, **acr_kw)
        else:
            fig.add_artist(Line2D([left / FW, (left + sw) / FW], [y / FH] * 2,
                                  transform=fig.transFigure, color=LINE, lw=lw * 1.05,
                                  zorder=6, solid_capstyle="butt"))
            fig.text(x_acr / FW, base, acr, color=LINE, va="baseline", zorder=6, **tlc_kw)
        fig.text(x_name / FW, base, name, color=BODY, va="baseline", zorder=6, **name_kw)
        y -= pitch

    return {"legend_clear": clear, "legend_corner": (float(cx), float(cy))}
