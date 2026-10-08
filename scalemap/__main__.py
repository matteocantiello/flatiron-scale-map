"""Command-line entry point.

    python -m scalemap                  # all layouts, PNG + PDF, into figures/
    python -m scalemap slide            # one layout
    python -m scalemap web paper -f pdf # several layouts, PDF only
    python -m scalemap slide --with-extensions --outdir /tmp
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .layouts import LAYOUTS
from .plot import BG, render

REPO = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m scalemap",
                                description="Render the Flatiron Institute scale map.")
    p.add_argument("layouts", nargs="*", metavar="LAYOUT",
                   help=f"one or more of {', '.join(LAYOUTS)} or all (default: all)")
    p.add_argument("-o", "--outdir", type=Path, default=REPO / "figures",
                   help="output directory (default: figures/)")
    p.add_argument("-f", "--formats", nargs="+", default=["png", "pdf"],
                   choices=["png", "pdf", "svg"], help="output formats (default: png pdf)")
    p.add_argument("--with-extensions", action="store_true",
                   help="also draw the edge cases in data/extensions.toml (dashed)")
    args = p.parse_args(argv)

    unknown = set(args.layouts) - {*LAYOUTS, "all"}
    if unknown:
        p.error(f"unknown layout(s): {', '.join(sorted(unknown))}")
    names = list(LAYOUTS) if not args.layouts or "all" in args.layouts else args.layouts
    args.outdir.mkdir(parents=True, exist_ok=True)
    for name in names:
        cfg = LAYOUTS[name]
        fig, diag = render(cfg, extensions=args.with_extensions)
        stem = cfg["name"] + ("_extensions" if args.with_extensions else "")
        for fmt in args.formats:
            out = args.outdir / f"{stem}.{fmt}"
            fig.savefig(out, dpi=cfg["dpi"], facecolor=BG)
            print(f"wrote {out}")
        if not diag["legend_clear"]:
            print(f"  warning: legend overlaps the t = L/c line in '{name}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
