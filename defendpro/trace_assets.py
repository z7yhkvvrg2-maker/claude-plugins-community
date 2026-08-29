#!/usr/bin/env python3
"""Vektorisiert Wortmarke und Emblem aus den PNG-Quellen.

    python3 trace_assets.py

Die PNG-Fassung reicht fuer Papier nicht. Das Emblem liegt mit 300 px
vor, auf der Visitenkarte waere das rund 170 dpi. Als Pfad ist es
aufloesungsunabhaengig und dient zugleich der Homepage als Maske.

Hinweis zur Polaritaet: potracer fuellt die False-Bereiche der Bitmap.
Die Maske muss deshalb invertiert uebergeben werden, sonst entsteht ein
gefuelltes Rechteck mit ausgestanzter Form.
"""

from PIL import Image
import numpy as np
import pathlib
import potrace

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "assets"
OUT = ROOT / "assets"


def trace(src: str, dst: str, upscale: int = 4) -> None:
    alpha = Image.open(SRC / src).convert("LA").getchannel("A")
    w, h = alpha.size
    # Hochskalieren vor dem Tracen glaettet die Kurven, weil potrace auf
    # einer Bitmap arbeitet und deren Kantenaufloesung uebernimmt.
    big = alpha.resize((w * upscale, h * upscale), Image.LANCZOS)
    bits = np.array(big) <= 128          # invertiert, siehe Docstring
    path = potrace.Bitmap(bits).trace(
        turdsize=8, alphamax=1.0, opticurve=True, opttolerance=0.2)

    u, d = upscale, []
    for curve in path:
        p = curve.start_point
        d.append(f"M{p.x / u:.2f} {p.y / u:.2f}")
        for seg in curve:
            e = seg.end_point
            if seg.is_corner:
                c = seg.c
                d.append(f"L{c.x / u:.2f} {c.y / u:.2f}L{e.x / u:.2f} {e.y / u:.2f}")
            else:
                c1, c2 = seg.c1, seg.c2
                d.append(f"C{c1.x / u:.2f} {c1.y / u:.2f} "
                         f"{c2.x / u:.2f} {c2.y / u:.2f} {e.x / u:.2f} {e.y / u:.2f}")
        d.append("Z")

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
           f'<path fill="currentColor" fill-rule="evenodd" d="{"".join(d)}"/></svg>')
    (OUT / dst).write_text(svg, encoding="utf-8")
    print(f"{dst:12s} {w}x{h}  {len(list(path))} Konturen  {len(svg) / 1024:.1f} KB")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    trace("emblem.png", "emblem.svg")
    trace("logo.png", "logo.svg")
