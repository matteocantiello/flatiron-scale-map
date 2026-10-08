"""Page layouts: one dictionary per output format.

Everything here is presentation: page size, margins, type sizes and
label positions. Geometry and colors come from ``data/``.

Units
    size, margins (left, right, bottom, top), ty, sy, fy   inches
    fs (font sizes)                                        points
    legend_right, legend_floor                             points
    labels, ccq_label, tlc_x, ccm_x                        data coordinates
                                                           (log10 m, log10 s)

Keys
    title / foot      draw the title block / footnote
    ty, sy, fy        baselines: title and subtitle from the top, footnote
                      from the bottom. The title block is set flush with the
                      outer edge of the y-axis label.
    names             legend names: "full" (official) or "short"
    legend_right      gap between the legend and the right axis
    legend_floor      extra lift of the legend above the CCM band
    labels            centers of the in-region acronyms
    ccq_label         (x, y) of the right edge of the CCQ label, set outside
                      its small region
    ccq_leader        leader-line gap in decades, or None for no leader
    tlc_x             where the t = L/c label sits along the line
    ccm_x             left edge of the CCM band caption
    lw                base line width in points
"""

from __future__ import annotations

_LABELS = {"CCA": (10.5, 12.5), "CCN": (-3.5, 7.5), "CCB": (-2.2, -7.5), "ICC": (-8.5, -2.5)}

SLIDE = dict(
    name="flatiron_scale_map_16x9",
    description="16:9 presentation slide, full center names",
    size=(16, 9), dpi=200, lw=1.3,
    margins=(1.38, 1.62, 1.44, 1.92),
    fs=dict(title=40, sub=16.5, tick=15, axlabel=16, land=16.5, region=21, legend=14,
            foot=12, ccm=13.5, tlc=19),
    title=True, foot=True, ty=0.78, sy=1.16, fy=0.30,
    names="full", legend_right=22, legend_floor=10,
    labels=_LABELS, ccq_label=(-11.45, -13.0), ccq_leader=0.25,
    tlc_x=22.6, ccm_x=-4.0,
)

WEB = dict(
    name="flatiron_scale_map_3x2",
    description="3:2 for web pages, short legend names",
    size=(9, 6), dpi=340, lw=0.95,
    margins=(0.98, 0.98, 0.98, 1.30),
    fs=dict(title=22, sub=11, tick=10, axlabel=11, land=11, region=13.5, legend=9.8,
            foot=8.2, ccm=9.2, tlc=13),
    title=True, foot=True, ty=0.48, sy=0.72, fy=0.20,
    names="short", legend_right=14, legend_floor=10,
    labels={**_LABELS, "CCN": (-3.5, 7.2)}, ccq_label=(-10.78, -13.0), ccq_leader=None,
    tlc_x=22.4, ccm_x=-4.0,
)

PAPER = dict(
    WEB,
    name="flatiron_scale_map_3x2_notitle",
    description="3:2 for papers: no title or footnote (put them in the caption)",
    margins=(0.98, 0.98, 0.74, 0.70),
    title=False, foot=False,
)

LAYOUTS: dict[str, dict] = {"slide": SLIDE, "web": WEB, "paper": PAPER}
