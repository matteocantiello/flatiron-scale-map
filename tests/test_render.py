"""Smoke tests: every layout renders, its legend stays clear of t = L/c, and
the CCM band's two arms match on the page without touching the CCQ label."""

import pytest

from scalemap import LAYOUTS, render
from scalemap.plot import BAND_TOP, XMIN, YMIN


@pytest.mark.parametrize("name", LAYOUTS)
def test_layout_renders_with_clear_legend(name, tmp_path):
    fig, diag = render(name)
    assert diag["legend_clear"], diag
    fig.savefig(tmp_path / f"{name}.png", dpi=40)
    assert (tmp_path / f"{name}.png").stat().st_size > 0


@pytest.mark.parametrize("name", LAYOUTS)
def test_ccm_band_arms_match_and_clear_ccq_label(name):
    fig, diag = render(name)
    ax = fig.axes[0]
    px = ax.transData.transform
    bottom_arm = px((XMIN, BAND_TOP))[1] - px((XMIN, YMIN))[1]
    left_arm = px((diag["band_right"], YMIN))[0] - px((XMIN, YMIN))[0]
    assert bottom_arm > 0
    assert left_arm == pytest.approx(bottom_arm, rel=1e-6)
    # the CCQ label (white-boxed, left of its region) must not cut into the left arm
    fig.canvas.draw()
    label = next(t for t in ax.texts if t.get_text() == "CCQ")
    box = label.get_bbox_patch().get_window_extent(fig.canvas.get_renderer())
    gap_pt = (box.x0 - px((diag["band_right"], YMIN))[0]) * 72 / fig.dpi
    assert gap_pt > 4, f"{name}: CCQ label is {gap_pt:.1f} pt from the CCM band"


def test_extensions_render(tmp_path):
    fig, _ = render("slide", extensions=True)
    fig.savefig(tmp_path / "ext.pdf")
    assert (tmp_path / "ext.pdf").stat().st_size > 0
