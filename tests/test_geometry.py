"""Geometry and data checks.

The reference vertices below are the ones the figure was first specified with
(hand-computed with log10 c rounded to 8.48). The code derives them from the
core ranges in data/centers.toml, so these tests pin the data and the clipping
together.
"""

import math

import pytest

from scalemap.data import (LOG10_C, box_polygon, clip_to_causal, load_centers,
                           load_extensions, load_landmarks, polygon_area)

REFERENCE = {
    "CCQ": [(-10.5, -18), (-9.52, -18), (-7.5, -15.98), (-7.5, -11), (-10.5, -11)],
    "ICC": [(-10, -15), (-7, -15), (-7, 4), (-10, 4)],
    "CCB": [(-10, -12), (-3.52, -12), (0, -8.48), (0, 6), (-10, 6)],
    "CCN": [(-6, -3), (-1, -3), (-1, 9), (-6, 9)],
    "CCA": [(4, -3), (5.48, -3), (26.08, 17.6), (4, 17.6)],
}
TOL = 0.01  # decades; covers the 8.48 vs 8.4768 rounding


def _same_polygon(a, b, tol=TOL):
    """Equal as cyclic vertex sequences, starting point free."""
    if len(a) != len(b):
        return False
    n = len(a)
    for shift in range(n):
        if all(math.dist(a[(i + shift) % n], b[i]) <= tol for i in range(n)):
            return True
    return False


@pytest.fixture(scope="module")
def centers():
    return {c.id: c for c in load_centers()}


def test_log10_c():
    assert LOG10_C == pytest.approx(8.4768, abs=1e-4)


@pytest.mark.parametrize("cid", REFERENCE)
def test_regions_match_reference(centers, cid):
    assert _same_polygon(centers[cid].polygon, REFERENCE[cid]), centers[cid].polygon


def test_every_vertex_is_causal(centers):
    for c in centers.values():
        if c.is_region:
            for x, y in c.polygon:
                assert y >= x - LOG10_C - 1e-9, (c.id, x, y)


def test_clip_leaves_causal_box_untouched():
    box = box_polygon((-6, -1), (-3, 9))
    assert clip_to_causal(box) == box


def test_clip_removes_acausal_box():
    assert clip_to_causal(box_polygon((10, 12), (-5, -4))) == []


def test_draw_order_by_area(centers):
    order = [c.id for c in sorted((c for c in centers.values() if c.is_region),
                                  key=lambda c: c.area, reverse=True)]
    assert order == ["CCA", "CCB", "CCN", "ICC", "CCQ"]


def test_area_of_unit_square():
    assert polygon_area(box_polygon((0, 1), (0, 1))) == pytest.approx(1.0)


def test_centers_listed_smallest_first():
    # legend order runs from the smallest systems to the largest
    regions = [c for c in load_centers() if c.is_region]
    assert [c.id for c in regions] == ["CCQ", "ICC", "CCB", "CCN", "CCA"]
    lows = [c.length[0] for c in regions]
    assert lows == sorted(lows)


def test_one_methods_center(centers):
    methods = [c for c in centers.values() if not c.is_region]
    assert [c.id for c in methods] == ["CCM"]
    with pytest.raises(ValueError):
        methods[0].polygon


def test_landmarks_sorted_and_in_window():
    lm = load_landmarks()
    for axis, (lo, hi) in {"length": (-14, 28), "time": (-20, 19)}.items():
        vals = [m.log10 for m in lm[axis]]
        assert vals == sorted(vals), axis
        assert all(lo <= v <= hi for v in vals), axis


def test_extensions_reference_known_centers(centers):
    for e in load_extensions():
        assert e.center in centers
        assert e.polygon, e.label
