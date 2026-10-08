"""Scale map of the Flatiron Institute centers.

Plots each center's characteristic length and time scales on a log–log plane,
clipped at the light-crossing line t = L/c.

    from scalemap import render
    fig, diagnostics = render("slide")
    fig.savefig("map.png", dpi=200)

Data lives in ``data/*.toml``, layouts in ``scalemap.layouts``.
"""

from .data import LOG10_C, Center, clip_to_causal, load_centers, load_extensions, load_landmarks
from .layouts import LAYOUTS
from .plot import render

__all__ = ["LAYOUTS", "LOG10_C", "Center", "clip_to_causal", "load_centers",
           "load_extensions", "load_landmarks", "render"]
__version__ = "1.0.0"
