"""Load the scale-map data and derive region geometry.

All coordinates are base-10 logarithms: ``x = log10(L / m)`` and
``y = log10(t / s)``.

A center's region is its rectangular core range clipped to the causal
half-plane ``t >= L / c``. In log space that half-plane is
``y >= x - LOG10_C``. Systems below that line would change faster than light
can cross them, so no coherent system-scale dynamics sit there.
"""

from __future__ import annotations

import math
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

#: log10 of the speed of light in m/s (8.4768).
LOG10_C = math.log10(299_792_458.0)

#: Default data directory (``<repo>/data``).
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

Point = tuple[float, float]
Box = tuple[tuple[float, float], tuple[float, float]]

_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


# --------------------------------------------------------------------------- geometry


def box_polygon(length: tuple[float, float], time: tuple[float, float]) -> list[Point]:
    """Corners of the box, counter-clockwise from the bottom-left."""
    (x0, x1), (y0, y1) = length, time
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def clip_to_causal(poly: list[Point], log10_c: float = LOG10_C) -> list[Point]:
    """Clip a convex polygon to the half-plane ``y >= x - log10_c``.

    One pass of Sutherland–Hodgman against a single edge. Vertices on the
    line count as inside. Returns an empty list if nothing survives.
    """

    def side(p: Point) -> float:  # >= 0 means inside
        return p[1] - p[0] + log10_c

    out: list[Point] = []
    n = len(poly)
    for i in range(n):
        cur, nxt = poly[i], poly[(i + 1) % n]
        s_cur, s_nxt = side(cur), side(nxt)
        if s_cur >= 0:
            out.append(cur)
        if (s_cur >= 0) != (s_nxt >= 0):
            t = s_cur / (s_cur - s_nxt)
            out.append((cur[0] + t * (nxt[0] - cur[0]), cur[1] + t * (nxt[1] - cur[1])))
    # drop consecutive duplicates created when a vertex sits exactly on the line
    dedup: list[Point] = []
    for p in out:
        if not dedup or math.dist(p, dedup[-1]) > 1e-12:
            dedup.append(p)
    if len(dedup) > 1 and math.dist(dedup[0], dedup[-1]) <= 1e-12:
        dedup.pop()
    return dedup


def polygon_area(poly: list[Point]) -> float:
    """Unsigned area in decade² (shoelace formula)."""
    s = 0.0
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        s += x0 * y1 - x1 * y0
    return abs(s) / 2.0


# --------------------------------------------------------------------------- records


@dataclass(frozen=True)
class Center:
    """One Flatiron center, as read from ``centers.toml``."""

    id: str
    name: str
    short_name: str
    kind: str  # "region" or "methods"
    color: str
    label_color: str
    wash_alpha: float
    url: str
    length: tuple[float, float] | None = None
    time: tuple[float, float] | None = None
    provenance: dict[str, str] = field(default_factory=dict)

    @property
    def is_region(self) -> bool:
        return self.kind == "region"

    @property
    def polygon(self) -> list[Point]:
        """The drawn region: core box clipped to ``t >= L/c``."""
        if not self.is_region:
            raise ValueError(f"{self.id} is a methods center and has no region")
        return clip_to_causal(box_polygon(self.length, self.time))

    @property
    def area(self) -> float:
        return polygon_area(self.polygon) if self.is_region else 0.0


@dataclass(frozen=True)
class Extension:
    """An edge case outside a center's core range (``extensions.toml``)."""

    center: str
    label: str
    length: tuple[float, float]
    time: tuple[float, float]
    note: str = ""

    @property
    def polygon(self) -> list[Point]:
        return clip_to_causal(box_polygon(self.length, self.time))


@dataclass(frozen=True)
class Landmark:
    label: str
    value: float  # SI units

    @property
    def log10(self) -> float:
        return math.log10(self.value)


# --------------------------------------------------------------------------- loaders


def _read(path: Path) -> dict:
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def _range(v, what: str) -> tuple[float, float]:
    lo, hi = (float(x) for x in v)
    if not lo < hi:
        raise ValueError(f"{what}: expected [min, max] with min < max, got {v}")
    return lo, hi


def load_centers(path: Path | str = DATA_DIR / "centers.toml") -> list[Center]:
    """Read and validate ``centers.toml``. Order is preserved (smallest scale first)."""
    raw = _read(Path(path))["center"]
    centers: list[Center] = []
    seen: set[str] = set()
    for c in raw:
        cid = c["id"]
        if cid in seen:
            raise ValueError(f"duplicate center id {cid}")
        seen.add(cid)
        for key in ("color", "label_color"):
            if not _HEX.match(c[key]):
                raise ValueError(f"{cid}.{key}: expected #RRGGBB, got {c[key]!r}")
        if not 0 < c["wash_alpha"] <= 1:
            raise ValueError(f"{cid}.wash_alpha must be in (0, 1]")
        kind = c.get("kind", "region")
        if kind not in ("region", "methods"):
            raise ValueError(f"{cid}.kind must be 'region' or 'methods'")
        length = _range(c["length"], f"{cid}.length") if kind == "region" else None
        time = _range(c["time"], f"{cid}.time") if kind == "region" else None
        prov = {k: c[k] for k in ("smallest", "largest", "fastest", "slowest", "note") if k in c}
        centers.append(Center(id=cid, name=c["name"], short_name=c["short_name"], kind=kind,
                              color=c["color"], label_color=c["label_color"],
                              wash_alpha=float(c["wash_alpha"]), url=c["url"],
                              length=length, time=time, provenance=prov))
        if kind == "region" and not centers[-1].polygon:
            raise ValueError(f"{cid}: core range lies entirely below t = L/c")
    return centers


def load_landmarks(path: Path | str = DATA_DIR / "landmarks.toml") -> dict[str, list[Landmark]]:
    """Read ``landmarks.toml`` into ``{"length": [...], "time": [...]}``."""
    raw = _read(Path(path))
    return {axis: [Landmark(d["label"], float(d["value"])) for d in raw.get(axis, [])]
            for axis in ("length", "time")}


def load_extensions(path: Path | str = DATA_DIR / "extensions.toml") -> list[Extension]:
    """Read ``extensions.toml`` (edge cases, not drawn by default)."""
    raw = _read(Path(path)).get("extension", [])
    return [Extension(center=e["center"], label=e["label"],
                      length=_range(e["length"], e["label"]), time=_range(e["time"], e["label"]),
                      note=e.get("note", "")) for e in raw]
