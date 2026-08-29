#!/usr/bin/env python3
"""Baut die Visitenkarte zu einer eigenstaendigen HTML-Datei zusammen.

    python3 card/build_card.py

Ergebnis: card/karte.html, Grundlage fuer das Druck-PDF.
Schriften als base64, Logo und Emblem als eingebettetes SVG. Kein
externer Request, keine Abhaengigkeiten ausserhalb der Standardbibliothek.

Platzhalter in src/karte.html:

    {{FONT_400}} … {{FONT_800}}   Inter, Latin-Subset, woff2
    {{EMBLEM_SVG}}                Emblem als Pfad, faerbt ueber currentColor
    {{LOGO_SVG}}                  Wortmarke als Pfad, ebenso
"""

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "karte.html"
ASSETS = ROOT / "assets"
OUT = ROOT / "karte.html"

FONTS = {f"FONT_{w}": f"fonts/inter-latin-{w}-normal.woff2" for w in (400, 600, 700, 800)}
SVGS = {"EMBLEM_SVG": "emblem.svg", "LOGO_SVG": "logo.svg"}


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"Quelle fehlt: {SRC}")
    html = SRC.read_text(encoding="utf-8")

    for key, rel in FONTS.items():
        path = ASSETS / rel
        if not path.exists():
            raise SystemExit(f"Schrift fehlt: {path}")
        uri = "data:font/woff2;base64," + base64.b64encode(path.read_bytes()).decode("ascii")
        html = html.replace("{{" + key + "}}", uri)

    for key, rel in SVGS.items():
        path = ASSETS / rel
        if not path.exists():
            raise SystemExit(f"Grafik fehlt: {path}. Zuerst trace_assets.py laufen lassen.")
        # Groesse steuert das CSS, deshalb hier Breite und Hoehe entfernen.
        html = html.replace("{{" + key + "}}", path.read_text(encoding="utf-8").strip())

    if "{{" in html:
        rest = {p.split("}}")[0] for p in html.split("{{")[1:]}
        raise SystemExit(f"Platzhalter nicht ersetzt: {sorted(rest)}")

    OUT.write_text(html, encoding="utf-8")
    print(f"geschrieben: {OUT}")
    print(f"groesse:     {len(html.encode('utf-8')) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
