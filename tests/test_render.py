"""Smoke tests: every layout renders and its legend stays clear of t = L/c."""

import pytest

from scalemap import LAYOUTS, render


@pytest.mark.parametrize("name", LAYOUTS)
def test_layout_renders_with_clear_legend(name, tmp_path):
    fig, diag = render(name)
    assert diag["legend_clear"], diag
    fig.savefig(tmp_path / f"{name}.png", dpi=40)
    assert (tmp_path / f"{name}.png").stat().st_size > 0


def test_extensions_render(tmp_path):
    fig, _ = render("slide", extensions=True)
    fig.savefig(tmp_path / "ext.pdf")
    assert (tmp_path / "ext.pdf").stat().st_size > 0
