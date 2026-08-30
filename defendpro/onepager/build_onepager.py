#!/usr/bin/env python3
"""Baut den Einseiter zu einer eigenstaendigen HTML-Datei zusammen.

    python3 onepager/build_onepager.py

Ergebnis: onepager/einseiter.html, Grundlage fuer das PDF.

Platzhalter in src/einseiter.html:

    {{FONT_400}} … {{FONT_800}}   Inter, statische Schnitte, woff2
    {{LOGO}}                      Wortmarke als Maske
    {{EMBLEM}}                    Emblem als Maske

Schriften und Vektoren liegen in ../assets und werden mit Homepage und
Visitenkarte geteilt. Geaendert wird nur dort.

Statische Schnitte, kein Variable Font: Chromium bettet einen Variable
Font nicht ins PDF ein. Begruendung und Messung in card/README.md.
"""

import base64
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "einseiter.html"
ASSETS = ROOT.parent / "assets"
OUT = ROOT / "einseiter.html"

FONTS = {f"FONT_{w}": f"fonts/inter-latin-{w}-normal.woff2" for w in (400, 600, 700, 800)}
VECTORS = {"LOGO": "logo.svg", "EMBLEM": "emblem.svg"}


def read(rel: str) -> bytes:
    path = ASSETS / rel
    if not path.exists():
        raise SystemExit(f"Asset fehlt: {path}")
    return path.read_bytes()


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Quelle fehlt: {SRC}")
    html = SRC.read_text(encoding="utf-8")

    for key, rel in FONTS.items():
        uri = "data:font/woff2;base64," + base64.b64encode(read(rel)).decode("ascii")
        html = html.replace("{{" + key + "}}", uri)

    for key, rel in VECTORS.items():
        # Als Maske hat die Grafik keinen CSS-Kontext, currentColor waere
        # unbestimmt. Fuer die Maske zaehlt ohnehin nur der Alphakanal.
        svg = read(rel).decode("utf-8").replace("currentColor", "#000")
        html = html.replace("{{" + key + "}}", "data:image/svg+xml," + quote(svg, safe="/:=;,()"))

    if "{{" in html:
        rest = sorted({p.split("}}")[0] for p in html.split("{{")[1:]})
        raise SystemExit(f"Platzhalter nicht ersetzt: {rest}")

    OUT.write_text(html, encoding="utf-8")
    print(f"geschrieben: {OUT}")
    print(f"groesse:     {len(html.encode('utf-8')) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
